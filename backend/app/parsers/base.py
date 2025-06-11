import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.parser import ParserConfig, ParserLog

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Базовый класс для всех парсеров"""
    
    def __init__(self, config: ParserConfig, db_session: Session):
        self.config = config
        self.db = db_session
        self.log_data = []
        self.errors_count = 0
        self.records_processed = 0
        self.start_time = None
        self.parser_log = None
        
    @abstractmethod
    async def parse(self) -> Dict[str, Any]:
        """Основной метод парсинга - должен быть реализован в наследниках"""
        pass
    
    @abstractmethod
    async def save_to_db(self, data: Any) -> None:
        """Сохранение данных в БД - должен быть реализован в наследниках"""
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """Логирование с сохранением в список"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_data.append(log_entry)
        
        if level == "ERROR":
            logger.error(message)
            self.errors_count += 1
        else:
            logger.info(message)
    
    async def run(self) -> bool:
        """Запуск парсера с логированием"""
        self.start_time = datetime.now()
        
        # Создаем запись в логах
        self.parser_log = ParserLog(
            parser_config_id=self.config.id,
            started_at=self.start_time,
            status="running"
        )
        self.db.add(self.parser_log)
        self.db.commit()
        
        try:
            self.log(f"Starting parser: {self.config.name}")
            
            # Запускаем парсинг
            data = await self.parse()
            
            # Сохраняем в БД
            await self.save_to_db(data)
            
            # Обновляем статус
            self.parser_log.finished_at = datetime.now()
            self.parser_log.status = "success"
            self.parser_log.records_processed = self.records_processed
            self.parser_log.errors_count = self.errors_count
            self.parser_log.log_data = "\n".join(self.log_data)
            
            # Обновляем конфигурацию парсера
            self.config.last_run = datetime.now()
            self.config.last_status = "success"
            
            self.db.commit()
            self.log(f"Parser completed successfully. Processed: {self.records_processed} records")
            return True
            
        except Exception as e:
            self.log(f"Parser failed: {str(e)}", "ERROR")
            
            # Обновляем статус при ошибке
            if self.parser_log:
                self.parser_log.finished_at = datetime.now()
                self.parser_log.status = "failed"
                self.parser_log.errors_count = self.errors_count
                self.parser_log.log_data = "\n".join(self.log_data)
            
            self.config.last_run = datetime.now()
            self.config.last_status = "failed"
            
            self.db.commit()
            return False


class LegacyParserAdapter(BaseParser):
    """Адаптер для интеграции существующих парсеров"""
    
    def __init__(self, config: ParserConfig, db_session: Session, legacy_parser_module: str):
        super().__init__(config, db_session)
        self.legacy_parser_module = legacy_parser_module
        
    async def parse(self) -> Dict[str, Any]:
        """Запуск legacy парсера в отдельном процессе"""
        import subprocess
        import os
        
        try:
            # Устанавливаем переменные окружения
            env = os.environ.copy()
            env['SIMPLE_SETTINGS'] = 'settings.general'
            
            # Запускаем парсер
            result = subprocess.run(
                ['python', self.legacy_parser_module],
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode != 0:
                self.log(f"Parser error: {result.stderr}", "ERROR")
                raise Exception(f"Parser failed with code {result.returncode}")
                
            self.log("Legacy parser completed")
            
            # Возвращаем путь к CSV файлу
            return {"csv_file": self.config.config.get("result_file")}
            
        except Exception as e:
            self.log(f"Failed to run legacy parser: {str(e)}", "ERROR")
            raise
    
    async def save_to_db(self, data: Any) -> None:
        """Импорт данных из CSV в БД"""
        csv_file = data.get("csv_file")
        if not csv_file:
            return
            
        # Здесь будет логика импорта CSV в БД
        # Это зависит от конкретного парсера
        self.log(f"CSV file created: {csv_file}")
        self.log("Import to DB will be implemented based on parser type")

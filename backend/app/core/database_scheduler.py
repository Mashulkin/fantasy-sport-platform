import logging
from datetime import datetime
from celery.beat import ScheduleEntry, Scheduler
from celery.schedules import crontab
from app.core.database import SessionLocal
from app.models.parser import ParserConfig

logger = logging.getLogger(__name__)


class DatabaseScheduler(Scheduler):
    """
    Планировщик, который автоматически загружает расписания из БД
    каждые 60 секунд с быстрой проверкой изменений
    """
    
    def __init__(self, *args, **kwargs):
        self.last_db_update = 0
        self.last_db_check = 0
        super().__init__(*args, **kwargs)
        
    def setup_schedule(self):
        """Начальная настройка планировщика"""
        logger.info("🚀 Setting up DatabaseScheduler...")
        
        # Загружаем базовые системные задачи
        self.merge_inplace(self.app.conf.beat_schedule)
        self.install_default_entries(self.app.conf.beat_schedule)
        
        # Сразу загружаем парсеры из БД
        self.update_from_database()
        
        # Устанавливаем короткий интервал для частых проверок БД
        self.max_interval = 30  # Проверяем каждые 30 секунд
        
    def validate_and_fix_cron(self, schedule_str):
        """Проверяет и исправляет cron выражение"""
        if not schedule_str:
            return None, "Empty schedule"
        
        try:
            # Убираем лишние пробелы и разбиваем
            parts = schedule_str.strip().split()
            
            # Удаляем пустые части
            parts = [part for part in parts if part]
            
            # Проверяем количество частей
            if len(parts) < 5:
                while len(parts) < 5:
                    parts.append('*')
            elif len(parts) > 5:
                parts = parts[:5]
            
            # Убираем лишние символы
            clean_parts = []
            for part in parts:
                clean_part = part.replace('**', '*').replace('***', '*')
                clean_parts.append(clean_part)
            
            # Тестируем создание crontab
            test_cron = crontab(
                minute=clean_parts[0],
                hour=clean_parts[1],
                day_of_month=clean_parts[2],
                month_of_year=clean_parts[3],
                day_of_week=clean_parts[4]
            )
            
            fixed_schedule = ' '.join(clean_parts)
            return fixed_schedule, None
            
        except Exception as e:
            return None, f"Invalid cron expression: {e}"
    
    def update_from_database(self):
        """Загружает/обновляет расписания парсеров из БД"""
        try:
            db = SessionLocal()
            
            # Получаем все активные парсеры с расписанием
            parsers = db.query(ParserConfig).filter(
                ParserConfig.is_active == True,
                ParserConfig.schedule.isnot(None)
            ).all()
            
            logger.info(f"📋 Found {len(parsers)} active parsers in database")
            
            # Получаем текущие ID активных парсеров
            current_parser_ids = set(parser.id for parser in parsers)
            
            # Удаляем расписания для парсеров, которые больше не активны
            old_parser_schedules = [name for name in self.schedule.keys() if name.startswith('parser_')]
            removed_count = 0
            
            for schedule_name in old_parser_schedules:
                # Извлекаем ID парсера из имени расписания (parser_1 -> 1)
                try:
                    parser_id = int(schedule_name.split('_')[1])
                    if parser_id not in current_parser_ids:
                        del self.schedule[schedule_name]
                        removed_count += 1
                        logger.info(f"🗑️ Removed schedule for inactive parser: {schedule_name}")
                except (IndexError, ValueError):
                    # Если не можем извлечь ID, удаляем для безопасности
                    del self.schedule[schedule_name]
                    removed_count += 1
                    logger.warning(f"🗑️ Removed malformed schedule: {schedule_name}")
            
            if removed_count > 0:
                logger.info(f"🧹 Removed {removed_count} inactive parser schedules")
            
            # Добавляем/обновляем расписания для активных парсеров
            added_count = 0
            updated_count = 0
            error_count = 0
            
            for parser in parsers:
                if parser.schedule:
                    # Проверяем и исправляем cron выражение
                    fixed_schedule, error = self.validate_and_fix_cron(parser.schedule)
                    
                    if error:
                        logger.error(f"❌ Parser {parser.name} has invalid schedule '{parser.schedule}': {error}")
                        error_count += 1
                        continue
                    
                    try:
                        # Разбиваем исправленное расписание
                        parts = fixed_schedule.split()
                        
                        schedule_name = f"parser_{parser.id}"
                        
                        # Проверяем, существует ли уже такое расписание
                        is_update = schedule_name in self.schedule
                        
                        # Создаем ScheduleEntry
                        entry = ScheduleEntry(
                            name=schedule_name,
                            task='run_parser',
                            schedule=crontab(
                                minute=parts[0],
                                hour=parts[1],
                                day_of_month=parts[2],
                                month_of_year=parts[3],
                                day_of_week=parts[4]
                            ),
                            args=(parser.id,),
                            kwargs={},
                            options={'expires': 3600},
                            app=self.app
                        )
                        
                        self.schedule[schedule_name] = entry
                        
                        if is_update:
                            updated_count += 1
                            logger.info(f"🔄 Updated schedule: {parser.name} ({schedule_name}) - {fixed_schedule}")
                        else:
                            added_count += 1
                            logger.info(f"➕ Added schedule: {parser.name} ({schedule_name}) - {fixed_schedule}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error creating schedule for {parser.name}: {e}")
                        error_count += 1
            
            db.close()
            
            total_schedules = len(self.schedule)
            parser_schedules = len([k for k in self.schedule.keys() if k.startswith('parser_')])
            
            if error_count > 0:
                logger.warning(f"⚠️ Database update complete: {added_count} added, {updated_count} updated, {removed_count} removed, {error_count} errors. Total: {parser_schedules} parsers, {total_schedules} schedules")
            else:
                logger.info(f"✅ Database update complete: {added_count} added, {updated_count} updated, {removed_count} removed. Total: {parser_schedules} parsers, {total_schedules} schedules")
            
        except Exception as e:
            logger.error(f"💥 Error updating from database: {e}")
    
    def tick(self):
        """
        Переопределяем tick для автоматического обновления из БД
        """
        import time
        current_time = time.time()
        
        # Обновляем из БД каждые 90 секунд (более частое обновление)
        if current_time - self.last_db_update > 90:  # 1.5 минуты = 90 секунд
            logger.info("🔄 Periodic database update...")
            self.update_from_database()
            self.last_db_update = current_time
        
        # Вызываем родительский tick
        return super().tick()
    
    @property
    def schedule(self):
        """Возвращает текущее расписание"""
        return self.data
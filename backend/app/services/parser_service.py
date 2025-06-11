from typing import Dict, Type, Optional
from sqlalchemy.orm import Session
from app.models.parser import ParserConfig
from app.parsers.base import BaseParser
from app.parsers.fpl.players import FPLPlayersParser, FPLOwnershipParser

# Регистр всех доступных парсеров
PARSER_REGISTRY: Dict[str, Type[BaseParser]] = {
    "fpl_players": FPLPlayersParser,
    "fpl_ownership": FPLOwnershipParser,
    # Добавьте сюда другие парсеры по мере создания
    # "fanton_tournament": FantonTournamentParser,
}


class ParserService:
    """Сервис для управления парсерами"""
    
    @staticmethod
    def get_parser(parser_config: ParserConfig, db: Session) -> Optional[BaseParser]:
        """Получить экземпляр парсера по конфигурации"""
        parser_type = parser_config.parser_type
        
        parser_class = PARSER_REGISTRY.get(parser_type)
        if not parser_class:
            raise ValueError(f"Unknown parser type: {parser_type}")
            
        return parser_class(parser_config, db)
    
    @staticmethod
    async def run_parser(parser_config_id: int, db: Session) -> bool:
        """Запустить парсер по ID конфигурации"""
        parser_config = db.query(ParserConfig).get(parser_config_id)
        if not parser_config:
            raise ValueError(f"Parser config not found: {parser_config_id}")
            
        if not parser_config.is_active:
            raise ValueError(f"Parser is not active: {parser_config.name}")
            
        parser = ParserService.get_parser(parser_config, db)
        return await parser.run()
    
    @staticmethod
    def register_parser(parser_type: str, parser_class: Type[BaseParser]):
        """Зарегистрировать новый парсер"""
        PARSER_REGISTRY[parser_type] = parser_class

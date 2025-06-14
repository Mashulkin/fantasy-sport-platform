"""
Parser service for managing and executing data parsers.

Provides a registry system for parser classes and orchestrates
parser execution with proper error handling and logging.
"""

from typing import Dict, Type, Optional
from sqlalchemy.orm import Session
from app.models.parser import ParserConfig
from app.parsers.base import BaseParser
from app.parsers.fpl.players import FPLPlayersParser, FPLOwnershipParser

# Registry of all available parser implementations
PARSER_REGISTRY: Dict[str, Type[BaseParser]] = {
    "fpl_players": FPLPlayersParser,
    "fpl_ownership": FPLOwnershipParser,
    # Additional parsers can be registered here as they are implemented
    # "fanteam_tournament": FanteamTournamentParser,
    # "sorare_cards": SorareCardsParser,
}


class ParserService:
    """
    Service class for parser management and execution.
    
    Provides methods to instantiate parsers, execute them,
    and manage the parser registry system.
    """
    
    @staticmethod
    def get_parser(parser_config: ParserConfig, db: Session) -> Optional[BaseParser]:
        """
        Create parser instance from configuration.
        
        Looks up the parser class in the registry and instantiates it
        with the provided configuration and database session.
        
        Args:
            parser_config: Parser configuration from database
            db: Database session for parser operations
            
        Returns:
            BaseParser: Instantiated parser ready for execution
            
        Raises:
            ValueError: If parser type is not registered
        """
        parser_type = parser_config.parser_type
        
        parser_class = PARSER_REGISTRY.get(parser_type)
        if not parser_class:
            raise ValueError(f"Unknown parser type: {parser_type}")
            
        return parser_class(parser_config, db)
    
    @staticmethod
    async def run_parser(parser_config_id: int, db: Session) -> bool:
        """
        Execute parser by configuration ID.
        
        Loads the parser configuration, instantiates the appropriate
        parser class, and executes it with full error handling.
        
        Args:
            parser_config_id: Database ID of parser configuration
            db: Database session for operations
            
        Returns:
            bool: True if parser executed successfully, False otherwise
            
        Raises:
            ValueError: If parser config not found or inactive
        """
        # Load parser configuration
        parser_config = db.query(ParserConfig).get(parser_config_id)
        if not parser_config:
            raise ValueError(f"Parser config not found: {parser_config_id}")
            
        if not parser_config.is_active:
            raise ValueError(f"Parser is not active: {parser_config.name}")
            
        # Instantiate and execute parser
        parser = ParserService.get_parser(parser_config, db)
        return await parser.run()
    
    @staticmethod
    def register_parser(parser_type: str, parser_class: Type[BaseParser]):
        """
        Register new parser type in the global registry.
        
        Allows dynamic registration of parser implementations
        for use in the system.
        
        Args:
            parser_type: Unique identifier for the parser type
            parser_class: Parser class implementing BaseParser interface
        """
        PARSER_REGISTRY[parser_type] = parser_class

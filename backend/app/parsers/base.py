"""
Base parser classes for data extraction and processing.

This module provides abstract base classes and utilities for implementing
parsers that fetch data from external APIs and save it to the database.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.parser import ParserConfig, ParserLog

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract base class for all data parsers.
    
    Provides common functionality for logging, error handling,
    and database operations. Subclasses must implement parse()
    and save_to_db() methods.
    """
    
    def __init__(self, config: ParserConfig, db_session: Session):
        """
        Initialize parser with configuration and database session.
        
        Args:
            config (ParserConfig): Parser configuration from database
            db_session (Session): SQLAlchemy database session
        """
        self.config = config
        self.db = db_session
        self.log_data = []
        self.errors_count = 0
        self.records_processed = 0
        self.start_time = None
        self.parser_log = None
        
    @abstractmethod
    async def parse(self) -> Dict[str, Any]:
        """
        Fetch and parse data from external source.
        
        This method must be implemented by subclasses to define
        the specific data fetching logic.
        
        Returns:
            Dict[str, Any]: Parsed data to be saved to database
        """
        pass
    
    @abstractmethod
    async def save_to_db(self, data: Any) -> None:
        """
        Save parsed data to database.
        
        This method must be implemented by subclasses to define
        how the parsed data should be stored.
        
        Args:
            data: Parsed data from parse() method
        """
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log message with timestamp and update error counter.
        
        Args:
            message (str): Log message
            level (str): Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_data.append(log_entry)
        
        if level == "ERROR":
            logger.error(message)
            self.errors_count += 1
        else:
            logger.info(message)
    
    async def run(self) -> bool:
        """
        Execute the complete parsing workflow.
        
        Handles initialization, parsing, saving, and cleanup
        with comprehensive error handling and logging.
        
        Returns:
            bool: True if parsing completed successfully, False otherwise
        """
        self.start_time = datetime.now()
        
        # Create initial log entry
        self.parser_log = ParserLog(
            parser_config_id=self.config.id,
            started_at=self.start_time,
            status="running"
        )
        self.db.add(self.parser_log)
        self.db.commit()
        
        try:
            self.log(f"Starting parser: {self.config.name}")
            
            # Execute parsing workflow
            data = await self.parse()
            await self.save_to_db(data)
            
            # Update success status
            self._update_success_status()
            
            self.log(
                f"Parser completed successfully. "
                f"Processed: {self.records_processed} records"
            )
            return True
            
        except Exception as e:
            self.log(f"Parser failed: {str(e)}", "ERROR")
            self._update_failure_status()
            return False
    
    def _update_success_status(self):
        """Update parser log and config with successful completion status."""
        self.parser_log.finished_at = datetime.now()
        self.parser_log.status = "success"
        self.parser_log.records_processed = self.records_processed
        self.parser_log.errors_count = self.errors_count
        self.parser_log.log_data = "\n".join(self.log_data)
        
        self.config.last_run = datetime.now()
        self.config.last_status = "success"
        
        self.db.commit()
    
    def _update_failure_status(self):
        """Update parser log and config with failure status."""
        if self.parser_log:
            self.parser_log.finished_at = datetime.now()
            self.parser_log.status = "failed"
            self.parser_log.errors_count = self.errors_count
            self.parser_log.log_data = "\n".join(self.log_data)
        
        self.config.last_run = datetime.now()
        self.config.last_status = "failed"
        
        self.db.commit()


class LegacyParserAdapter(BaseParser):
    """
    Adapter for integrating existing legacy parsers.
    
    This class allows running legacy command-line parsers
    as background tasks within the new parser framework.
    """
    
    def __init__(self, config: ParserConfig, db_session: Session, legacy_parser_module: str):
        """
        Initialize legacy parser adapter.
        
        Args:
            config (ParserConfig): Parser configuration
            db_session (Session): Database session
            legacy_parser_module (str): Path to legacy parser module
        """
        super().__init__(config, db_session)
        self.legacy_parser_module = legacy_parser_module
        
    async def parse(self) -> Dict[str, Any]:
        """
        Execute legacy parser in subprocess.
        
        Returns:
            Dict[str, Any]: Result containing CSV file path
        """
        import subprocess
        import os
        
        try:
            # Set up environment for legacy parser
            env = os.environ.copy()
            env['SIMPLE_SETTINGS'] = 'settings.general'
            
            # Execute legacy parser as subprocess
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
            
            # Return path to generated CSV file
            return {"csv_file": self.config.config.get("result_file")}
            
        except Exception as e:
            self.log(f"Failed to run legacy parser: {str(e)}", "ERROR")
            raise
    
    async def save_to_db(self, data: Any) -> None:
        """
        Import CSV data to database.
        
        Args:
            data: Dictionary containing csv_file path
        """
        csv_file = data.get("csv_file")
        if not csv_file:
            return
            
        # CSV import logic would be implemented based on parser type
        self.log(f"CSV file created: {csv_file}")
        self.log("Import to DB will be implemented based on parser type")

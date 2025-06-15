"""
Alembic migration environment configuration.

This module configures the Alembic migration environment for database schema
management. It sets up the database connection, imports all models for 
autogenerate support, and defines migration execution functions.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add project root to Python path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.database import Base

# Import all models to ensure they are registered with SQLAlchemy metadata
# This is crucial for autogenerate functionality to detect schema changes
from app.models.user import User
from app.models.team import Team
from app.models.player import Player, PlayerPlatformProfile
from app.models.stats import PlayerStats, PriceHistory
from app.models.tournament import Tournament, TournamentParticipant
from app.models.parser import ParserConfig, ParserLog
from app.models.odds import MatchOdds

# Alembic Config object with access to .ini file values
config = context.config

# Override database URL from application settings
# This ensures migrations use the same database as the application
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configure Python logging from alembic.ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
# This enables Alembic to compare current schema with model definitions
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context. This is the standard way to run migrations against
    a live database.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Use NullPool to avoid connection pool issues
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Execute appropriate migration mode based on Alembic context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

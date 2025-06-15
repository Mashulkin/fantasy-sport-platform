"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Revision identifiers, used by Alembic for migration tracking
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    Apply database schema changes for this migration.
    
    This function contains the forward migration logic - operations that
    will be executed when running 'alembic upgrade'. Add your schema
    changes here (create tables, add columns, create indexes, etc.).
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Reverse database schema changes for this migration.
    
    This function contains the rollback logic - operations that will
    undo the changes made in upgrade(). This allows for safe rollbacks
    using 'alembic downgrade'. Always ensure downgrade operations
    properly reverse the upgrade changes.
    """
    ${downgrades if downgrades else "pass"}

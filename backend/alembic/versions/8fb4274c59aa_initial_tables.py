"""initial tables

Revision ID: 8fb4274c59aa
Revises: 475db3b24576
Create Date: 2026-03-11 15:38:56.957610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fb4274c59aa'
down_revision: Union[str, Sequence[str], None] = '475db3b24576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

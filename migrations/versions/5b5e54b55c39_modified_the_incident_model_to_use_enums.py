"""Modified the incident model to use enums

Revision ID: 5b5e54b55c39
Revises: 48b9434cfd73
Create Date: 2025-09-10 19:14:50.346621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b5e54b55c39'
down_revision: Union[str, Sequence[str], None] = '48b9434cfd73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

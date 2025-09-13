"""Added a followups field

Revision ID: b85dd751ca83
Revises: d8e5d9a41450
Create Date: 2025-09-11 10:21:38.494236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b85dd751ca83'
down_revision: Union[str, Sequence[str], None] = 'd8e5d9a41450'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

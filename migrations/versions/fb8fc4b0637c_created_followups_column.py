"""Created followups column

Revision ID: fb8fc4b0637c
Revises: b85dd751ca83
Create Date: 2025-09-11 10:29:13.078334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb8fc4b0637c'
down_revision: Union[str, Sequence[str], None] = 'b85dd751ca83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

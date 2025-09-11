"""Made enums non-native

Revision ID: 91712af1b5b1
Revises: 5b5e54b55c39
Create Date: 2025-09-10 19:20:24.905907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91712af1b5b1'
down_revision: Union[str, Sequence[str], None] = '5b5e54b55c39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""removed extraneous field

Revision ID: d8e5d9a41450
Revises: 91712af1b5b1
Create Date: 2025-09-10 19:33:39.069089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8e5d9a41450'
down_revision: Union[str, Sequence[str], None] = '91712af1b5b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

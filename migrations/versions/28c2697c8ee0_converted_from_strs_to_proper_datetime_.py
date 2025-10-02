"""Converted from strs to proper datetime types

Revision ID: 28c2697c8ee0
Revises: 1ae7f5eb1e4e
Create Date: 2025-09-29 13:41:02.255371
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "28c2697c8ee0"
down_revision: Union[str, Sequence[str], None] = "1ae7f5eb1e4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # (Optional) fail fast on lock/contention instead of hanging
    op.execute("SET LOCAL lock_timeout = '5s'; SET LOCAL statement_timeout = '1min';")

    # Drop any empty-string defaults that could interfere
    op.alter_column("incidents", "date_of_incident", server_default=None, existing_type=sa.VARCHAR())
    op.alter_column("incidents", "time_of_incident", server_default=None, existing_type=sa.VARCHAR())

    # Normalize blanks to NULL so casts don't fail
    op.execute("""
        UPDATE incidents
        SET date_of_incident = NULL
        WHERE date_of_incident IS NOT NULL AND btrim(date_of_incident) = '';
    """)
    op.execute("""
        UPDATE incidents
        SET time_of_incident = NULL
        WHERE time_of_incident IS NOT NULL AND btrim(time_of_incident) = '';
    """)

    # Convert TEXT/VARCHAR -> DATE (MM/DD/YYYY)
    op.alter_column(
        "incidents",
        "date_of_incident",
        existing_type=sa.VARCHAR(),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="to_date(date_of_incident, 'MM/DD/YYYY')",
    )

    # Convert TEXT/VARCHAR -> TIME ('03:25pm', '3:25PM', etc.)
    # Postgres can cast these directly to TIME:
    op.alter_column(
        "incidents",
        "time_of_incident",
        existing_type=sa.VARCHAR(),
        type_=sa.Time(),
        existing_nullable=True,
        postgresql_using="time_of_incident::time",
        # If you prefer explicit parsing, use:
        # postgresql_using="to_timestamp(time_of_incident, 'HH12:MIAM')::time"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "incidents",
        "time_of_incident",
        existing_type=sa.Time(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="time_of_incident::text",
    )
    op.alter_column(
        "incidents",
        "date_of_incident",
        existing_type=sa.Date(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="date_of_incident::text",
    )

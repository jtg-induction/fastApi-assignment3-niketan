"""add_fk_to_restaurant

Revision ID: 44976245f1ca
Revises: 400593562983
Create Date: 2026-10-31 15:50:18.599620

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44976245f1ca"
down_revision: str | Sequence[str] | None = "400593562983"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

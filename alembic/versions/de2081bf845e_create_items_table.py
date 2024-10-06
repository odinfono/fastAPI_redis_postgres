"""create items table

Revision ID: de2081bf845e
Revises: 7881b27aa5ee
Create Date: 2024-10-05 21:32:17.603331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de2081bf845e'
down_revision: Union[str, None] = '7881b27aa5ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

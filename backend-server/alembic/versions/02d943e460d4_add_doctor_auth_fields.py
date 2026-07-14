"""add doctor auth fields

Revision ID: 02d943e460d4
Revises: 7f2fa296ed56
Create Date: 2026-07-11 22:26:17.396108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02d943e460d4'
down_revision: Union[str, None] = '7f2fa296ed56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('doctors') as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('hashed_password', sa.String(length=255), nullable=True))
        batch_op.create_unique_constraint('uq_doctors_email', ['email'])


def downgrade() -> None:
    with op.batch_alter_table('doctors') as batch_op:
        batch_op.drop_constraint('uq_doctors_email', type_='unique')
        batch_op.drop_column('hashed_password')
        batch_op.drop_column('email')

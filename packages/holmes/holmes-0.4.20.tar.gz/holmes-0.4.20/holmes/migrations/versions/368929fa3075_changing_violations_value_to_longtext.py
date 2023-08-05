"""changing violations value to Longtext

Revision ID: 368929fa3075
Revises: 54ca0bd9bc1e
Create Date: 2014-01-10 14:01:54.876125

"""

# revision identifiers, used by Alembic.
revision = '368929fa3075'
down_revision = '54ca0bd9bc1e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('violations', 'value', type_=sa.Text(4294967295), nullable=False)


def downgrade():
    op.alter_column('violations', 'value', type_=sa.Text, nullable=False)

"""add direct_created

Revision ID: ee84bfaad706
Revises: c723db9f0aae
Create Date: 2018-07-11 11:22:39.439198

"""

# revision identifiers, used by Alembic.
revision = 'ee84bfaad706'
down_revision = 'c723db9f0aae'

from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    # sqlite doesn't have ALTER command
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("records") as batch_op:
            batch_op.add_column(sa.Column('direct_created', sa.TIMESTAMP))
    else:
        op.add_column('records', sa.Column('direct_created', sa.TIMESTAMP))


def downgrade():
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("records") as batch_op:
            batch_op.drop_column('direct_created')
    else:
        op.drop_column('records', 'direct_created')


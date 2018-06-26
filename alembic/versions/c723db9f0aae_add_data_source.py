"""add data source

Revision ID: c723db9f0aae
Revises: 43dc6621db1c
Create Date: 2018-06-19 09:20:58.006482

"""

# revision identifiers, used by Alembic.
revision = 'c723db9f0aae'
down_revision = '43dc6621db1c'

from alembic import op
import sqlalchemy as sa

# new origin field holds 'classic' or 'direct'
# other values may eventually be useful
# it records where the data is from, used to compute what bibcodes to delete

def upgrade():
    # sqlite doesn't have ALTER command
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("records") as batch_op:
            batch_op.add_column(sa.Column('origin', sa.Text), nullable=False, server_default='classic')
    else:
        op.add_column('records', sa.Column('origin', sa.Text, nullable=False, server_default='classic'))
            

def downgrade():
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("records") as batch_op:
            batch_op.drop_column('origin')
    else:
        op.drop_column('records', 'origin')
            


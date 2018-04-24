"""fix column name for changelog

Revision ID: d259a9bca9e7
Revises: 264537860322
Create Date: 2017-12-11 16:14:53.373524

"""

# revision identifiers, used by Alembic.
revision = 'd259a9bca9e7'
down_revision = '264537860322'

from alembic import op
import sqlalchemy as sa

                               


from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("change_log") as batch_op:
            batch_op.alter_column('oldvalue', new_column_name='newvalue')
            batch_op.add_column('change_log', sa.Column('oldvalue', sa.Text))
    else:
        op.alter_column('change_log', 'oldvalue', new_column_name='newvalue')
        op.add_column('change_log', sa.Column('oldvalue', sa.Text))


def downgrade():
    cx = op.get_context()
    with op.batch_alter_table("change_log") as batch_op:
        batch_op.drop_column('oldvalue')
        batch_op.alter_column('newvalue', new_column_name='oldvalue')
        

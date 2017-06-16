"""fix column name typo

Revision ID: 264537860322
Revises: b13b7dbc4ddf
Create Date: 2017-06-14 14:39:11.542474

"""

# revision identifiers, used by Alembic.
revision = '264537860322'
down_revision = 'b13b7dbc4ddf'

from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("records") as batch_op:
            batch_op.alter_column('fingerprints', new_column_name='fingerprint')
    else:
        op.alter_column('records', 'fingerprints', new_column_name='fingerprint')


def downgrade():
    cx = op.get_context()
    if 'sqlite' in cx.connection.engine.name:
        with op.batch_alter_table("records") as batch_op:
            batch_op.alter_column('fingerprint', new_column_name='fingerprints')
    else:
        op.alter_column('records', 'fingerprint', new_column_name='fingerprints')    

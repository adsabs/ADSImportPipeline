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
    #with app.app_context() as c:
    #   db.session.add(Model())
    #   db.session.commit()
    op.alter_column('records', 'fingerprints', new_column_name='fingerprint')


def downgrade():
    op.alter_column('records', 'fingerprint', new_column_name='fingerprints')    

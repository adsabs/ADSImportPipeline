"""store only biblio data

Revision ID: b13b7dbc4ddf
Revises: 4475ef3e98ag
Create Date: 2017-06-08 18:12:38.140846

"""

# revision identifiers, used by Alembic.
revision = 'b13b7dbc4ddf'
down_revision = '4475ef3e98ag'

from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    #with app.app_context() as c:
    #   db.session.add(Model())
    #   db.session.commit()
        
    op.add_column('records', sa.Column('fingerprints', sa.Text))
    
    op.drop_column('records', 'meta_data')
    op.drop_column('records', 'orcid_claims')
    op.drop_column('records', 'nonbib_data')
    op.drop_column('records', 'fulltext')
    
    op.drop_column('records', 'meta_data_updated')
    op.drop_column('records', 'orcid_claims_updated')
    op.drop_column('records', 'nonbib_data_updated')
    op.drop_column('records', 'fulltext_updated')


def downgrade():
    op.drop_column('records', 'fingerprints')
    
    op.add_column('records', sa.Column('meta_data', sa.Text))
    op.add_column('records', sa.Column('orcid_claims', sa.Text))
    op.add_column('records', sa.Column('nonbib_data', sa.Text))
    op.add_column('records', sa.Column('fulltext', sa.Text))
    
    op.add_column('records', sa.Column('meta_data_updated', sa.TIMESTAMP))
    op.add_column('records', sa.Column('orcid_claims_updated', sa.TIMESTAMP))
    op.add_column('records', sa.Column('nonbib_data_updated', sa.TIMESTAMP))
    op.add_column('records', sa.Column('fulltext_updated', sa.TIMESTAMP))

"""Added direct ingest pipeline

Revision ID: 43dc6621db1c
Revises: d259a9bca9e7
Create Date: 2018-04-20 16:00:14.894938

"""

# revision identifiers, used by Alembic.
revision = '43dc6621db1c'
down_revision = 'd259a9bca9e7'

from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    cx = op.get_context()
    
    with op.batch_alter_table("records") as batch_op:
        batch_op.add_column(sa.Column('arxiv_data', sa.Text))
        batch_op.add_column(sa.Column('arxiv_updated', sa.TIMESTAMP))
        batch_op.add_column(sa.Column('arxiv_processed', sa.TIMESTAMP))
            

def downgrade():
    cx = op.get_context()
    with op.batch_alter_table("records") as batch_op:
        batch_op.drop_column('arxiv_data')
        batch_op.drop_column('arxiv_updated')
        batch_op.drop_column('arxiv_processed')
        

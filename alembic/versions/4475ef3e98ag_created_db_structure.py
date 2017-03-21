"""created db structure

Revision ID: 4475ef3e98ag
Revises: None
Create Date: 2017-19-03 11:09:19.590444

"""

# revision identifiers, used by Alembic.
revision = '4475ef3e98ag'
down_revision = None

from alembic import op
import sqlalchemy as sa

import datetime
                               

from sqlalchemy import Column, String, Integer, TIMESTAMP, DateTime, Text, Index
from sqlalchemy.sql import table, column


def upgrade():
    op.create_table('storage',
        Column('key', String(255), primary_key=True),
        Column('value', Text),
    )
    
    op.create_table('change_log',
        Column('id', Integer, primary_key=True),
        Column('created', TIMESTAMP, default=datetime.datetime.utcnow),
        Column('key', String(255), nullable=False),
        Column('oldvalue', Text),
        Column('oldvalue', Text)
    )
    
    op.create_table('records',
        Column('id', Integer, primary_key=True),
        Column('bibcode', String(19), unique=True, nullable=False),
        Column('status', String(255)),
        
        Column('metadata', Text),
        Column('orcid_claims', Text),
        Column('nonbib_data', Text),
        Column('fulltext', Text),
        
        Column('metadata_updated', TIMESTAMP),
        Column('orcid_claims_updated', TIMESTAMP),
        Column('nonbib_data_updated', TIMESTAMP),
        Column('fulltext_updated', TIMESTAMP),

        
        Column('created', TIMESTAMP),
        Column('updated', TIMESTAMP, default=datetime.datetime.utcnow),
        Column('processed', TIMESTAMP),
        
        Index('ix_recs_updated', 'updated'),
        Index('ix_recs_created', 'created'),
        Index('ix_processed', 'processed')
    )

def downgrade():
    op.drop_table('storage')
    op.drop_table('change_log')
    op.drop_table('records')

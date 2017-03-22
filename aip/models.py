# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.types import Enum
import datetime
import json
from aip.libs.utils import get_date

Base = declarative_base()

from sqlalchemy import types
from dateutil.tz import tzutc
from datetime import datetime

class UTCDateTime(types.TypeDecorator):
    impl = TIMESTAMP
    def process_bind_param(self, value, engine):
        if isinstance(value, basestring):
            return get_date(value).astimezone(tzutc())
        elif value is not None:
            return value.astimezone(tzutc()) # will raise Error is not datetime

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=tzutc())


class KeyValue(Base):
    __tablename__ = 'storage'
    key = Column(String(255), primary_key=True)
    value = Column(Text)


    
class Records(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    bibcode = Column(String(19))
    
    metadata = Column(Text)
    orcid_claims = Column(Text)
    nonbib_data = Column(Text)
    fulltext = Column(Text)

    metadata_updated = Column(UTCDateTime, default=get_date)
    orcid_claims_updated = Column(UTCDateTime, default=get_date)
    nonbib_data_updated = Column(UTCDateTime, default=get_date)
    fulltext_updated = Column(UTCDateTime, default=get_date)
    
    created = Column(UTCDateTime, default=get_date)
    updated = Column(UTCDateTime, default=get_date)
    processed = Column(UTCDateTime)
    
    def toJSON(self, for_solr=False):
        if for_solr:
            return self
        else:
            doc = {'id': self.id }
            for f in ['created', 'updated', 'processed', 
                      'metadata_updated', 'orcid_claims_updated', 'nonbib_data_updated',
                      'fulltext_updated']:
                if hasattr(self, f) and getattr(self, f):
                    doc[f] = get_date(getattr(self, f))
                else:
                    doc[f] = None
            for f in ['bibcode', 'metadata', 'orcid_claims', 'nonbib_data', 'fulltext']:
                doc[f] = getattr(self, f, None)
            return doc


class ChangeLog(Base):
    __tablename__ = 'change_log'
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=get_date)
    key = Column(String(255))
    oldvalue = Column(Text)
    newvalue = Column(Text)
    
    
    def toJSON(self):
        return {'id': self.id, 
                'key': self.key,
                'created': self.created and get_date(self.created).isoformat() or None,
                'newvalue': self.newvalue,
                'oldvalue': self.oldvalue
                }
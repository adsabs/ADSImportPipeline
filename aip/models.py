# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.types import Enum
import datetime
import json
from adsputils import get_date

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
    fingerprint = Column(Text)

    created = Column(UTCDateTime, default=get_date)
    updated = Column(UTCDateTime, default=get_date)
    processed = Column(UTCDateTime)
    
    arxiv_data = Column(Text)
    arxiv_created = Column(UTCDateTime, default=get_date)
    arxiv_updated = Column(UTCDateTime, default=get_date)
    
    _date_fields = ['created', 'updated', 'processed', 'arxiv_created', 'arxiv_updated']
    _text_fields = ['id', 'bibcode', 'fingerprint']
    _json_fields = ['arxiv_data']
    
    def toJSON(self, for_solr=False, load_only=None):
        if for_solr:
            return self
        else:
            load_only = load_only and set(load_only) or set()
            doc = {}
            
            for f in Records._text_fields:
                if load_only and f not in load_only:
                    continue
                doc[f] = getattr(self, f, None)
            for f in Records._date_fields:
                if load_only and f not in load_only:
                    continue
                if hasattr(self, f) and getattr(self, f):
                    doc[f] = get_date(getattr(self, f))
                else:
                    doc[f] = None
            for f in Records._json_fields: # json
                if load_only and f not in load_only:
                    continue
                v = getattr(self, f, None)
                if v:
                    v = json.loads(v)
                doc[f] = v
                
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
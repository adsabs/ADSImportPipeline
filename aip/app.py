"""
The main application object (it has to be loaded by any worker/script)
in order to initialize the database and get a working configuration.
"""

from __future__ import absolute_import, unicode_literals
from .models import Records, ChangeLog
from sqlalchemy.orm import load_only as _load_only
from adsputils import ADSCelery, get_date
from aip.models import Records

class ADSImportPipelineCelery(ADSCelery):
    
    def delete_by_bibcode(self, bibcode):
        with self.session_scope() as session:
            r = session.query(Records).filter_by(bibcode=bibcode).first()
            if r is not None:
                session.delete(r)
                session.add(ChangeLog(key='deleted', oldvalue=bibcode))
                session.commit()
    
    
    def update_storage(self, bibcode, **kwargs):
        """Update database record; you can pass in the kwargs
        the payload; only 'data' and fingerprint are considered
        payload. The record will be created if the bibcode is 
        seen the first time.
        
        @param bibcode: bibcode
        @keyword kwargs: dictionary with payload, keys correspond
            to the `Records` attribute
        @return: JSON representation of the record
        """
        
        with self.session_scope() as session:
            r = session.query(Records).filter_by(bibcode=bibcode).first()
            updated = False
            if r is None:
                updated = True
                r = Records(bibcode=bibcode)
                session.add(r)
            
            now = get_date()
            for k, v in kwargs.items():
                if k == 'fingerprint':
                    r.__setattr__(k, v)
                elif '_data' in k and hasattr(r, k):
                    colname, _ = k.split('_')
                    r.__setattr__(k, v)
                    if r.__getattr__('{}_created').format(colname) is None:
                        r.__setattr__('{}_created'.format(colname), now)
                    r.__setattr__('{}_upated'.format(colname), now)
                    updated = True
                elif k == 'origin':
                    r.__setattr__(k, v)
                    if v == 'direct':
                        r.__setattr__('direct_created', now)
                    updated = True
                    
            if updated:
                r.updated = now
                session.commit()

            return r.toJSON()
    
    
    def get_record(self, bibcode, load_only=None):
        if isinstance(bibcode, list):
            out = []
            with self.session_scope() as session:
                q = session.query(Records).filter(Records.bibcode.in_(bibcode))
                if load_only:
                    q = q.options(_load_only(*load_only))
                for r in q.all():
                    out.append(r.toJSON(load_only=load_only))
            return out
        else:
            with self.session_scope() as session:
                q = session.query(Records).filter_by(bibcode=bibcode)
                if load_only:
                    q = q.options(_load_only(*load_only))
                r = q.first()
                if r is None:
                    return None
                return r.toJSON(load_only=load_only)
       
    
    def update_processed_timestamp(self, bibcode):
        with self.session_scope() as session:
            r = session.query(Records).filter_by(bibcode=bibcode).first()
            if r is None:
                raise Exception('Cant find bibcode {0} to update timestamp'.format(bibcode))
            r.processed = get_date()
            session.commit()

    def compute_orphaned(self, canonical_bibcodes):
        """return a list of orphaned bibcodes, compare database to passed canonical """
        orphaned = set()
        # get all bibcodes from the storage (into memory)
        store = set()
        with self.session_scope() as session:
            for r in session.query(Records).filter(Records.origin=='classic').options(_load_only('bibcode')).yield_per(1000):
                store.add(r.bibcode)
            orphaned = store.difference(canonical_bibcodes)
            self.logger.info('Found %s orphaned bibcode, %s canonical, %s from database',
                             len(orphaned), len(canonical_bibcodes), len(store))
        return orphaned

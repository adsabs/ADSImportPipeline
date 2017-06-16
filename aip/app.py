"""
The main application object (it has to be loaded by any worker/script)
in order to initialize the database and get a working configuration.
"""

from __future__ import absolute_import, unicode_literals
from .models import KeyValue, Records, ChangeLog
import adsputils as utils
from celery import Celery
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import load_only as _load_only
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


def create_app(app_name='ADSImportPipeline',
               local_config=None):
    """Builds and initializes the Celery application."""
    
    conf = utils.load_config()
    if local_config:
        conf.update(local_config)

    app = ADSImportPipelineCelery(app_name,
             broker=conf.get('CELERY_BROKER', 'pyamqp://'),
             include=conf.get('CELERY_INCLUDE', ['aip.tasks']))

    app.init_app(conf)
    return app



class ADSImportPipelineCelery(Celery):
    
    def __init__(self, app_name, *args, **kwargs):
        Celery.__init__(self, *args, **kwargs)
        self._config = utils.load_config()
        self._session = None
        self._engine = None
        self.logger = utils.setup_logging(app_name) #default logger
        
    

    def init_app(self, config=None):
        """This function must be called before you start working with the application
        (or worker, script etc)
        
        :return None
        """
        
        if self._session is not None: # the app was already instantiated
            return
        
        if config:
            self._config.update(config) #our config
            self.conf.update(config) #celery's config (devs should be careful to avoid clashes)
        
        self.logger = utils.setup_logging('app', level=self._config.get('LOGGING_LEVEL', 'INFO'))
        self._engine = create_engine(config.get('SQLALCHEMY_URL', 'sqlite:///'),
                               echo=config.get('SQLALCHEMY_ECHO', False))
        self._session_factory = sessionmaker()
        self._session = scoped_session(self._session_factory)
        self._session.configure(bind=self._engine)
    
    
    def close_app(self):
        """Closes the app"""
        self._session = self._engine = self._session_factory = None
        self.logger = None
    
        
    @contextmanager
    def session_scope(self):
        """Provides a transactional session - ie. the session for the 
        current thread/work of unit.
        
        Use as:
        
            with session_scope() as session:
                o = ModelObject(...)
                session.add(o)
        """
    
        if self._session is None:
            raise Exception('init_app() must be called before you can use the session')
        
        # create local session (optional step)
        s = self._session()
        
        try:
            yield s
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()
            
    def delete_by_bibcode(self, bibcode):
        with self.session_scope() as session:
            r = session.query(Records).filter_by(bibcode=bibcode).first()
            if r is not None:
                session.delete(r)
                session.commit()
    
    
    def update_storage(self, bibcode, fingerprint):
        with self.session_scope() as session:
            r = session.query(Records).filter_by(bibcode=bibcode).first()
            if r is None:
                r = Records(bibcode=bibcode)
                session.add(r)
            now = utils.get_date()
            r.fingerprint = fingerprint
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
            r.processed = utils.get_date()
            session.commit()
    

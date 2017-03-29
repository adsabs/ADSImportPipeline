"""
Contains useful functions and utilities that are not neccessarily only useful
for this module. But are also used in differing modules insidide the same
project, and so do not belong to anything specific.
"""


import os
import logging
import imp
import sys
import json
from dateutil import parser, tz
from datetime import datetime

from cloghandler import ConcurrentRotatingFileHandler
local_zone = tz.tzlocal()
utc_zone = tz.tzutc()

def get_date(timestr=None):
    """
    Always parses the time to be in the UTC time zone; or returns
    the current date (with UTC timezone specified)
    
    :param: timestr
    :type: str or None
    
    :return: datetime object with tzinfo=tzutc()
    """
    if timestr is None:
        return datetime.utcnow().replace(tzinfo=utc_zone)
    
    if isinstance(timestr, datetime):
        date = timestr
    else:
        date = parser.parse(timestr)
    
    if 'tzinfo' in repr(date): #hack, around silly None.encode()...
        date = date.astimezone(utc_zone)
    else:
        # this depends on current locale, for the moment when not 
        # timezone specified, I'll treat them as UTC (however, it
        # is probably not correct and should work with an offset
        # but to that we would have to know which timezone the
        # was created) 
        
        #local_date = date.replace(tzinfo=local_zone)
        #date = date.astimezone(utc_zone)
        
        date = date.replace(tzinfo=utc_zone)
        
    return date


def load_config():
    """
    Loads configuration from config.py and also from local_config.py
    
    :return dictionary
    """
    conf = {}
    PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    if PROJECT_HOME not in sys.path:
        sys.path.append(PROJECT_HOME)
    conf['PROJECT_HOME'] = PROJECT_HOME
    
    conf.update(load_module(os.path.join(PROJECT_HOME, 'config.py')))
    conf.update(load_module(os.path.join(PROJECT_HOME, 'local_config.py')))
    
    return conf

def load_module(filename):
    """
    Loads module, first from config.py then from local_config.py
    
    :return dictionary
    """
    
    filename = os.path.join(filename)
    d = imp.new_module('config')
    d.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
    except IOError as e:
        pass
    res = {}
    from_object(d, res)
    return res

def setup_logging(file_, name_, level='WARN'):
    """
    Sets up generic logging to file with rotating files on disk

    :param file_: the __file__ doc of python module that called the logging
    :param name_: the name of the file that called the logging
    :param level: the level of the logging DEBUG, INFO, WARN
    :return: logging instance
    """

    level = getattr(logging, level)

    logfmt = u'%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
    datefmt = u'%m/%d/%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=logfmt, datefmt=datefmt)
    logging_instance = logging.getLogger(name_)
    fn_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')), 'logs')
    if not os.path.exists(fn_path):
        os.makedirs(fn_path)
    fn = os.path.join(fn_path, '{0}.log'.format(name_))
    rfh = ConcurrentRotatingFileHandler(filename=fn,
                                        maxBytes=2097152,
                                        backupCount=5,
                                        mode='a',
                                        encoding='UTF-8')  # 2MB file
    rfh.setFormatter(formatter)
    logging_instance.handlers = []
    logging_instance.addHandler(rfh)
    logging_instance.setLevel(level)

    return logging_instance


def from_object(from_obj, to_obj):
    """Updates the values from the given object.  An object can be of one
    of the following two types:

    Objects are usually either modules or classes.
    Just the uppercase variables in that object are stored in the config.

    :param obj: an import name or object
    """
    for key in dir(from_obj):
        if key.isupper():
            to_obj[key] = getattr(from_obj, key)


def overrides(interface_class):
    """
    To be used as a decorator, it allows the explicit declaration you are
    overriding the method of class from the one it has inherited. It checks that
     the name you have used matches that in the parent class and returns an
     assertion error if not
    """
    def overrider(method):
        """
        Makes a check that the overrided method now exists in the given class
        :param method: method to override
        :return: the class with the overriden method
        """
        assert(method.__name__ in dir(interface_class))
        return method

    return overrider


def _date_handler(item):
    return item.isoformat() if hasattr(item, 'isoformat') else item

def dump_json(obj):
    return json.dumps(obj, default=_date_handler)

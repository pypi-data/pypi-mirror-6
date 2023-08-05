import logging
from os import environ

__logger = None

def init():
    global __logger
    __logger = logging.getLogger('km2pg')
    __logger.addHandler(logging.StreamHandler())
    if 'ASA_LOGLEVEL' in environ and environ['ASA_LOGLEVEL'] == 'debug':
        __logger.setLevel(logging.DEBUG)

def getLogger():
    if not __logger:
        init()
    return __logger

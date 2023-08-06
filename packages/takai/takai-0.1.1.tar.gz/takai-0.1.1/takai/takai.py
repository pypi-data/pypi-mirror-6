__author__  = 'Yaw Boakye Yiadom'
__date__    = 'October 7, 2013'
__license__ = 'MIT'

from sys import stderr, exit
from os import environ
from takai.constants import *
import json

class Takai(object):
    def __init__(self, MASTER_KEY_ENV_VAR=None, PRIVATE_KEY_ENV_VAR=None, API):
        try:
            self.MASTER   = MASTER_KEY_ENV_VAR  or environ[MASTER_KEY_ENV_VAR]
            self.PRIVATE  = PRIVATE_KEY_ENV_VAR or environ[PRIVATE_KEY_ENV_VAR]
            self.API      = API
            self.mpower = takai.httpsconn.Connection('app.mpowerpayments.com/{}'.format(self.API))
        except KeyError as error:
            stderr.write('The environment variables you specified are not set in your envs')
            raise KeyError(error) #re-raise original error after good enough information


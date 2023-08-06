import datetime
import logging
import os
import random
import time

try:
    from cloghandler import (
        ConcurrentRotatingFileHandler as RotatingFileHandler
    )
except ImportError:
    from logging.handlers import RotatingFileHandler 

import requests

class MultyvacError(Exception):
    pass

class MultyvacRequestError(Exception):
    """Exception class for errors when making web requests to the
    Multyvac API."""

    def __init__(self, code, message, hint=None, retry=False):
        Exception.__init__(self, code, message, hint, retry)
        self.code = code
        self.message = message
        self.hint = hint
        self.retry = retry
    
    def __str__(self):
        return '%s (Code: %s Hint: %s)' % (self.message, self.code, self.hint)
    
    def __repr__(self):
        return 'MultyvacError({code}, "{message}", {hint})'.format(
                    code=self.code,
                    message=self.message,
                    hint=self.hint,
                )

class Multyvac(object):
    """
    Multyvac

    The primary object for interacting with the Multyvac API.
    All Multyvac modules are exposed through this.
    """
    
    _ASK_GET = 'GET'
    _ASK_POST = 'POST'
    _ASK_PUT = 'PUT'
    
    def __init__(self, api_key=None, api_secret_key=None, api_url=None):
        self._session = requests.session()
        
        from .config import ConfigModule
        # Note: At this time, the rest of the Multyvac modules have not been
        # initialized. So the constructor should not do anything that requires
        # any other modules (ie. Do not use the ApiKey module).
        self.config = ConfigModule(self, api_key, api_secret_key, api_url)
        
        # Must be after config
        self._setup_logger()
        
        from .job import JobModule
        self.job = JobModule(self)
        from .layer import LayerModule
        self.layer = LayerModule(self)
        from .volume import VolumeModule
        self.volume = VolumeModule(self)
        from .api_key import ApiKeyModule
        self.api_key = ApiKeyModule(self)
    
    def _setup_logger(self):
        """
        Sets up a rotating file logger.
        TODO: Have config option for printing to screen.
        """
        
        logs_path = os.path.join(self.config.get_multyvac_path(), 'log')
        if not os.path.exists(logs_path):
            self.config._create_path_ignore_existing(logs_path)
        log_path = os.path.join(logs_path, 'multyvac.log')
            
        self._logger = logging.getLogger('multyvac')
        self._logger.setLevel(logging.INFO)
    
        handler = RotatingFileHandler(log_path, 'a', 512*1024, 10)
        formatter = logging.Formatter(
            '[%(asctime)s] - [%(levelname)s] - %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
    
    def _get_session_method(self, method):
        if method == self._ASK_POST:
            return self._session.post
        elif method == self._ASK_GET:
            return self._session.get
        elif method == self._ASK_PUT:
            return self._session.put
        else:
            raise KeyError('Unknown method "%s"' % method)
    
    def _ask(self, method, uri, auth=None, params=None, data=None,
             headers=None, files=None):
        
        attempt = 0
        max_attempts = 4
        while True:
            try:
                self._logger.info('%s request to %s', method, uri)
                r = self._ask_helper(method,
                                     uri,
                                     auth=auth,
                                     params=params,
                                     data=data,
                                     headers=headers,
                                     files=files)
                return r
            except MultyvacRequestError as e:
                attempt += 1
                if e.retry and attempt < max_attempts:
                    delay = 2**attempt * random.random()
                    self._logger.info('Request failed. Retrying in %.1fs',
                                      delay)
                    time.sleep(delay)
                    continue
                else:
                    raise
    
    def _ask_helper(self, method, uri, auth, params, data, headers, files):
        
        if not auth:
            auth = self.config.get_auth()
        
        r = self._get_session_method(method)(
                self.config.api_url + uri,
                auth = auth,
                params=params,
                data=data,
                headers=headers,
                files=files,
            )
        
        try:
            obj = r.json()
        except ValueError:
            raise MultyvacRequestError(500,
                                       'Unknown error',
                                       hint=r.text)
        if 'error' in obj:
            raise MultyvacRequestError(obj['error']['code'],
                                       obj['error']['message'],
                                       obj['error'].get('hint'),
                                       obj['error'].get('retry'))
        
        return obj
        
    def running_on_multyvac(self):
        """Returns True if this process is currently running on Multyvac."""
        return os.environ.get('RUNNING_ON_MULTYVAC') == 'true'

class MultyvacModule(object):
    """All modules should extend this class."""
    def __init__(self, multyvac):
        self.multyvac = multyvac
        logger_name = self.__class__.__name__.lower()[:-len('module')]
        self._logger = logging.getLogger('multyvac.%s' % logger_name)

    @staticmethod
    def clear_null_entries(d):
        for k, v in d.items():
            if v is None:
                del d[k]

    @staticmethod
    def convert_str_to_datetime(s):
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # FIXME
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def check_success(r):
        return r['status'] == 'ok'
    
    @staticmethod
    def is_iterable_list(obj):
        return hasattr(obj, '__iter__')


class MultyvacModel(object):
    def __init__(self, multyvac=None, **kwargs):
        if multyvac:
            self.multyvac = multyvac
        else:
            raise Exception('Needs multyvac object for now')
            
    def __str__(self):
        return repr(self)


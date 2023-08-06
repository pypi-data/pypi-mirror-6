import json
import os

from .multyvac import (
    MultyvacError,
    MultyvacModule,
)

class ConfigError(MultyvacError):
    """Raised when Multyvac's configuration is incomplete or incorrect."""
    pass

class ConfigModule(MultyvacModule):
    """Top-level Config module. Use this through ``multyvac.config``."""
    
    def __init__(self, multyvac, api_key=None, api_secret_key=None,
                 api_url=None):
        MultyvacModule.__init__(self, multyvac)
        
        self.api_key = None
        self.api_secret_key = None
        self.api_url = api_url or 'https://api.multyvac.com'
        
        self._multyvac_path = self.get_multyvac_path()
        #self._credentials_path = self._get_credentials_path()
        ConfigModule._create_path_ignore_existing(self._multyvac_path)
        #ConfigModule._create_path_ignore_existing(self._credentials_path)
        self._config_name = 'multyvac.json'
        self._config_path = os.path.join(self._multyvac_path, self._config_name)
        
        self._load_config()
        
        if os.environ.get('MULTYVAC_API_KEY'):
            self.api_key = os.environ.get('MULTYVAC_API_KEY')
            if os.environ.get('MULTYVAC_API_SECRET_KEY'):
                self.api_secret_key = os.environ.get('MULTYVAC_API_SECRET_KEY')
            if os.environ.get('MULTYVAC_API_URL'):
                self.api_url = os.environ.get('MULTYVAC_API_URL')
        
        self.api_key = api_key or self.api_key
        self.api_secret_key = api_secret_key or self.api_secret_key
        self.api_url = api_url or self.api_url or 'https://api.multyvac.com'
    
    def get_api_domain(self):
        """Returns the domain of the Multyvac API endpoint."""
        return self.api_url[self.api_url.index('//')+2:]
    
    def get_multyvac_path(self):
        """Returns the path on the filesystem to the multyvac configuration
        directory."""
        if os.name == 'nt' and os.environ.get('APPDATA'):
            path = os.path.join(os.environ.get('APPDATA'), 'multyvac')
        else:
            path = os.path.join('~', '.multyvac')
        return os.path.expanduser(path)
    
    def _get_credentials_path(self, api_key=None):
        if api_key:
            return os.path.join(self._multyvac_path,
                                self.get_api_domain(),
                                api_key)
        else:
            return os.path.join(self._multyvac_path,
                                self.get_api_domain())
    
    @staticmethod
    def _create_path_ignore_existing(path):
        """Create a path if it doesn't exist. Ignore any race condition errors
        if the path happens to be created while this is executing."""
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != 17:
                    raise
    
    def get_auth(self):
        """If a key is set, returns a tuple of (api key, api secret key).
        Otherwise, raises a ConfigError."""
        if not self.api_key:
            raise ConfigError('Api Key is not set')
        return (self.api_key, self.api_secret_key)
        
    def path_to_private_key(self):
        """Returns the path on the file system to the private key necessary to
        SSH into a job. Note that this private key is tied to the currently
        set api key."""
        private_key_path = self._get_credentials_path(self.api_key + '.key')
        if os.path.exists(private_key_path):
            return private_key_path
        else:
            self._get_and_save_ssh_key(self.api_key)
            return private_key_path
    
    def set_key(self, api_key, api_secret_key, api_url=None):
        """
        Sets the API credentials forcibly replacing any other credentials
        that have been set.
        
        :param api_key: The ApiKey id.
        :param api_secret_key: The ApiKey secret.
        :param api_url: The API end point to use.
        """
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.api_url = api_url or self.api_url
    
    def _load_config(self):
        if os.path.exists(self._config_path):
            with open(self._config_path) as f:
                conf = json.load(f)
                self.api_key = conf['default_api_key']
                self.api_url = conf['api_url']
                # only load if we have an api key
                if self.api_key:
                    self._load_credential_from_disk(self.api_key)
        else:
            self.save_to_disk()
        
    def _load_credential_from_disk(self, api_key):
        credential_path = self._get_credentials_path(api_key)
        if os.path.exists(credential_path + '.json'):
            with open(credential_path + '.json') as f:
                credential = json.load(f)
            self.api_secret_key = credential['api_secret_key']
        else:
            raise ConfigError('Could not find credentials for api_key '
                                      '%s on disk' % api_key)
        
    def _get_and_save_ssh_key(self, api_key):
        """Assumes that the api_key and secret_key are valid"""
        key = self.multyvac.api_key.get(api_key)
        if not api_key:
            raise KeyError('Could not get find key.')
        
        credentials_path = self._get_credentials_path()
        self._create_path_ignore_existing(credentials_path)
        
        credential_path = self._get_credentials_path(api_key)
        with open(credential_path+'.key', 'w') as f:
            f.write(key.private_key)
        os.chmod(credential_path+'.key', 0600)
        
        
    def save_to_disk(self):
        """Saves the current configuration to disk. The next time multyvac
        is imported, the current configurations will be available."""
        with open(self._config_path, 'w') as f:
            d = {'default_api_key': self.api_key,
                 'api_url': self.api_url,
                 }
            json.dump(d, f, indent=4)
        credentials_path = self._get_credentials_path()
        self._create_path_ignore_existing(credentials_path)
        if self.api_key:
            credential_path = self._get_credentials_path(self.api_key)
            with open(credential_path + '.json', 'w') as f:
                d = {'api_secret_key': self.api_secret_key}
                json.dump(d, f, indent=4)

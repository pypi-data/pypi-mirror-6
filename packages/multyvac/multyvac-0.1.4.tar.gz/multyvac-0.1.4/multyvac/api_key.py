from .multyvac import (
    Multyvac,
    MultyvacModel,
    MultyvacModule,
)

class ApiKey(MultyvacModel):
    
    def __init__(self, id, **kwargs):
        MultyvacModel.__init__(self, **kwargs)
        
        self.id = id
        self.secret_key = kwargs.get('secret_key')
        self.public_key = kwargs.get('public_key')
        self.private_key = kwargs.get('private_key')
        self.created = kwargs.get('created')
        self.active = kwargs.get('active')

    def activate(self):
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/key/%s/activate' % self.id)
        self.active = True
        return MultyvacModule.check_success(r)

    def deactivate(self):
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/key/%s/deactivate' % self.id)
        self.active = False
        return MultyvacModule.check_success(r)

    def __repr__(self):
        return 'ApiKey(%s)' % repr(self.id)

class ApiKeyModule(MultyvacModule):
    
    def get(self, id, username=None, password=None):
        auth = ('web-'+username, password) if username else None
        iter_in = MultyvacModule.is_iterable_list(id)
        params = {'id': id}
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/key',
                               auth=auth,
                               params=params)
        keys = [ApiKey(multyvac=self.multyvac, **k) for k in r['keys']]
        if iter_in:
            return keys
        else:
            return keys[0] if keys else None
        
        return ApiKey(id=id, multyvac=self.multyvac)
    
    def list(self, username=None, password=None):
        auth = ('web-'+username, password) if username else None
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/key',
                               auth=auth)
        return [ApiKey(multyvac=self.multyvac, **k) for k in r['keys']]

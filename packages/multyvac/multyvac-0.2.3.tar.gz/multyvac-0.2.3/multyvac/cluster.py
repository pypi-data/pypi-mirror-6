import json

from .multyvac import (
    Multyvac,
    MultyvacModel,
    MultyvacModule,
)

class Cluster(MultyvacModel):
    """Represents a Multyvac Cluster and its associated operations."""
    
    def __init__(self, id, **kwargs):
        """Creates a new Cluster."""
        MultyvacModel.__init__(self, **kwargs)
        
        self.id = id
        self.duration = kwargs.get('duration')
        self.requested_at = kwargs.get('requested_at')
        self.provisioned_at = kwargs.get('provisioned_at')
        self.released_at = kwargs.get('released_at')

    def release(self):
        """Releases the cluster's resources."""
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/cluster/%s/release' % self.id)
        return MultyvacModule.check_success(r)

    def __repr__(self):
        return 'Cluster(%s)' % repr(self.id)

class ClusterModule(MultyvacModule):
    """Top-level Cluster module. Use this through ``multyvac.cluster``."""
    
    def get(self, id):
        """
        Returns a Cluster object.
        
        :param id: Id of cluster.
        """
        iter_in = MultyvacModule.is_iterable_list(id)
        params = {'id': id}
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/cluster',
                               params=params)
        clusters = [Cluster(multyvac=self.multyvac, **k) for k in r['clusters']]
        if iter_in:
            return clusters
        else:
            return clusters[0] if clusters else None
        
        return Cluster(id=id, multyvac=self.multyvac)
    
    def create(self, core, core_count, duration=None):
        """
        Creates a new cluster.
        
        :param core: The core type to provision.
        :param core_count: The number of cores to provision.
        :param duration: The number of hours to keep cluster up for.
        """
        
        cluster = {'core': core,
                   'core_count': core_count,
                   }
        MultyvacModule.clear_null_entries(cluster)
        payload = {'cluster': cluster}
        headers = {'content-type': 'application/json'}
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/cluster',
                               data=json.dumps(payload),
                               headers=headers)
        return MultyvacModule.check_success(r)
    
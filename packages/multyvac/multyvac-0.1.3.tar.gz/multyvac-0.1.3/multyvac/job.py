import base64
try: import cPickle as pickle
except: import pickle
try: from cStringIO import StringIO
except: import StringIO
import json
import socket
import subprocess
import time

from .multyvac import (
    Multyvac,
    MultyvacModel,
    MultyvacModule,
    MultyvacRequestError,
)
from .util import preinstalls
from .util.module_dependency import ModuleDependencyAnalyzer

class Job(MultyvacModel):
    
    status_waiting = 'waiting'
    status_queued = 'queued'
    status_processing = 'processing'
    
    status_done = 'done'
    status_error = 'error'
    status_killed = 'killed'
    status_stalled = 'stalled'
    
    finished_statuses = [status_done,
                         status_error,
                         status_killed,
                         status_stalled,
                         ]
    
    def __init__(self, jid, **kwargs):
        MultyvacModel.__init__(self, **kwargs)
        self.jid = jid
        
        self.cmd = kwargs.get('cmd')
        self.core = kwargs.get('core')
        self.created = kwargs.get('created_at')
        self.multicore = kwargs.get('multicore')
        self.name = kwargs.get('tags', {}).get('name')
        self.status = kwargs.get('status')
        self.tags = kwargs.get('tags')
    
        result = kwargs.get('result')
        self.result_type = kwargs.get('result_type')
        if result and self.result_type  == 'pickle':
            self.result = pickle.loads(base64.b64decode(result))
        elif result and self.result_type == 'binary':
            self.result = base64.b64decode(result)
        else:
            self.result = result
        self.return_code = kwargs.get('return_code')
        
        self.started_at = kwargs.get('started_at')
        self.finished_at = kwargs.get('finished_at')
        self.runtime = kwargs.get('runtime')
        
        self.cputime_user = kwargs.get('collected', {}).get('cputime_user')
        self.cputime_system = kwargs.get('collected', {}).get('cputime_system')
        self.memory_failcnt = kwargs.get('collected', {}).get('memory_failcnt')
        self.memory_max_usage = kwargs.get('collected', {}).get('memory_max_usage')
        self.ports = kwargs.get('collected', {}).get('ports')
        self.stderr = kwargs.get('stderr')
        self.stdout = kwargs.get('stdout')
    
    def kill(self):
        """
        :param jid: Can be a number or list of numbers.
        """
        
        data = {'jid': self.jid}
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/job/kill',
                               data=data)
        return MultyvacModule.check_success(r)
    
    def wait(self, status=finished_statuses, timeout=None):
        """
        Wait for the job to reach the specified status.
        
        :param status: Can be a status string or a list of strings.
        
        Returns the status if the job reaches it, otherwise on a timeout
        returns False.
        """
        start_time = time.time()
        poll_period = 1
        max_poll_period = 10
        while True:
            current_time = time.time()
            time_elapsed = current_time - start_time
            if timeout and time_elapsed > timeout:
                return False
            elif self.status == status or self.status in status:
                return self.status
            else:
                sleep_time = (min(poll_period, timeout - time_elapsed)
                              if timeout else poll_period)
                time.sleep(sleep_time)
                if poll_period < max_poll_period:
                    poll_period += 0.5
                self.update()
    
    def wait_for_open_port(self, port, timeout=None):
        """Blocks until it detects that port has been opened by the job."""
        self.wait(self.finished_statuses + [self.status_processing], timeout)
        if self.status == self.status_processing:
            attempt = 1
            max_attempts = 5
            while attempt < max_attempts and self.status == Job.status_processing:
                if not self.ports or not self.ports.get('tcp', {}).get(str(port)):
                    # Wait for SSH to start
                    time.sleep(2.0)
                    attempt += 1
                    self.update()
                else:
                    return True
            else:
                return False
        else:
            return False
    
    def open_ssh_console(self):
        """Opens an SSH console to a running job. If a job is queued, waits
        indefinitely until it is processing."""
        
        if self.wait_for_open_port(22):
            info = self.ports.get('tcp', {}).get('22')
            address = info['address']
            port = info['port']
            cmd = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -X -p {port} -i {key_path} '
                   ' multyvac@{address}'.format(
                        port=port,
                        key_path=self.multyvac.config.path_to_private_key(),
                        address=address,)
                   )
            p = subprocess.Popen(cmd, shell=True)
            p.wait()
        
    def run_command(self, cmd):
        """
        Runs the specified command over ssh.
        
        If successful, returns (stdout, stderr). Otherwise, returns None.
        """
        self.wait(self.finished_statuses + [self.status_processing])
        if self.status == self.status_processing:
            if not self.ports.get('tcp', {}).get('22'):
                # Wait for SSH to start
                time.sleep(8.0)
                self.update()
            info = self.ports.get('tcp', {}).get('22')
            if not info:
                self.multyvac.job._logger.info('Port 22 is not open')
                return
            address = info['address']
            port = info['port']
            cmd = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -p {port} -i {key_path} '
                   ' multyvac@{address} {cmd}'.format(
                        port=port,
                        key_path=self.multyvac.config.path_to_private_key(),
                        address=address,
                        cmd=cmd)
                   )
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            return p.communicate()
        else:
            self.multyvac.job._logger.info('Cannot SSH into finished job')
            return
    
    def update(self):
        """Updates this Job object with the latest version available of itself
        from Multyvac."""
        j = self.multyvac.job.get(self.jid)
        self.__dict__ = j.__dict__
        return self.status

    def __repr__(self):
        if self.name:
            return 'Job(%s, name=%s)' % (repr(self.jid), repr(self.name))
        else:
            return 'Job(%s)' % repr(self.jid)


class JobModule(MultyvacModule):

    def __init__(self, *args, **kwargs):
        MultyvacModule.__init__(self, *args, **kwargs)
        self._modulemgr = ModuleDependencyAnalyzer()
        preinstalled_modules = [name for name, _ in preinstalls.modules]
        self._modulemgr.ignore(preinstalled_modules)
    
    def _normalize_vol(self, vol):
        if isinstance(vol, basestring):
            return [{'name': vol}]
        elif isinstance(vol, dict):
            return [vol]
        elif hasattr(vol, '__iter__'):
            if isinstance(vol[0], dict):
                return vol
            elif isinstance(vol[0], basestring):
                return [{'name': v} for v in vol]
            else:
                raise TypeError('vol must be a iterable of strings or dicts')
        else:
            raise TypeError('vol must be a string, dict, or iterable')
        
    def _normalize_layer(self, layer):
        if isinstance(layer, basestring):
            return [{'name':layer}]
        elif isinstance(layer, dict):
            return [layer]
        else:
            raise TypeError('layer must be a string or dict')

    def shell_submit(self, cmd, _name=None, _core='c1', _multicore=1,
                     _layer=None,  _vol=None, _env=None,
                     _result_source='stdout', _result_type='binary',
                     _max_runtime=None, _profile=False, _restartable=True,
                     _tags=None, _depends_on=None, _stdin=None):
        
        job = {
               'cmd': cmd,
               'name': _name,
               'core': _core,
               'multicore': _multicore,
               'profile': _profile,
               'restartable': _restartable,
               'depends_on': _depends_on,
               'tags': _tags,
               'layer': self._normalize_layer(_layer) if _layer else None,
               'vol': self._normalize_vol(_vol) if _vol else None,
               'env': _env,
               'result_source': _result_source,
               'result_type': _result_type,
               'max_runtime': _max_runtime,
               }
        
        if _stdin:
            job['stdin'] = base64.b64encode(_stdin)
        
        MultyvacModule.clear_null_entries(job)
        
        payload = {'jobs': [job]}
        
        headers = {'content-type': 'application/json'}
        
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/job',
                               data=json.dumps(payload),
                               headers=headers)
        return r['jids'][0]

    def _get_auto_module_volume_name(self):
        return 'auto-deps-%s' % socket.gethostname()

    def submit(self, f, *args, **kwargs):
        """Submit job based on Python function to Multyvac.
        See arguments to shell_submit."""
        #_name=None, _core='c1', _multicore=1, _layer=None, _vol=None,
        #       _env=None, _result_source='stdout', _max_runtime=None,
        #       _profile=False, _restartable=True, _tags=None, _depends_on=None, _stdin=None):
        
        f_kwargs = {}
        for k, v in kwargs.items():
            if not k.startswith('_'):
                f_kwargs[k] = v
                del kwargs[k]
        
        from .util.cloudpickle import CloudPickler
        
        s = StringIO()
        cp = CloudPickler(s, 2)
        cp.dump((f, args, f_kwargs))
        
        # Add modules
        for module in cp.modules:
            self._modulemgr.add(module.__name__)
        
        mod_paths = self._modulemgr.get_and_clear_paths()
        
        vol_name = self._get_auto_module_volume_name()
        if self._modulemgr.has_module_dependencies:
            v = self.multyvac.volume.get(vol_name)
            if not v:
                try:
                    self.multyvac.volume.create(vol_name, '/pymodules')
                except MultyvacRequestError as e:
                    if 'name already exists' not in e.message:
                        raise
                v = self.multyvac.volume.get(vol_name)
            if mod_paths:
                v.sync_up(mod_paths, '')
            
        kwargs['_stdin'] = s.getvalue()
        kwargs['_result_source'] = 'file:/tmp/.result'
        kwargs['_result_type'] = 'pickle'
        if self._modulemgr.has_module_dependencies:
            kwargs.setdefault('_vol', []).append(vol_name)
        # Add to the PYTHONPATH if user is using it as well
        env = kwargs.setdefault('_env', {})
        if env.get('PYTHONPATH'):
            env['PYTHONPATH'] = env['PYTHONPATH'] + ':/pymodules'
        else:
            env['PYTHONPATH'] = '/pymodules'
        
        return self.shell_submit(
            'python -m multyvacinit.pybootstrap',
            **kwargs
        )

    def list(self, jid=None, name=None, limit=50):
        """Returns a list of jobs matching.
        Add filter by tags."""
        params = {'jid': jid,
                  'name': name,
                  'limit': limit,
                  #'field': self.fields,
                  }
        MultyvacModule.clear_null_entries(params)
        
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/job',
                               params=params)
        for job in r['jobs']:
            job['created_at'] = MultyvacModule.convert_str_to_datetime(job['created_at'])
        return r['jobs']
    
    def get(self, jid):
        """
        :param jid: Can be a number or list of numbers.
        
        Returns a list if input was a list, otherwise returns an object.
        """
        iter_in = MultyvacModule.is_iterable_list(jid)
        params = {'jid': jid}
        if not iter_in:
            params['limit'] = 1
        jobs = self._get(params)
        if iter_in:
            return jobs
        else:
            return jobs[0] if jobs else None
    
    def get_by_name(self, name):
        """Returns the job with the matching :param name:.
        
        This function cannot be used to query multiple names are once."""
        
        iter_in = MultyvacModule.is_iterable_list(name)
        if iter_in:
            raise ValueError('name can only be a string, not a list')
        
        params = {'name': name,
                  'limit': 1}
        jobs = self._get(params)
        
        return jobs[0] if jobs else None
    
    def _get(self, more_params):
        
        params = {#'field': self.fields
                  }
        params.update(more_params)
        
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/job',
                               params=params)
        for job in r['jobs']:
            job['created_at'] = MultyvacModule.convert_str_to_datetime(job['created_at'])
        return [Job(multyvac=self.multyvac, **job) for job in r['jobs']]

    def kill(self, jid):
        """
        :param jid: Can be a number or list of numbers.
        """
        
        data = {'jid': jid}
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/job/kill',
                               data=data)
        return MultyvacModule.check_success(r)

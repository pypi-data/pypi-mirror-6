from .multyvac import (
    Multyvac,
    MultyvacError,
    RequestError
)

# Default Multyvac singleton
_multyvac = Multyvac()

on_multyvac = _multyvac.on_multyvac
send_log_to_support = _multyvac.send_log_to_support

# Job methods that have been elevated to top level
from .job import JobError
modulemgr = _multyvac.job._modulemgr
get = _multyvac.job.get
get_by_name = _multyvac.job.get_by_name
list = _multyvac.job.list
kill = _multyvac.job.kill
shell_submit = _multyvac.job.shell_submit
submit = _multyvac.job.submit

# All other modules
from .config import ConfigError
config = _multyvac.config
from .volume import SyncError
volume = _multyvac.volume
api_key = _multyvac.api_key
layer = _multyvac.layer

"""
A pluggable abstract queueing API designed to be used within a Django project
but useful within a general Python application too.  The design is modeled
after a pluggable backend system ala django.core.cache.
"""
from os import environ as os_environ
from inspect import isclass as inspect_isclass

__version_raw__ = ['0', '7', '2']
__version__ = VERSION = '.'.join(__version_raw__)
def get_version():# pragma: no cover
    '''get the version number'''
    return VERSION

class InvalidBackend(Exception):
    '''Invalid backend exception.'''
    pass

class QueueException(Exception):
    '''Queue Exception.'''
    pass

# TODO: raise exceptions when stuff doesn't get stored/returned properly?
# i.e. unified API and handle what each backend returns.

# Handle QUEUE_BACKEND set from either DJANGO_SETTINGS_MODULE or an environment
# variable. If set both places, django takes precedence.
try:
    from django.conf import settings
    if (os_environ.get('DJANGO_SETTINGS_MODULE', None) is None and
        not settings.configured):
        raise ImportError
    GETSETTING = lambda *args: getattr(settings, *args)
except ImportError:
    GETSETTING = os_environ.get

BACKEND = GETSETTING('QUEUE_BACKEND', None)

if not BACKEND:
    raise InvalidBackend("QUEUE_BACKEND not set.")

# Set up queue_front.queues to point to the proper backend.
try:
    # Most of the time we'll be importing a bundled backend,
    # so look here first.  You might recall this pattern from
    # such web frameworks as Django.
    queues = __import__('queue_front.backends.%s' % BACKEND, {}, {}, [''])
except ImportError as err:
    # If that didn't work, try an external import.
    try:
        queues = __import__(BACKEND, {}, {}, [''])
    except ImportError:
        raise InvalidBackend("Unable to import QUEUE BACKEND '%s'" % BACKEND)
    # Check that this is really a queues backend, not just some other random
    # module.
    if not inspect_isclass(getattr(queues, 'Queue', None)):
        raise InvalidBackend("Unable to import QUEUE BACKEND '%s' does not "
            "appear to be valid." % BACKEND)

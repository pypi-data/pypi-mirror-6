import os
import sys

from kotocore import get_version


# TODO: Assert if this is egg-safe (or if that matters to us)?
KOTOCORE_ROOT = os.path.dirname(os.path.dirname(__file__))

USER_AGENT_NAME = 'kotocore'
USER_AGENT_VERSION = get_version(full=True)

DEFAULT_REGION = 'us-east-1'

DEFAULT_DOCSTRING = """
Please make an instance of this class to inspect the docstring.

No underlying connection is yet available.
"""

DEFAULT_DATA_DIR = os.path.join(KOTOCORE_ROOT, 'data', 'aws')
DEFAULT_RESOURCE_JSON_DIR = os.path.join(DEFAULT_DATA_DIR, 'resources')


class NOTHING_PROVIDED(object):
    """
    An identifier for no data provided.

    Never meant to be instantiated.
    """
    pass


class NO_NAME(object):
    """
    An identifier to indicate a method instance hasn't been given a name.

    Never meant to be instantiated.
    """
    pass


class NO_RESOURCE(object):
    """
    An identifier to indicate a method instance hasn't been attached to a
    resource.

    Never meant to be instantiated.
    """
    pass

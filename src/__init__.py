from ._version import __version__

try:
    from .diftypes import *
    from .dif import *
    from .cli import *

except OSError:
    import logging
    logging.error("Could not load sscDif shared libraries")

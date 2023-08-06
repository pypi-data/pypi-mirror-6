from .base import *

try:
    from .local import *
except ImportError:
    pass

APP_SETTINGS = {'debug': DEBUG, 'static_path': STATIC_ROOT}

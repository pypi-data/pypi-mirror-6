# flake8: noqa
from .app_settings import *
try:
    from .local_settings import *
except ImportError:
    pass

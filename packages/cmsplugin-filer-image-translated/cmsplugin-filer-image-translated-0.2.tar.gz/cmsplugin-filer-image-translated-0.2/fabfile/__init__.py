# flake8: noqa
import os
from cmsplugin_filer_image_translated import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "cmsplugin_filer_image_translated.settings")

from development_fabfile.fabfile import *
from fabfile.local import *

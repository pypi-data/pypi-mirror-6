# flake8: noqa
"""Settings to be used for running tests."""
from . import *


INSTALLED_APPS.append('django_nose')


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


EMAIL_SUBJECT_PREFIX = '[test cmsplugin_filer_image_translated] '
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SOUTH_TESTS_MIGRATE = False


TEST_RUNNER = 'django_libs.testrunner.NoseCoverageTestRunner'
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$', 'wsgi$', 'testrunner$',
    'migrations', '^fixtures$', 'admin$', 'django_extensions', 'debug_toolbar$',
]
COVERAGE_MODULE_EXCLUDES += [appname + '$' for appname in EXTERNAL_APPS]
COVERAGE_MODULE_EXCLUDES += DJANGO_APPS
COVERAGE_REPORT_HTML_OUTPUT_DIR = "coverage"

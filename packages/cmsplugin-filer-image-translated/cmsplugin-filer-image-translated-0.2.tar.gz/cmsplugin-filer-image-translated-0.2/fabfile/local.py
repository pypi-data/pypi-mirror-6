"""Fabric commands that are run locally."""
from fabric.api import local
from development_fabfile.fabfile.local import (
    check_coverage,
    create_db,
    drop_db,
    test as fab_test,
)


def dumpdata():
    """Dumps everything.

    Remember to add new dumpdata commands for new apps here so that you always
    get a full initial dump when running this task.

    """
    local('python2.7 ./manage.py dumpdata --indent 4 --natural auth --exclude auth.permission > cmsplugin_filer_image_translated/fixtures/bootstrap_auth.json')  # NOPEP8
    local('python2.7 ./manage.py dumpdata --indent 4 --natural sites > cmsplugin_filer_image_translated/fixtures/bootstrap_sites.json')  # NOQA
    local('python2.7 ./manage.py dumpdata --indent 4 --natural cms.placeholder > cmsplugin_filer_image_translated/fixtures/bootstrap_cms.json')  # NOQA
    local('python2.7 ./manage.py dumpdata --indent 4 --natural cms --exclude cms.placeholder > cmsplugin_filer_image_translated/fixtures/bootstrap_cms2.json')  # NOQA


def loaddata():
    local('python2.7 manage.py loaddata cmsplugin_filer_image_translated/fixtures/bootstrap_auth.json')  # NOPEP8
    local('python2.7 manage.py loaddata cmsplugin_filer_image_translated/fixtures/bootstrap_sites.json')  # NOPEP8
    local('python2.7 manage.py loaddata cmsplugin_filer_image_translated/fixtures/bootstrap_cms.json')  # NOPEP8
    local('python2.7 manage.py loaddata cmsplugin_filer_image_translated/fixtures/bootstrap_cms2.json')  # NOPEP8


def rebuild():
    """Deletes and re-creates the local database."""
    drop_db()
    create_db()
    local('python2.7 manage.py syncdb --noinput')
    local('python2.7 manage.py migrate ')
    loaddata()


def test(*args, **kwargs):
    fab_test()
    check_coverage()

# encoding: utf-8
from __future__ import absolute_import
from fabric.api import *


@task
def build_docs():
    with lcd('docs'):
        local('rm -rf _build/html/*.html')
        local('source ../.virtualenv-sphinx/bin/activate && make html')


@task
def test():
    local('mypy --silent-import bocco bin')
    local('mypy --silent-import --py2 bocco bin')
    local('python bocco/models.py')


@task
def prepare_for_release():
    local('python setup.py sdist')

@task
def release(server='test', version=None):  # server=(test|pypi)
    if not version:
        version = prompt('Input version')
    local('twine upload -r {} dist/bocco-{}.tar.gz'.format(server, version))

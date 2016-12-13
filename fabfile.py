from fabric.api import *


@task
def build_docs():
    with lcd('docs'):
        local('rm -rf _build/html/*.html')
        local('source ../.virtualenv-sphinx/bin/activate && make html')

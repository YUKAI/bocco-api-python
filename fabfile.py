from fabric.api import *


@task
def build_docs():
    with lcd('docs'):
        local('source ../.virtualenv-sphinx/bin/activate && make html')

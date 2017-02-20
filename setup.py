from setuptools import setup, find_packages
from os import path
from codecs import open
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requirements_txt = parse_requirements(path.join(here, 'requirements.txt'), session='hack')
requires = [str(i.req) for i in requirements_txt]

setup(
    name='bocco',
    version='0.1',
    description='BOCCO API Client',
    long_description=long_description,
    url='https://github.com/YUKAI/bocco-api-python',
    author='wkiryu',
    author_email='kiryu@ux-xu.com',
    packages=['bocco'],
    keywords='bocco',
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requires,
)

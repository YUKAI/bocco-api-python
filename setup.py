from setuptools import setup, find_packages
from os import path
from codecs import open
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bocco',
    version='0.1.3',
    description='BOCCO API Client',
    long_description=long_description,
    url='https://github.com/YUKAI/bocco-api-python',
    author='wkiryu',
    author_email='kiryu@ux-xu.com',
    packages=['bocco'],
    keywords='bocco',
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'arrow>=0.10',
        'click>=6.6',
        'enum34>=1.1.6',
        'Flask>=0.11.1',
        'requests>=2.12.3',
        'schema>=0.6.5',
    ],
)

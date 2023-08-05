#!/usr/bin/env python

# bootstrap setuptools
from ez_setup import use_setuptools
use_setuptools()

# the rest of the imports
import os
from setuptools import setup, find_packages

# so we can put the long description in a README file; see
# http://pythonhosted.org/an_example_pypi_project/setuptools.html
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    # required info
    name='nori',
    version='1.0',
    packages=['nori', 'nori.dbms'],
    package_dir={'nori': ''},
    #py_modules=[],
    #install_requires=[],
    extras_require={
        'MySQL': 'mysql-connector-python',
        'PostgreSQL': 'psycopg2',
    },

    # PyPI metadata
    description=(
        'A library for wrapping scripts, especially ones run from cron.'
    ),
    long_description=read('README'),
    author='Daniel Malament',
    author_email='daniel.j.malament@gmail.com',
    url='http://www.obsessivecompulsivesoftware.com/',
    #download_url='',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Topic :: Database',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
    ],
    #license='',  # only if it's not in the classifiers
    keywords='cron, logging, monitoring, wrapper',
)

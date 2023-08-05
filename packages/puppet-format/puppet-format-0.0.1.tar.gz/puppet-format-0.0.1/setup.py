#!/usr/bin/python

from distutils.core import setup
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.sdist import sdist

setup(
    name='puppet-format',
    version='0.0.1',
    description='Python Puppet Formatter',
    author='Yecheng Fu',
    url='https://github.com/Cofyc/puppet-format',
    packages=['puppet', 'puppet.scanner'],
    entry_points={'console_scripts': ['puppet-format = puppet.format:main'
                  ]},
    )

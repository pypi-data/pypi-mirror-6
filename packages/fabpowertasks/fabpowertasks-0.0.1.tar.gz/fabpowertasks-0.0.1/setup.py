#!/usr/bin/env python
"""
Installation script for the project
"""
import os
from setuptools import setup, find_packages


def get_long_description():
    """
    Returns the long description of the project; either read from the README
    or a default description, if that doesn't exist.
    """
    readme_file_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file_path):
        description = open(readme_file_path).read()
    else:
        description = """Offers an alternative to the standard way of generating
Fabric tasks. Instead
of random functions or Task declarations, instead create Commands classes that
use a simple configuration flow and allow for dependency injection to share
functionality between Tasks.

Additionally, some simple tasks are auto-generated and act as examples of how
to write Commands."""
    return description

setup(
    name='fabpowertasks',
    version='0.0.1',
    author='Shane Breatnach',
    author_email='shane.breatnach@gmail.com',
    description='',
    license='MIT',
    keywords='fabric tool',
    url='http://github.com/sbreatnach/fabpowertasks',
    packages=find_packages(),
    install_requires=[
        "fabric>=1.7.0", 'fabtools>=0.17.0'
    ],
    long_description=get_long_description(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

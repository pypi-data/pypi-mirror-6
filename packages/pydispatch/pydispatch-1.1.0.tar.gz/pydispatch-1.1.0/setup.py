#!/usr/bin/env python
from distutils.core import setup
from os.path import dirname, realpath
from setuptools import find_packages


pip_requirements = 'requirements.txt'


setup(
    # Basic metadata.
    name='pydispatch',
    version=open('VERSION').read().strip(),
    description='Simple Python message dispatcher',
    
    author='Luke Sneeringer',
    author_email='luke@sneeringer.com',
    url='http://github.com/feedmagnet/pydispatch',
    
    # How to do the install
    install_requires=open(pip_requirements, 'r').read().strip().split('\n'),
    provides=[
        'dispatch',
    ],
    packages=[i for i in find_packages() if i.startswith('dispatch')],

    # Data files
    package_data={
        'dispatch': ['VERSION'],
    },

    # PyPI metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
    ],
)

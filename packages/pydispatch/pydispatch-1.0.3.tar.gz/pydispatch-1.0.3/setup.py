#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pydispatch',
    version='1.0.3',
    description='Simple Python message dispatcher',
    
    author='Luke Sneeringer',
    author_email='lukesneeringer@gmail.com',
    url='http://github.com/feedmagnet/pydispatch',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],

    packages=['dispatch'],
)

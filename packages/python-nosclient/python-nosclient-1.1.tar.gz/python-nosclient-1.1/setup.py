#!/usr/bin/python

import setuptools


setuptools.setup(
    name='python-nosclient',
    version='1.1',
    description='Python client for Netease-NOS',
    author='hzyangtk',
    author_email='hzyangtk@corp.netease.com',
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Environment :: No Input/Output (Daemon)',
    ],
    py_modules=[]
)

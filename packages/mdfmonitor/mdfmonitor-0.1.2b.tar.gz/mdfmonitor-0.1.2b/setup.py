#!/usr/bin/env python
#coding: utf-8

from mdfmonitor     import __version__
from distutils.core import setup

setup(
    name="mdfmonitor",
    author="alice1017",
    author_email="genocidedragon@gmail.com",
    version=__version__,
    url="https://github.com/alice1017/watcher",
    description="The mdfmonitor  can monitoring the file modification.",
    py_modules=['mdfmonitor'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities" ]
)


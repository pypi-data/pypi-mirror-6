#!/usr/bin/env python

from distutils.core import setup

setup(
    name='bls',
    version='0.0.5',
    author="Oliver Sherouse",
    author_email="oliver.sherouse@gmail.com",
    py_modules=["bls"],
    url="https://github.com/OliverSherouse/bls",
    description="A library to access Bureau of Labor Statistics data",
    requires=["pandas"],
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)

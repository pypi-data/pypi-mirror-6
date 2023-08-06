#!/usr/bin/env python

"""gflags-multibool
=====================

A Gflags definition suitable for Nagios --verbose style flags 

The nagios monitoring system's parameter convention recommends
multiple invocations of --verbose be used to indicate increasing
levels of verbosity in the emitted output.  This module provides a
method called DEFINE_mutlibool that provides

"""

from setuptools import setup

setup(
    name="gflags-multibool",
    version="0.0.0",
    author="Adam DePrince",
    author_email="adeprince@googlealumni.com",
    description="GFlags multibool",
    long_description=__doc__,
    py_modules = [
        "gflags_multibool",
        ],
    packages = ["gflags_multibool"],
    zip_safe = True,
    include_package_data = True,
    classifiers = [],
    scripts = [
        ],
    install_requires = [
        "python-gflags",
        ],
)

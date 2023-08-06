#!/usr/bin/env python
""" setup.py for multimethods
"""

from distutils.core import setup

setup(
    name         = 'multimethods.py',
    version      = '0.2.2',
    description  = 'updated Clojure-style multimethods for Python',
    author       = 'Jeff Weiss',
    author_email = 'me@jweiss.com',
    license      = 'BSD 2-clause',
    keywords     = 'multimethods dispatch',
    classifiers  = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    url          = 'http://github.com/weissjeffm/multimethods',
    py_modules   = ['multimethods'],

    long_description = "This module adds multimethod support to the Python programming language. \
It has custom dispatch functions, method preference, and module namespacing. This design \
is inspired the Clojure programming language's multimethods.",
)

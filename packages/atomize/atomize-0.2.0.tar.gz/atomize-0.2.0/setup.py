#!/usr/bin/env python

from distutils.core import setup
import sys

# handle python 2 vs 3
if sys.version_info < (3,): # python 2
    sys.path = ["src2"] + sys.path
    package_dir = {"": "src2"}
else:
    sys.path = ["src3"] + sys.path
    package_dir = {"": "src3"}
import atomize

setup(
    name="atomize",
    version="%s.%s.%s" % atomize.__version__,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary'
        ],
    author="Christopher Wienberg",
    author_email="cwienberg@ict.usc.edu",
    url="http://code.google.com/p/atomize/",
    download_url="http://code.google.com/p/atomize/downloads/list",
    description=("A simple Python package for easily generating "
                  "Atom feeds"),
    long_description=("A pure-Python package for easily generating "
                       "Atom Syndicated Format feeds."),
    package_dir=package_dir,
    py_modules=["atomize"],
    provides=["atomize"],
    keywords="atom feed web",
    license="Eclipse Public License 1.0"
)

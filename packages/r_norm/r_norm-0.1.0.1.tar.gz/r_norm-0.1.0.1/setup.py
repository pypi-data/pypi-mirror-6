#!coding:utf-8
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "r_norm",
    version = "0.1.0.1",
    author = "Ruslan Khalikov",
    author_email = "khalikoff@gmail.com",
    description = ("Simple normalization of RTF files - removing unnesessary tags"
                   "that can be produced by document processor program"),
    license = "Apache v2",
    keywords = "RTF",
    url = "http://packages.python.org/r_norm",
    packages=['r_norm', 'tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
    ],
    install_requires=[
        "pyparsing"
    ]
)

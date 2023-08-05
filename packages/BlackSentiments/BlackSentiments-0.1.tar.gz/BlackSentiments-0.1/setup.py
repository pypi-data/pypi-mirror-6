#!/usr/bin/env python
from distutils.core import setup

setup(
    name="BlackSentiments",
    version="0.1",
    author="Stephen B. Murray",
    author_email="sbm199@gmail.com",
    py_modules=["blacksentiments"],
    url="http://pypi.python.org/pypi/BlackSentiments/",
    license="LICENSE.txt",
    description="Fast sentiment analysis for Tolkien's Black Speech of Mordor.",
    long_description=open("README.txt").read(),
)

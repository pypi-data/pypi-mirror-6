#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@pyrosome.org>'

import os
from setuptools import setup, find_packages

dependencies = [ "launchpadlib", "tabulate" ]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="lp-show-my-bugs",
    version="0.0.2",
    author="Jorge Niedbalski R.",
    author_email="jnr@metaklass.org",
    description="",
    install_requires=dependencies,
    include_package_data=True,
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
    license="BSD",
    entry_points={
	'console_scripts' : [
	'lp-show-my-bugs = lp_show_my_bugs.cli:main'
	]
    }
)

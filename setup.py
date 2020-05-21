#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="mephisto",
    version="0.1",
    packages=find_packages(),
    entry_points= {
        'console_scripts': 'mephisto=mephisto.client.cli:cli'
    }
    # package_dir={'': 'mephisto'},
)

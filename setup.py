#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup, find_packages

setup(
    name="mephisto",
    version="0.1",
    packages=find_packages(),
    entry_points={"console_scripts": "mephisto=mephisto.client.cli:cli"}
    # package_dir={'': 'mephisto'},
)

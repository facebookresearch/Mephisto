#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", encoding="utf8") as f:
    # strip the header and badges etc
    readme = f.read()

with open("requirements.txt") as f:
    reqs = f.readlines()
    reqs = [r for r in reqs if "--hash" not in r]
    reqs = [r.split("\\")[0].split(";")[0].strip() for r in reqs]

with open(os.path.join(here, "mephisto", "VERSION")) as version_file:
    version = version_file.read().strip()

setup(
    name="mephisto",
    version=version,
    description="Crowdsourcing made simpler.",
    author="Jack Urbanek, Pratik Ringshia",
    author_email="jju@fb.com",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/facebookresearch/Mephisto",
    python_requires=">=3.7",
    packages=find_packages(include=["mephisto.*", "hydra_plugins.*"]),
    license="MIT",
    install_requires=reqs,
    include_package_data=True,
    package_data={"mephisto": ["*.yaml", "abstractions/**/*"]},
    zip_safe=False,
    entry_points={"console_scripts": "mephisto=mephisto.client.cli:cli"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Natural Language :: English",
    ],
)

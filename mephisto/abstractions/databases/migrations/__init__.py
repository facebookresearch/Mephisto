#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ._001_20240325_data_porter_feature import *
from ._002_20241002_add_qualification_description import *


migrations = {
    "20240418_data_porter_feature": MODIFICATIONS_FOR_DATA_PORTER,
    "20241002_add_qualification_description": ADD_QUALIFICATION_DESCRIPTION,
}

#!/bin/sh

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

set -e

pip install pytest
cd /mephisto
mkdir -p "data" && chmod 777 "data"

mephisto register mturk_sandbox \
    name=$MTURK_SANDBOX_NAME \
    access_key_id=$MTURK_SANDBOX_ACCESS_KEY_ID \
    secret_access_key=$MTURK_SANDBOX_SECRET_ACCESS_KEY

exec "$@"

#!/bin/sh
set -e

pip install pytest
cd /mephisto
mkdir -p "data" && chmod 777 "data"

mephisto register mturk_sandbox \
    name=$MTURK_SANDBOX_NAME \
    access_key_id=$MTURK_SANDBOX_ACCESS_KEY_ID \
    secret_access_key=$MTURK_SANDBOX_SECRET_ACCESS_KEY

exec "$@"

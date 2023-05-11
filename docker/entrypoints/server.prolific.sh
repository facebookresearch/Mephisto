#!/bin/sh
set -e

pip install pytest black
cd /mephisto
mkdir -p "data" && chmod 777 "data"

mephisto register prolific name=prolific api_key=$PROLIFIC_API_KEY

exec "$@"

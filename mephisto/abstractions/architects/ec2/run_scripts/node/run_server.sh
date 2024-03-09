#!/bin/bash

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


cd /home/ec2-user/routing_server/router/
. ~/.nvm/nvm.sh
PORT=5000 node server.js

#!/bin/bash

cd /home/ec2-user/routing_server/router/
. ~/.nvm/nvm.sh
PORT=5000 node server.js

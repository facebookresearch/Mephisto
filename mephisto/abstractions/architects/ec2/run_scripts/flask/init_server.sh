#!/bin/bash

sudo yum update -y
sudo yum install -y httpd

sudo -H pip3 install flask gevent

sudo cp /home/ec2-user/routing_server/setup/router.service /etc/systemd/system/router.service
sudo chmod 744 /home/ec2-user/routing_server/setup/run_server.sh
sudo chmod 664 /etc/systemd/system/router.service

sudo systemctl daemon-reload
sudo systemctl enable router.service
sudo systemctl start router.service

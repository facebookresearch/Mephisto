#!/bin/bash

echo "Installing basic requirements..."
sudo yum update -y >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1
sudo yum install -y httpd >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1

echo "Downloading Node..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1
. ~/.nvm/nvm.sh >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1
nvm install node >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1

echo "Installing router modules..."
cd /home/ec2-user/routing_server/router/
npm install >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1

echo "Preparing service..."
sudo cp /home/ec2-user/routing_server/setup/router.service /etc/systemd/system/router.service
sudo chmod 744 /home/ec2-user/routing_server/setup/run_server.sh
sudo chmod 664 /etc/systemd/system/router.service

echo "Launching service..."
sudo systemctl daemon-reload >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1
sudo systemctl enable router.service >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1
sudo systemctl start router.service >> /home/ec2-user/routing_server/setup/setup_log.txt 2>&1

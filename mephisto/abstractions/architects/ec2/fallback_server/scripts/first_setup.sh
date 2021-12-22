echo "Installing requirements"
sudo yum update -y >> /home/ec2-user/setup_log.txt 2>&1
sudo yum install -y httpd >> /home/ec2-user/setup_log.txt 2>&1

sudo -H pip3 install flask gevent >> /home/ec2-user/setup_log.txt 2>&1

echo "Preparing service..."
sudo cp /home/ec2-user/fallback_server/fallback.service /etc/systemd/system/fallback.service >> /home/ec2-user/setup_log.txt 2>&1
sudo chmod 744 /home/ec2-user/fallback_server/scripts/run_server.sh >> /home/ec2-user/setup_log.txt 2>&1
sudo chmod 664 /etc/systemd/system/fallback.service >> /home/ec2-user/setup_log.txt 2>&1

echo "Launching service..."
sudo systemctl daemon-reload >> /home/ec2-user/setup_log.txt 2>&1
sudo systemctl enable fallback.service >> /home/ec2-user/setup_log.txt 2>&1
sudo systemctl start fallback.service >> /home/ec2-user/setup_log.txt 2>&1

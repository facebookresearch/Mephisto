sudo yum update -y
sudo yum install -y httpd

sudo -H pip3 install flask gevent

sudo cp /home/ec2-user/fallback_server/fallback.service /etc/systemd/system/fallback.service
sudo chmod 744 /home/ec2-user/fallback_server/scripts/run_server.sh
sudo chmod 664 /etc/systemd/system/fallback.service

sudo systemctl daemon-reload
sudo systemctl enable fallback.service
sudo systemctl start fallback.service

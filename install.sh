#!/usr/bin/bash
sudo chmod +x fanctl
sudo chmod +x fan_control_script
echo Moving Fan Script to /usr/bin/
sudo mv fan_control_script /usr/bin/
echo Moving Fan Control Utility to /usr/bin/
sudo mv fanctl /usr/bin/
echo Moving Fan Systemd Service to /etc/systemd/system/
sudo mv fan_control.service /etc/systemd/system/
echo starting service and enabling service
sudo systemctl start fan_control.service
sudo systemctl enable fan_control.service
echo Done!

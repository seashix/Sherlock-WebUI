#!/bin/bash

# Update the system and install Python3 and pip
echo "System update and dependency installation..."
sudo apt update
sudo apt install -y python3 python3-pip git

# Clone the Sherlock repository
echo "Cloning the Sherlock repository..."
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock

# Installing Python dependencies for Sherlock
echo "Installation of Sherlock's outbuildings..."
pip3 install -r requirements.txt

# Return to parent directory
cd ..

# Installing Flask
echo "Installing Flask..."
pip3 install flask flask-socketio

echo "Configuration complete. To start the Flask server, run: python3 app.py"

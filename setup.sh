#!/bin/bash

# Check for sudo privileges (disabled for PythonAnywhere)
if [ "$EUID" -ne 0 ]; then
    echo "Note : This script may require sudo for global package installation."
fi

# Update the system (if authorized)
if command -v apt &>/dev/null; then
    echo "Updating the system and installing dependencies..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv git
fi  

# Create a Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating a Python virtual environment...."
    python3 -m venv venv
else
    echo "The Python virtual environment already exists."
fi

# Activate virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Installing Sherlock dependencies
echo "Installation of Sherlock & dependencies..."
pip install --upgrade pip
pip install pipx
pipx install sherlock-project

# Installing Flask and Flask-SocketIO
echo "Installing Flask and Flask-SocketIO..."
pip install flask flask-socketio eventlet python-dotenv


# Create a Flask configuration file
echo "Creating a .flaskenv file..."
cat <<EOL > .flaskenv
FLASK_APP=app.py
FLASK_ENV=production
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
EOL

# Deactivate the virtual environment
deactivate

echo "Setup complete. To start the Flask server, run: source venv/bin/activate && python app.py (or flask run)"

echo "Configuration complete. To start the Flask server, use the following commands:"
echo "source venv/bin/activate"
echo "python app.py"

# Instructions for PythonAnywhere
if [[ "$HOSTNAME" == *"pythonanywhere"* ]]; then
    echo "You're on PythonAnywhere. Configure your web application to point to 'app.py' and enable the virtual environment in the settings."
fi

# Instructions for Digital Ocean
if [[ "$HOSTNAME" == *"do"* ]]; then
    echo "You're on Digital Ocean. Configure your web application to point to 'app.py' and enable the virtual environment in the settings."
fi

# Instructions for Google Cloud
if [[ "$HOSTNAME" == *"google"* ]]; then
    echo "You're on Google Cloud. Configure your web application to point to 'app.py' and enable the virtual environment in the settings."
fi

#!/bin/bash

echo "🐧 Setting up Sherlock WebUI on Linux..."

# Detect environment
CLOUD_PROVIDER=""
if [[ "$HOSTNAME" == *"pythonanywhere"* ]]; then
    CLOUD_PROVIDER="PythonAnywhere"
elif [[ "$HOSTNAME" == *"do"* ]]; then
    CLOUD_PROVIDER="Digital Ocean"
elif [[ "$HOSTNAME" == *"google"* ]]; then
    CLOUD_PROVIDER="Google Cloud"
elif [[ "$HOSTNAME" == *"aws"* ]]; then
    CLOUD_PROVIDER="AWS"
fi

echo "🌐 Detected environment: ${CLOUD_PROVIDER:-Local Machine}"

# Update system (if using apt)
if command -v apt &>/dev/null; then
    echo "📦 Updating the system and installing dependencies..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv git
fi  

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install dependencies from requirements.txt
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Ensure output directory exists
mkdir -p sherlock_output

# Create .flaskenv file
echo "⚙️ Creating a .flaskenv file..."
cat <<EOL > .flaskenv
FLASK_APP=app.py
FLASK_ENV=production
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
EOL

# Deactivate virtual environment
deactivate

echo "✅ Setup complete! To start the Flask server, run:"
echo "source venv/bin/activate && python app.py"

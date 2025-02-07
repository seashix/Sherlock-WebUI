#!/bin/bash

echo "🍏 Setting up Sherlock WebUI on macOS..."

# Check if Homebrew is installed
if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew is not installed. Please install it from https://brew.sh and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python, Git, and Pipx..."
brew install python git pipx

# Ensure Pipx is in PATH
export PATH="$HOME/.local/bin:$PATH"
pipx ensurepath

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

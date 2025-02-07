@echo off
echo 🔍 Setting up Sherlock WebUI on Windows...
echo.

:: Check for Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3 and try again.
    exit /b
)

:: Create virtual environment
if not exist "venv" (
    echo 🐍 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists.
)

:: Activate virtual environment
echo 🚀 Activating virtual environment...
call venv\Scripts\activate

:: Install dependencies from requirements.txt
echo 📦 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

:: Ensure output directory exists
if not exist "sherlock_output" mkdir sherlock_output

:: Create .flaskenv file
echo ⚙️ Configuring Flask...
(
    echo FLASK_APP=app.py
    echo FLASK_ENV=production
    echo FLASK_RUN_HOST=127.0.0.1
    echo FLASK_RUN_PORT=5000
) > .flaskenv

:: Deactivate virtual environment
deactivate

echo ✅ Setup complete!
echo To start the server, run:
echo call venv\Scripts\activate && python app.py

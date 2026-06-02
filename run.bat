@echo off
echo =========================================
echo Traffic Flow Simulation Startup Script
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo Python found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Traffic Simulation Server...
echo.
echo Once the server starts, open your browser to:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo =========================================
echo.

REM Run the application
python traffic_simulation.py

pause

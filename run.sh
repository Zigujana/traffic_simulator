#!/bin/bash

echo "========================================="
echo "Traffic Flow Simulation Startup Script"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt

echo ""
echo "🚀 Starting Traffic Simulation Server..."
echo ""
echo "Once the server starts, open your browser to:"
echo "👉 http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

# Run the application
python3 traffic_simulation.py

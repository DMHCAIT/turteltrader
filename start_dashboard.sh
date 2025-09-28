#!/bin/bash

# Turtle Trading Dashboard Startup Script
# Use this to start the dashboard with proper configuration

echo "🐢 Starting Turtle Trading Dashboard..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📋 Installing requirements..."
pip install -r requirements.txt

# Check if config.ini exists
if [ ! -f "config.ini" ]; then
    echo "⚙️ Creating config.ini from template..."
    cp config_template.ini config.ini
    echo "⚠️  Please update config.ini with your API credentials before running!"
    exit 1
fi

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo "📄 Creating logs directory..."
    mkdir -p logs
fi

# Start the dashboard
echo "🚀 Starting Streamlit dashboard..."
echo "📱 Dashboard will be available at: http://localhost:8052"
echo "🔐 Access Token Manager: Go to 'Access Token Manager' tab in the dashboard"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

streamlit run trading_dashboard.py --server.port 8052

echo "👋 Dashboard stopped."
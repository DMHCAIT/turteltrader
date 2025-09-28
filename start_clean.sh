#!/bin/bash

# 🐢 TURTLE TRADER - CLEAN STARTUP SCRIPT
# =====================================
# Production-ready startup - Real data only

echo "🐢 TURTLE TRADER - PRODUCTION STARTUP"
echo "====================================="
echo "⚡ Real data only - No demo mode"
echo "🔥 Live Kite API connection required"
echo ""

# Check if we're in the right directory
if [ ! -f "trading_dashboard.py" ]; then
    echo "❌ Error: Please run this script from the Turtle Trader directory"
    exit 1
fi

# Check config file
if [ ! -f "config.ini" ]; then
    echo "❌ Error: config.ini not found"
    echo "💡 Copy config_template.ini to config.ini and add your API credentials"
    exit 1
fi

# Check for API credentials
if ! grep -q "api_key.*=" config.ini || ! grep -q "access_token.*=" config.ini; then
    echo "⚠️  Warning: API credentials may not be configured"
    echo "💡 Make sure config.ini has your Kite API credentials"
    echo ""
fi

# Activate virtual environment if available
if [ -d "turtle_env" ]; then
    echo "🐍 Activating Python environment..."
    source turtle_env/bin/activate
elif [ -d "venv" ]; then
    echo "🐍 Activating Python environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found - using system Python"
fi

# Check if streamlit is available
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: Streamlit not found"
    echo "💡 Install requirements: pip install -r requirements.txt"
    exit 1
fi

# Kill any existing streamlit processes
echo "🧹 Cleaning up existing processes..."
pkill -f streamlit 2>/dev/null || true
sleep 2

# Start the dashboard
echo "🚀 Starting Turtle Trader Dashboard..."
echo "📍 URL: http://localhost:8052"
echo "🔴 LIVE TRADING MODE - Real money at risk"
echo ""

# Start Streamlit
streamlit run trading_dashboard.py --server.port 8052 --browser.gatherUsageStats false

echo ""
echo "👋 Turtle Trader stopped"
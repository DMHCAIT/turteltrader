#!/bin/bash

# 🐢 Turtle Trader Dashboard Launcher
# Activates virtual environment and starts the dashboard

echo "🐢 Starting Turtle Trader Dashboard..."

# Change to project directory
cd "/Users/rubeenakhan/Downloads/Turtel trader"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source turtle_env/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Launching dashboard on http://localhost:8501"
echo "💡 Use Ctrl+C to stop the dashboard"

# Start the dashboard
streamlit run app.py --server.port 8501 --server.headless true
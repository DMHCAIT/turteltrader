#!/bin/bash

# 🐢 DAILY TURTLE TRADER LAUNCHER
# Simple script to start trading system every day

echo "🌅 Good morning! Starting Turtle Trader for $(date '+%A, %B %d, %Y')"
echo "⏰ Market hours: 9:15 AM - 3:30 PM IST"

# Navigate to project
cd "/Users/rubeenakhan/Downloads/Turtel trader"

# Activate environment
echo "📦 Activating trading environment..."
source turtle_env/bin/activate

# Quick system check
echo "🔍 Quick system check..."
python3 -c "
import sys
print(f'✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
try:
    import streamlit, pandas, requests
    print('✅ Core modules ready')
except ImportError as e:
    print(f'❌ Missing module: {e}')
    exit(1)
"

echo ""
echo "🎯 TRADING DASHBOARD STARTING..."
echo "💻 Dashboard URL: http://localhost:8501" 
echo "📱 Mobile friendly interface"
echo "🛡️  Starts in DEMO mode (safe)"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo "=" * 50

# Launch dashboard
streamlit run app.py --server.port 8501 --server.headless false

echo ""
echo "👋 Turtle Trader session ended. Have a great day!"
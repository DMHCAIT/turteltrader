#!/bin/bash

# 🚀 TURTLE TRADER - PERFORMANCE OPTIMIZED LAUNCHER
# Enhanced startup with watchdog and performance optimizations

echo "🐢 TURTLE TRADER - HIGH PERFORMANCE MODE"
echo "=========================================="
echo "⏰ $(date '+%A, %B %d, %Y - %I:%M %p')"

# Navigate to project
cd "/Users/rubeenakhan/Downloads/Turtel trader"

# Activate environment
echo "📦 Activating trading environment..."
source turtle_env/bin/activate

# Performance check
echo "🔍 Performance optimization check..."

# Check if watchdog is installed
if python3 -c "import watchdog" 2>/dev/null; then
    echo "✅ Watchdog installed - File monitoring optimized"
else
    echo "⚡ Installing watchdog for better performance..."
    pip install watchdog
fi

# Check Xcode tools
if xcode-select -p >/dev/null 2>&1; then
    echo "✅ Xcode command line tools available"
else
    echo "⚠️  Consider installing: xcode-select --install"
fi

# System info
echo ""
echo "🖥️  System Information:"
echo "   • Python: $(python3 --version | cut -d' ' -f2)"
echo "   • Streamlit: $(python3 -c 'import streamlit; print(streamlit.__version__)')"
echo "   • CPU Cores: $(sysctl -n hw.ncpu)"
echo "   • Memory: $(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)"GB"}')"

echo ""
echo "🎯 LAUNCHING HIGH-PERFORMANCE DASHBOARD..."
echo "💻 Dashboard URL: http://localhost:8503"
echo "📱 Mobile optimized interface"
echo "⚡ File watching enabled (auto-reload)"
echo "🛡️  Starting in DEMO mode (safe)"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo "=" * 50

# Launch with performance optimizations
streamlit run app.py \
    --server.port 8503 \
    --server.headless false \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false \
    --global.developmentMode false

echo ""
echo "👋 Turtle Trader session ended."
echo "📊 Check logs for any issues."
echo "🔄 To restart: ./start_optimized.sh"
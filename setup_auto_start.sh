#!/bin/bash

# 🕐 SCHEDULE DAILY AUTO-START (Optional)
# Creates a LaunchAgent for automatic daily startup

PLIST_PATH="$HOME/Library/LaunchAgents/com.turtletrader.daily.plist"
PROJECT_PATH="/Users/rubeenakhan/Downloads/Turtel trader"

# Create LaunchAgent plist
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.turtletrader.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$PROJECT_PATH/start_daily.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>00</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$HOME/turtle_trader_startup.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/turtle_trader_startup.log</string>
</dict>
</plist>
EOF

echo "✅ Auto-startup scheduled for 9:00 AM daily"
echo "📋 To enable: launchctl load $PLIST_PATH"
echo "🛑 To disable: launchctl unload $PLIST_PATH"
echo "📄 Log file: $HOME/turtle_trader_startup.log"
echo ""
echo "⚠️  NOTE: This will auto-start the server daily at 9 AM"
echo "   You still need to open browser to http://localhost:8501"
#!/bin/bash

# Create desktop shortcut for Turtle Trader
# Run this once to create a desktop icon

DESKTOP_PATH="$HOME/Desktop"
SHORTCUT_NAME="🐢 Turtle Trader"
PROJECT_PATH="/Users/rubeenakhan/Downloads/Turtel trader"

# Create the .command file (executable on macOS)
cat > "$DESKTOP_PATH/$SHORTCUT_NAME.command" << 'EOF'
#!/bin/bash
cd "/Users/rubeenakhan/Downloads/Turtel trader"
source turtle_env/bin/activate
echo "🐢 Starting Turtle Trader Dashboard..."
streamlit run app.py --server.port 8501
EOF

# Make it executable
chmod +x "$DESKTOP_PATH/$SHORTCUT_NAME.command"

echo "✅ Desktop shortcut created: $DESKTOP_PATH/$SHORTCUT_NAME.command"
echo "🖱️  Double-click the desktop icon to start trading!"
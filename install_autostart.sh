#!/bin/bash
# FireCorners Auto-start Installer
# This script helps set up FireCorners to start automatically at login

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# If we're in the app bundle, get the scripts directory
if [[ "$SCRIPT_DIR" == *"FireCorners.app/Contents/Resources/scripts" ]]; then
    RUN_SCRIPT="$SCRIPT_DIR/run_firecorners.sh"
else
    RUN_SCRIPT="$SCRIPT_DIR/run_firecorners.sh"
fi

# Create logs directory
mkdir -p ~/Library/Logs/FireCorners

# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Path for the plist file
PLIST_PATH=~/Library/LaunchAgents/com.firecorners.app.plist

# Check if we're uninstalling
if [ "$1" == "uninstall" ]; then
    echo "Uninstalling FireCorners auto-start..."
    
    # Unload the launch agent if it exists
    if [ -f "$PLIST_PATH" ]; then
        launchctl unload "$PLIST_PATH"
        rm "$PLIST_PATH"
        echo "✅ FireCorners auto-start has been removed."
    else
        echo "❌ FireCorners auto-start is not installed."
    fi
    
    exit 0
fi

# Check if the script exists and is executable
if [ ! -x "$RUN_SCRIPT" ]; then
    echo "❌ Error: $RUN_SCRIPT is not executable."
    echo "Run 'chmod +x $RUN_SCRIPT' first."
    exit 1
fi

# Parse command line arguments for custom settings
THRESHOLD="5"
COOLDOWN="3.0"
DWELL="0.5"
NO_TEST=""
CONFIG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --threshold=*)
      THRESHOLD="${1#*=}"
      shift
      ;;
    --cooldown=*)
      COOLDOWN="${1#*=}"
      shift
      ;;
    --dwell=*)
      DWELL="${1#*=}"
      shift
      ;;
    --no-test)
      NO_TEST="--no-test"
      shift
      ;;
    --config=*)
      CONFIG="${1}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./install_autostart.sh [--threshold=N] [--cooldown=N.N] [--dwell=N.N] [--no-test] [--config=PATH]"
      exit 1
      ;;
  esac
done

# Create the plist file
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.firecorners.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>$RUN_SCRIPT</string>
EOF

# Add command line arguments if specified
if [ "$THRESHOLD" != "5" ]; then
    echo "        <string>--threshold=$THRESHOLD</string>" >> "$PLIST_PATH"
fi

if [ "$COOLDOWN" != "3.0" ]; then
    echo "        <string>--cooldown=$COOLDOWN</string>" >> "$PLIST_PATH"
fi

if [ "$DWELL" != "0.5" ]; then
    echo "        <string>--dwell=$DWELL</string>" >> "$PLIST_PATH"
fi

if [ -n "$NO_TEST" ]; then
    echo "        <string>--no-test</string>" >> "$PLIST_PATH"
fi

if [ -n "$CONFIG" ]; then
    echo "        <string>$CONFIG</string>" >> "$PLIST_PATH"
fi

# Complete the plist file
cat >> "$PLIST_PATH" << EOF
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>~/Library/Logs/FireCorners/firecorners.log</string>
    <key>StandardErrorPath</key>
    <string>~/Library/Logs/FireCorners/firecorners.error.log</string>
</dict>
</plist>
EOF

# Unload existing launch agent if it exists
if launchctl list | grep -q "com.firecorners.app"; then
    echo "Unloading existing FireCorners auto-start..."
    launchctl unload "$PLIST_PATH" 2>/dev/null
fi

# Load the launch agent
echo "Loading FireCorners auto-start..."
launchctl load "$PLIST_PATH"

# Check if it was loaded successfully
if launchctl list | grep -q "com.firecorners.app"; then
    echo "✅ FireCorners auto-start has been installed successfully."
else
    echo "❌ Error: Failed to install FireCorners auto-start."
    exit 1
fi 
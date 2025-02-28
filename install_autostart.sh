#!/bin/bash
# FireCorners Auto-start Installer
# This script helps set up FireCorners to start automatically at login

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FIRECORNERS_PATH="$SCRIPT_DIR/run_firecorners.sh"

# Create logs directory
mkdir -p ~/Library/Logs/FireCorners

# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Path for the plist file
PLIST_PATH=~/Library/LaunchAgents/com.user.firecorners.plist

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
if [ ! -x "$FIRECORNERS_PATH" ]; then
    echo "❌ Error: $FIRECORNERS_PATH is not executable."
    echo "Run 'chmod +x $FIRECORNERS_PATH' first."
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
    <string>com.user.firecorners</string>
    <key>ProgramArguments</key>
    <array>
        <string>$FIRECORNERS_PATH</string>
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
if launchctl list | grep -q "com.user.firecorners"; then
    echo "Unloading existing FireCorners auto-start..."
    launchctl unload "$PLIST_PATH" 2>/dev/null
fi

# Load the launch agent
echo "Loading FireCorners auto-start..."
launchctl load "$PLIST_PATH"

# Check if it was loaded successfully
if launchctl list | grep -q "com.user.firecorners"; then
    echo "✅ FireCorners auto-start has been installed successfully!"
    echo "Settings:"
    echo "  Threshold: $THRESHOLD pixels"
    echo "  Cooldown: $COOLDOWN seconds"
    echo "  Dwell time: $DWELL seconds"
    if [ -n "$NO_TEST" ]; then
        echo "  Action tests disabled"
    fi
    if [ -n "$CONFIG" ]; then
        echo "  Custom config: ${CONFIG#*=}"
    fi
    echo ""
    echo "FireCorners will now start automatically when you log in."
    echo "Logs will be written to: ~/Library/Logs/FireCorners/"
    echo ""
    echo "To uninstall, run: ./install_autostart.sh uninstall"
else
    echo "❌ Failed to install FireCorners auto-start."
    echo "Please check the error messages above."
fi 
#!/bin/bash
# FireCorners Launcher
# This script launches the FireCorners daemon with custom settings

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# If we're in the app bundle, get the main executable
if [[ "$SCRIPT_DIR" == *"FireCorners.app/Contents/Resources/scripts" ]]; then
    FIRECORNERS_BIN="$SCRIPT_DIR/../../MacOS/FireCorners"
else
    FIRECORNERS_BIN="$SCRIPT_DIR/FireCorners"
fi

# Default settings
THRESHOLD=5
COOLDOWN=3.0
DWELL=0.5
NO_TEST=""
CONFIG=""

# Parse command line arguments
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
      CONFIG="--config=${1#*=}"
      shift
      ;;
    --configure)
      # Launch the configuration UI
      "$FIRECORNERS_BIN" --configure
      exit 0
      ;;
    --help)
      echo "FireCorners Launcher"
      echo "Usage: ./run_firecorners.sh [options]"
      echo ""
      echo "Options:"
      echo "  --threshold=N    Pixels from edge to trigger corner (default: 5)"
      echo "  --cooldown=N.N   Seconds between triggers (default: 3.0)"
      echo "  --dwell=N.N      Seconds mouse must stay in corner (default: 0.5)"
      echo "  --no-test        Skip testing actions on startup"
      echo "  --config=PATH    Path to custom config file"
      echo "  --configure      Launch the configuration UI"
      echo "  --help           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Print settings
echo "Starting FireCorners with settings:"
echo "  Threshold: $THRESHOLD pixels"
echo "  Cooldown: $COOLDOWN seconds"
echo "  Dwell time: $DWELL seconds"
if [ -n "$NO_TEST" ]; then
  echo "  Skipping action tests"
fi
if [ -n "$CONFIG" ]; then
  echo "  Using custom config: ${CONFIG#*=}"
fi

# Run the daemon
"$FIRECORNERS_BIN" --threshold=$THRESHOLD --cooldown=$COOLDOWN --dwell=$DWELL $NO_TEST $CONFIG 
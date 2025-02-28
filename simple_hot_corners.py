#!/usr/bin/env python3
"""
FireCorners Daemon

A lightweight hot corners daemon that detects when your mouse cursor reaches
the corners of your screen and triggers configured actions.

Usage:
  python3 simple_hot_corners.py [--threshold=5] [--cooldown=3.0] [--dwell=0.5] [--no-test]
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path

try:
    import Quartz
    from AppKit import NSWorkspace, NSURL
except ImportError:
    print("Installing required dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyobjc"], check=True)
    import Quartz
    from AppKit import NSWorkspace, NSURL

# Constants
DEFAULT_CORNER_THRESHOLD = 5  # pixels from edge to trigger corner
DEFAULT_CORNER_COOLDOWN = 3.0  # seconds between triggers
DEFAULT_DWELL_TIME = 0.5  # seconds mouse must stay in corner before triggering

def get_config_path():
    """Get the path to the config file, considering both package and user locations"""
    # First, check if there's a config in the user's home directory
    user_config = Path.home() / ".firecorners" / "config.json"
    if user_config.exists():
        return user_config
    
    # Next, check if there's a config in the current directory
    local_config = Path("config.json")
    if local_config.exists():
        return local_config
    
    # Finally, use the package config
    package_dir = Path(__file__).parent
    return package_dir / "config.json"

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="FireCorners - Hot Corners for macOS")
    parser.add_argument("--threshold", type=int, default=DEFAULT_CORNER_THRESHOLD,
                        help=f"Pixels from edge to trigger corner (default: {DEFAULT_CORNER_THRESHOLD})")
    parser.add_argument("--cooldown", type=float, default=DEFAULT_CORNER_COOLDOWN,
                        help=f"Seconds between triggers (default: {DEFAULT_CORNER_COOLDOWN})")
    parser.add_argument("--dwell", type=float, default=DEFAULT_DWELL_TIME,
                        help=f"Seconds mouse must stay in corner (default: {DEFAULT_DWELL_TIME})")
    parser.add_argument("--no-test", action="store_true",
                        help="Skip testing actions on startup")
    parser.add_argument("--config", type=str,
                        help="Path to custom config file")
    return parser.parse_args()

def load_config(config_path=None):
    """Load configuration from file"""
    default_config = {
        "top_left": [],
        "top_right": [],
        "bottom_left": [],
        "bottom_right": []
    }
    
    if config_path is None:
        config_path = get_config_path()
    
    try:
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Config file not found at {config_path}")
            print(f"Using default configuration")
            return default_config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return default_config

def get_mouse_position():
    """Get the current mouse position using Quartz"""
    mouse_loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    return (mouse_loc.x, mouse_loc.y)

def get_screen_dimensions():
    """Get the screen dimensions using Quartz"""
    main_display = Quartz.CGMainDisplayID()
    width = Quartz.CGDisplayPixelsWide(main_display)
    height = Quartz.CGDisplayPixelsHigh(main_display)
    return (width, height)

def is_in_corner(x, y, screen_width, screen_height, threshold):
    """Check if the mouse is in a corner and return which one"""
    # Check each corner
    if x <= threshold and y >= screen_height - threshold:
        return "bottom_left"  # Bottom left (macOS coordinates)
    elif x <= threshold and y <= threshold:
        return "top_left"  # Top left (macOS coordinates)
    elif x >= screen_width - threshold and y >= screen_height - threshold:
        return "bottom_right"  # Bottom right (macOS coordinates)
    elif x >= screen_width - threshold and y <= threshold:
        return "top_right"  # Top right (macOS coordinates)
    
    return None

def execute_action(action):
    """Execute a configured action"""
    action_type = action.get("type")
    value = action.get("value")
    
    if not value:
        return
    
    try:
        print(f"Executing action: {action_type} - {value}")
        
        if action_type == "app":
            # Use os.system directly
            app_path = value
            if not app_path.startswith("/"):
                app_path = f"/Applications/{app_path}.app"
            cmd = f"open '{app_path}'"
            print(f"Running command: {cmd}")
            os.system(cmd)
        
        elif action_type == "url":
            # Use os.system directly
            cmd = f"open '{value}'"
            print(f"Running command: {cmd}")
            os.system(cmd)
        
        elif action_type == "script":
            # Run AppleScript
            if value.endswith(".scpt") or value.endswith(".applescript"):
                cmd = f"osascript '{value}'"
            else:
                cmd = f"osascript -e '{value}'"
            print(f"Running command: {cmd}")
            os.system(cmd)
        
        elif action_type == "shell":
            # Run shell command
            print(f"Running command: {value}")
            os.system(value)
        
        print(f"Action executed successfully")
        
    except Exception as e:
        print(f"Error executing action: {e}")

def execute_corner_actions(corner, config):
    """Execute all actions for a specific corner"""
    if corner not in config:
        return
    
    actions = config[corner]
    if isinstance(actions, list):
        for action in actions:
            execute_action(action)
    else:
        execute_action(actions)

def test_actions(config):
    """Test all configured actions"""
    print("\n=== Testing Actions ===")
    
    for corner, actions in config.items():
        if not actions:
            continue
        
        print(f"\nTesting {corner} actions:")
        if isinstance(actions, list):
            for action in actions:
                print(f"Testing action: {action}")
                execute_action(action)
                time.sleep(1)  # Wait a bit between actions
        else:
            print(f"Testing action: {actions}")
            execute_action(actions)
            time.sleep(1)
    
    print("\n=== Testing Complete ===\n")

def show_corner_indicator(corner):
    """Show a visual indicator for the detected corner"""
    # Create a simple notification using AppleScript
    corner_name = corner.replace("_", " ").title()
    script = f'''
    display notification "Corner Detected: {corner_name}" with title "FireCorners" subtitle "Action Triggered"
    '''
    os.system(f"osascript -e '{script}'")

def main():
    """Main function"""
    # Parse command line arguments
    args = parse_args()
    
    # Set constants from arguments
    CORNER_THRESHOLD = args.threshold
    CORNER_COOLDOWN = args.cooldown
    DWELL_TIME = args.dwell
    
    print(f"Starting FireCorners Daemon with settings:")
    print(f"  Corner threshold: {CORNER_THRESHOLD} pixels")
    print(f"  Cooldown period: {CORNER_COOLDOWN} seconds")
    print(f"  Dwell time: {DWELL_TIME} seconds")
    
    # Load configuration
    config = load_config(args.config if args.config else None)
    
    # Print loaded configuration
    print("Loaded configuration:")
    for corner, actions in config.items():
        if actions:
            if isinstance(actions, list):
                print(f"  {corner}: {len(actions)} action(s)")
            else:
                print(f"  {corner}: 1 action")
    
    # Test actions first (unless --no-test is specified)
    if not args.no_test:
        test_actions(config)
    
    # Get screen dimensions
    screen_width, screen_height = get_screen_dimensions()
    print(f"Screen dimensions: {screen_width}x{screen_height}")
    
    # Initialize variables
    last_corner = None
    last_trigger_time = 0
    corner_enter_time = 0
    
    print("Hot Corners daemon started")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            # Get mouse position
            x, y = get_mouse_position()
            
            # Check if in a corner
            corner = is_in_corner(x, y, screen_width, screen_height, CORNER_THRESHOLD)
            current_time = time.time()
            
            # If in a corner
            if corner:
                # If it's a new corner or we've reset after leaving corners
                if corner != last_corner:
                    corner_enter_time = current_time
                    last_corner = corner
                # If we've been in this corner long enough and cooldown has passed
                elif (current_time - corner_enter_time >= DWELL_TIME and 
                      current_time - last_trigger_time > CORNER_COOLDOWN):
                    print(f"Corner detected: {corner} at position ({x}, {y})")
                    print(f"Dwell time: {current_time - corner_enter_time:.2f} seconds")
                    
                    # Show visual indicator
                    show_corner_indicator(corner)
                    
                    # Execute actions for this corner
                    execute_corner_actions(corner, config)
                    print(f"Actions executed for {corner}")
                    
                    # Update last trigger time
                    last_trigger_time = current_time
            # If not in a corner, reset last corner
            else:
                last_corner = None
            
            # Sleep to reduce CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nExiting FireCorners daemon")
        sys.exit(0)

if __name__ == "__main__":
    main() 
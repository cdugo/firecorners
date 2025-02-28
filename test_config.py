#!/usr/bin/env python3
"""
FireCorners Configuration Tester

This script tests the configuration file and verifies that all actions are properly configured.
It will attempt to execute each action to ensure they work as expected.
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path

def load_config():
    """Load the configuration file."""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("❌ Error: config.json not found.")
        print("Please create a configuration file first.")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        print("❌ Error: config.json is not valid JSON.")
        print("Please check the file format.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)

def validate_config(config):
    """Validate the configuration file structure."""
    valid_corners = ["top_left", "top_right", "bottom_left", "bottom_right"]
    valid_types = ["app", "url", "shell", "script"]
    
    errors = []
    
    for corner in valid_corners:
        if corner not in config:
            print(f"⚠️ Warning: '{corner}' is not configured.")
            continue
        
        actions = config[corner]
        
        # Handle both list and dictionary formats
        if isinstance(actions, list):
            if not actions:
                print(f"⚠️ Warning: '{corner}' has an empty action list.")
                continue
                
            for i, action in enumerate(actions):
                if not isinstance(action, dict):
                    errors.append(f"'{corner}' action {i} should be an object with 'type' and 'value' properties.")
                    continue
                    
                if "type" not in action:
                    errors.append(f"'{corner}' action {i} is missing the 'type' property.")
                elif action["type"] not in valid_types:
                    errors.append(f"'{corner}' action {i} has invalid type '{action['type']}'. Valid types are: {', '.join(valid_types)}")
                    
                if "value" not in action:
                    errors.append(f"'{corner}' action {i} is missing the 'value' property.")
                elif not action["value"]:
                    errors.append(f"'{corner}' action {i} has an empty 'value'.")
        
        elif isinstance(actions, dict):
            if "type" not in actions:
                errors.append(f"'{corner}' is missing the 'type' property.")
            elif actions["type"] not in valid_types:
                errors.append(f"'{corner}' has invalid type '{actions['type']}'. Valid types are: {', '.join(valid_types)}")
                
            if "value" not in actions:
                errors.append(f"'{corner}' is missing the 'value' property.")
            elif not actions["value"]:
                errors.append(f"'{corner}' has an empty 'value'.")
        
        else:
            errors.append(f"'{corner}' should be an object with 'type' and 'value' properties or a list of such objects.")
    
    if errors:
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def test_action(corner, action):
    """Test an action to see if it works."""
    action_type = action["type"]
    value = action["value"]
    
    print(f"\nTesting {corner} ({action_type}): {value}")
    
    try:
        if action_type == "app":
            if not os.path.exists(value):
                print(f"❌ App not found: {value}")
                return False
                
            print(f"📱 Opening app: {value}")
            result = os.system(f"open '{value}'")
            if result != 0:
                print(f"❌ Failed to open app: {value}")
                return False
                
        elif action_type == "url":
            print(f"🌐 Opening URL: {value}")
            result = os.system(f"open '{value}'")
            if result != 0:
                print(f"❌ Failed to open URL: {value}")
                return False
                
        elif action_type == "script":
            if not os.path.exists(value):
                print(f"❌ Script not found: {value}")
                return False
                
            if not os.access(value, os.X_OK):
                print(f"❌ Script is not executable: {value}")
                print(f"   Run 'chmod +x {value}' to make it executable.")
                return False
                
            print(f"📜 Running script: {value}")
            result = os.system(f"'{value}'")
            if result != 0:
                print(f"❌ Script returned non-zero exit code: {result}")
                return False
                
        elif action_type == "shell":
            print(f"🖥️ Running shell command: {value}")
            result = os.system(value)
            if result != 0:
                print(f"❌ Shell command returned non-zero exit code: {result}")
                return False
                
        print(f"✅ {corner} action executed successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Error executing action: {e}")
        return False

def main():
    """Main function."""
    print("🔍 FireCorners Configuration Tester")
    print("===================================")
    
    # Load and validate config
    config = load_config()
    if not validate_config(config):
        print("\n❌ Please fix the configuration errors and try again.")
        sys.exit(1)
    
    # Count configured corners
    configured_corners = 0
    for corner in ["top_left", "top_right", "bottom_left", "bottom_right"]:
        if corner in config and config[corner]:
            configured_corners += 1
    
    print(f"\n✅ Configuration file is valid. {configured_corners} corners configured.")
    
    # Ask for confirmation before testing
    print("\n⚠️ This will execute all configured actions.")
    print("   Apps will open, URLs will launch, and shell commands will run.")
    response = input("Do you want to continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Test cancelled.")
        sys.exit(0)
    
    # Test each action
    success_count = 0
    total_count = 0
    
    for corner in ["top_left", "top_right", "bottom_left", "bottom_right"]:
        if corner in config and config[corner]:
            actions = config[corner]
            
            # Handle both list and dictionary formats
            if isinstance(actions, list):
                for action in actions:
                    total_count += 1
                    if test_action(corner, action):
                        success_count += 1
                    time.sleep(1)  # Add a small delay between actions
            else:
                total_count += 1
                if test_action(corner, actions):
                    success_count += 1
                time.sleep(1)  # Add a small delay between actions
    
    # Print summary
    print("\n===================================")
    print(f"Test complete: {success_count}/{total_count} actions executed successfully.")
    
    if success_count == total_count:
        print("\n✅ All actions are working correctly!")
        print("   You can now run FireCorners with: ./run_firecorners.sh")
    else:
        print("\n⚠️ Some actions failed. Please check the errors above.")

if __name__ == "__main__":
    main() 
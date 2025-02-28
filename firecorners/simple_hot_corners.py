#!/usr/bin/env python3
"""
FireCorners Daemon

A lightweight hot corners daemon that detects when your mouse cursor reaches
the corners of your screen and triggers configured actions.

Usage:
  firecorners [--threshold=5] [--cooldown=3.0] [--dwell=0.5] [--no-test]
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

# Only import Quartz at startup since it's needed for core functionality
import Quartz
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, QTimer, pyqtSignal

# Constants
DEFAULT_CORNER_THRESHOLD = 5  # pixels from edge to trigger corner
DEFAULT_CORNER_COOLDOWN = 1.0  # seconds between triggers
DEFAULT_DWELL_TIME = 0.0  # seconds mouse must stay in corner before triggering

# Lazy imports and setup
_logging = None
_subprocess = None
_argparse = None
_config_window = None

def setup_logging():
    """Lazy setup of logging"""
    global _logging
    if _logging is None:
        import logging
        _logging = logging
        log_dir = os.path.expanduser('~/.firecorners')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        _logging.basicConfig(
            level=_logging.INFO,  # Changed to INFO for better performance
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                _logging.FileHandler(os.path.join(log_dir, 'firecorners.log')),
                _logging.StreamHandler()
            ]
        )
    return _logging

def get_subprocess():
    """Lazy import of subprocess"""
    global _subprocess
    if _subprocess is None:
        import subprocess
        _subprocess = subprocess
    return _subprocess

def get_config_window():
    """Lazy import of ConfigWindow"""
    global _config_window
    if _config_window is None:
        try:
            from firecorners.ui import ConfigWindow
        except ImportError:
            from ui import ConfigWindow
        _config_window = ConfigWindow
    return _config_window

class HotCornersDaemon(QThread):
    config_changed = pyqtSignal()

    def __init__(self, config: Dict, threshold: int = 5, cooldown: float = 1.0, dwell: float = 0.0):
        super().__init__()
        self.config = config
        self.threshold = config.get("settings", {}).get("threshold", threshold)
        self.cooldown = config.get("settings", {}).get("cooldown", cooldown)
        self.dwell = config.get("settings", {}).get("dwell", dwell)
        self.last_corner = None
        self.last_trigger_time = 0
        self.corner_enter_time = 0
        self.running = True
        self.logger = None

        # Set up config file watcher
        self.config_path = get_config_path()
        self.config_mtime = os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0
        
        # Start config watcher timer with reduced frequency
        self.config_timer = QTimer()
        self.config_timer.timeout.connect(self.check_config)
        self.config_timer.start(5000)  # Check every 5 seconds instead of every second
        
    def check_config(self):
        """Check if config file has been modified"""
        if os.path.exists(self.config_path):
            try:
                mtime = os.path.getmtime(self.config_path)
                if mtime > self.config_mtime:
                    self.logger.info("Config file changed, reloading...")
                    self.config_mtime = mtime
                    self.config = load_config()
                    # Update settings when config changes
                    self.threshold = self.config.get("settings", {}).get("threshold", self.threshold)
                    self.cooldown = self.config.get("settings", {}).get("cooldown", self.cooldown)
                    self.dwell = self.config.get("settings", {}).get("dwell", self.dwell)
                    self.config_changed.emit()
            except Exception:
                pass  # Ignore errors during config check
                
    def run(self):
        self.logger = setup_logging()
        self.logger.info("HotCornersDaemon initialized with config: %s", self.config)
        
        screen_width, screen_height = get_screen_dimensions()
        self.logger.info("Screen dimensions: %dx%d", screen_width, screen_height)
        
        while self.running:
            try:
                # Get current mouse position
                mouse_loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
                x, y = int(mouse_loc.x), int(mouse_loc.y)
                
                # Check if we're in a corner
                corner = None
                if x <= self.threshold:
                    if y <= self.threshold:
                        corner = "top_left"
                    elif y >= screen_height - self.threshold:
                        corner = "bottom_left"
                elif x >= screen_width - self.threshold:
                    if y <= self.threshold:
                        corner = "top_right"
                    elif y >= screen_height - self.threshold:
                        corner = "bottom_right"
                
                # Handle corner detection
                current_time = time.time()
                if corner:
                    if corner != self.last_corner:
                        self.corner_enter_time = current_time
                        self.last_corner = corner
                        self.logger.debug("Entered new corner: %s", corner)
                    elif (current_time - self.last_trigger_time >= self.cooldown and
                          current_time - self.corner_enter_time >= self.dwell):
                        self.logger.info("Triggering actions for corner: %s", corner)
                        self._trigger_corner_actions(corner)
                        self.last_trigger_time = current_time
                else:
                    self.last_corner = None
                
                # Adaptive sleep based on corner state
                time.sleep(0.05 if corner else 0.1)
                
            except Exception as e:
                self.logger.error("Error in mouse monitoring: %s", e, exc_info=True)
                time.sleep(1)
    
    def stop(self):
        self.logger.info("Stopping daemon...")
        self.running = False
        self.config_timer.stop()
    
    def _trigger_corner_actions(self, corner: str):
        actions = self.config.get(corner, [])
        if not actions:
            return
            
        subprocess = get_subprocess()
        for action in actions:
            action_type = action.get("type")
            value = action.get("value")
            
            if not action_type or not value:
                self.logger.warning("Invalid action in corner %s: %s", corner, action)
                continue
                
            try:
                self.logger.info("Executing %s action: %s", action_type, value)
                if action_type == "URL":
                    subprocess.run(["open", value])
                elif action_type == "Application":
                    subprocess.run(["open", "-a", value])
                elif action_type == "Shell Command":
                    subprocess.run(value, shell=True)
                elif action_type == "AppleScript":
                    subprocess.run(["osascript", "-e", value])
                self.logger.info("Action executed successfully")
            except Exception as e:
                self.logger.error("Error executing %s action: %s", action_type, e, exc_info=True)

def get_config_path():
    """Get the path to the config file"""
    return Path.home() / ".firecorners" / "config.json"

def parse_args():
    """Parse command line arguments"""
    global _argparse
    if _argparse is None:
        import argparse
        _argparse = argparse
        
    parser = _argparse.ArgumentParser(description="FireCorners - A hot corners daemon for macOS")
    parser.add_argument("--configure", action="store_true", help="Launch configuration UI")
    parser.add_argument("--threshold", type=int, default=5, help="Corner detection threshold in pixels")
    parser.add_argument("--cooldown", type=float, default=0.5, help="Cooldown period between triggers in seconds")
    parser.add_argument("--dwell", type=float, default=0.0, help="Time to dwell in corner before triggering")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--no-test", action="store_true", help="Skip testing actions on startup")
    return parser.parse_args()

def get_screen_dimensions() -> Tuple[int, int]:
    """Get the main screen dimensions"""
    main_monitor = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
    return int(main_monitor.size.width), int(main_monitor.size.height)

def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from file"""
    if not config_path:
        config_path = os.path.expanduser("~/.firecorners/config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def test_actions(config: Dict):
    """Test that all configured actions are valid"""
    for corner, actions in config.items():
        if not isinstance(actions, list) or not actions:
            continue
        logging.info("Testing actions for %s...", corner)
        for action in actions:
            action_type = action.get("type")
            value = action.get("value")
            if not action_type or not value:
                logging.warning("Invalid action in %s", corner)
                continue
            logging.info("  %s: %s", action_type, value)

def main():
    """Main function"""
    # Parse command line arguments
    args = parse_args()
    
    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Set application metadata
    app.setApplicationName("FireCorners")
    app.setApplicationDisplayName("FireCorners")
    app.setOrganizationName("FireCorners")
    app.setOrganizationDomain("firecorners.local")
    
    # Create system tray icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "FireCorners.icns")
    if not os.path.exists(icon_path):
        # Try to find the icon in the app bundle
        bundle_icon_path = os.path.join(os.path.dirname(sys.executable), "..", "Resources", "FireCorners.icns")
        if os.path.exists(bundle_icon_path):
            icon_path = bundle_icon_path
    
    tray_icon = QSystemTrayIcon(QIcon(icon_path))
    
    # Create tray menu
    menu = QMenu()
    configure_action = menu.addAction("Configure")
    menu.addSeparator()
    quit_action = menu.addAction("Quit")
    
    # Set the menu
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    
    # Load configuration
    config = load_config(args.config if args.config else None)
    
    # Create and start the daemon thread
    daemon = HotCornersDaemon(
        config,
        threshold=args.threshold,
        cooldown=args.cooldown,
        dwell=args.dwell
    )
    daemon.start()
    
    # Connect menu actions
    def show_config():
        ConfigWindow = get_config_window()
        window = ConfigWindow()
        window.show()
    
    def quit_app():
        daemon.stop()
        app.quit()
    
    configure_action.triggered.connect(show_config)
    quit_action.triggered.connect(quit_app)
    
    # Launch configuration UI if requested
    if args.configure:
        show_config()
    
    # Start the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
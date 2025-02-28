import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".firecorners"
        self.config_file = self.config_dir / "config.json"
        
        self.default_config = {
            "top_left": [],
            "top_right": [],
            "bottom_left": [],
            "bottom_right": [],
            "settings": {
                "threshold": 5,  # Default corner threshold in pixels
                "dwell": 0.0,   # Default dwell time in seconds
                "cooldown": 1.0, # Default cooldown period in seconds
                "launch_at_login": False
            }
        }
        
        # Ensure config directory exists
        try:
            self._ensure_config_dir()
        except Exception as e:
            logger.error("Failed to create config directory: %s", e, exc_info=True)
            raise
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        if not self.config_dir.exists():
            try:
                self.config_dir.mkdir(parents=True)
                logger.info("Created config directory: %s", self.config_dir)
            except Exception as e:
                logger.error("Failed to create config directory: %s", e, exc_info=True)
                raise
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    try:
                        config = json.load(f)
                        logger.info("Successfully loaded config from: %s", self.config_file)
                        
                        # Ensure all required fields exist
                        for key in self.default_config:
                            if key not in config:
                                config[key] = self.default_config[key]
                                logger.info("Added missing key to config: %s", key)
                        
                        # Ensure settings exist and have all required fields
                        if "settings" not in config:
                            config["settings"] = self.default_config["settings"]
                            logger.info("Added missing settings to config")
                        else:
                            # Add any missing settings fields
                            for key, value in self.default_config["settings"].items():
                                if key not in config["settings"]:
                                    config["settings"][key] = value
                                    logger.info("Added missing setting: %s", key)
                        
                        return config
                    except json.JSONDecodeError as e:
                        logger.error("Invalid JSON in config file: %s", e, exc_info=True)
                        logger.info("Creating new default configuration")
                        return self._create_default_config()
            else:
                logger.info("Config file not found, creating default configuration")
                return self._create_default_config()
        except Exception as e:
            logger.error("Error loading configuration: %s", e, exc_info=True)
            logger.info("Falling back to default configuration")
            return self.default_config.copy()
    
    def _create_default_config(self):
        """Create and save default configuration"""
        try:
            self._ensure_config_dir()
            config = self.default_config.copy()
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Created default configuration at: %s", self.config_file)
            return config
        except Exception as e:
            logger.error("Failed to create default configuration: %s", e, exc_info=True)
            return self.default_config.copy()
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            self._ensure_config_dir()
            
            # Validate config structure
            for key in self.default_config:
                if key not in config:
                    logger.warning("Missing key in config: %s, adding default", key)
                    config[key] = self.default_config[key]
            
            # Ensure settings exist and have all required fields
            if "settings" not in config:
                logger.warning("Missing settings in config, adding default")
                config["settings"] = self.default_config["settings"]
            else:
                for key, value in self.default_config["settings"].items():
                    if key not in config["settings"]:
                        logger.warning("Missing setting: %s, adding default", key)
                        config["settings"][key] = value
            
            # Save config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Successfully saved config to: %s", self.config_file)
            return True
        except Exception as e:
            logger.error("Error saving configuration: %s", e, exc_info=True)
            return False
    
    def get_launch_agent_path(self):
        """Get the path to the launch agent plist file"""
        return Path.home() / "Library/LaunchAgents/com.user.firecorners.plist"
    
    def set_launch_at_login(self, enabled):
        """Enable or disable launch at login"""
        plist_path = self.get_launch_agent_path()
        
        if enabled:
            try:
                # Create launch agent
                program_path = str(Path(__file__).parent.parent / "run_firecorners.sh")
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.firecorners</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>{program_path}</string>
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
</plist>"""
                
                # Create logs directory
                logs_dir = Path.home() / "Library/Logs/FireCorners"
                if not logs_dir.exists():
                    logs_dir.mkdir(parents=True)
                
                # Write plist file
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                
                # Load launch agent
                os.system(f"launchctl load {plist_path}")
                logger.info("Successfully enabled launch at login")
                return True
            except Exception as e:
                logger.error("Error enabling launch at login: %s", e, exc_info=True)
                return False
        else:
            try:
                # Remove launch agent
                if plist_path.exists():
                    os.system(f"launchctl unload {plist_path}")
                    plist_path.unlink()
                    logger.info("Successfully disabled launch at login")
                return True
            except Exception as e:
                logger.error("Error disabling launch at login: %s", e, exc_info=True)
                return False 
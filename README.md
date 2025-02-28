# FireCorners

<p align="center">
  <img src="firecorners/resources/logo.png" alt="FireCorners Logo" width="200" height="200">
</p>

A lightweight, customizable hot corners implementation for macOS that allows you to trigger actions when your mouse cursor reaches the corners of your screen.

## Features

- Trigger actions when your mouse reaches any screen corner
- Configurable corner detection threshold
- Adjustable cooldown period between triggers
- Dwell time requirement (mouse must stay in corner for a specified time)
- Visual notifications when corners are detected
- Supports multiple action types:
  - Open applications
  - Open URLs
  - Run shell commands
  - Execute scripts

## Installation

### Option 1: Download the Binary (Easiest)

1. Download the latest release from the [Releases](https://github.com/yourusername/firecorners/releases) page
2. Mount the DMG file and drag FireCorners to your Applications folder
   - Simply drag the FireCorners icon to the Applications folder shortcut in the installer window
   - After copying is complete, eject the installer by dragging it to the Trash or right-clicking and selecting "Eject"
3. Run FireCorners from your Applications folder

> **Note:** The first time you run FireCorners, macOS may show a security warning since the app is not signed with an Apple Developer certificate. To allow the app to run:
>
> 1. Go to System Preferences > Security & Privacy
> 2. Look for the message about FireCorners being blocked
> 3. Click "Open Anyway" to allow the application to run

### Option 2: Install from Source

1. Clone this repository or download the files
2. Make sure you have Python 3 installed
3. Make the startup script executable:
   ```
   chmod +x run_firecorners.sh
   ```
4. Run FireCorners:
   ```
   ./run_firecorners.sh
   ```

### Option 3: Install as a Python Package

```
pip install firecorners
```

After installation, you can run FireCorners from anywhere:

```
firecorners --dwell=0.2 --no-test
```

## Configuration

Actions for each corner are defined in the `config.json` file with the following format:

```json
{
  "top_left": {
    "type": "url",
    "value": "https://www.x.com/home"
  },
  "top_right": {
    "type": "app",
    "value": "/Applications/Obsidian.app"
  },
  "bottom_left": {
    "type": "shell",
    "value": "open -a 'System Preferences'"
  },
  "bottom_right": {
    "type": "script",
    "value": "/path/to/your/script.sh"
  }
}
```

The configuration file is searched for in the following locations (in order):

1. `~/.firecorners/config.json` (user's home directory)
2. `./config.json` (current directory)
3. Package default configuration

Each corner can have one of the following action types:

- `app`: Opens an application (provide the full path)
- `url`: Opens a URL in the default browser
- `shell`: Executes a shell command
- `script`: Runs a script file (must be executable)

## Usage

### Running from Source

Run the script with default settings:

```
./run_firecorners.sh
```

Or customize the settings:

```
./run_firecorners.sh --threshold=10 --cooldown=2.0 --dwell=0.3 --no-test
```

### Running as a Python Package

```
firecorners --threshold=10 --cooldown=2.0 --dwell=0.3 --no-test
```

### Command-line Options

- `--threshold=N`: Set the number of pixels from the edge to trigger a corner (default: 5)
- `--cooldown=N.N`: Set the seconds between triggers (default: 3.0)
- `--dwell=N.N`: Set the seconds the mouse must stay in a corner (default: 0.5)
- `--no-test`: Skip testing actions on startup
- `--config=PATH`: Specify a custom config file path
- `--help`: Show help message

## Auto-start at Login

To have FireCorners start automatically when you log in:

### Using the Installer Script

```
./install_autostart.sh --dwell=0.2 --no-test
```

### Manual Setup

1. Create a launch agent file:

   ```
   mkdir -p ~/Library/LaunchAgents
   touch ~/Library/LaunchAgents/com.user.firecorners.plist
   ```

2. Add the following content to the file (adjust paths as needed):

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.user.firecorners</string>
       <key>ProgramArguments</key>
       <array>
           <string>/path/to/run_firecorners.sh</string>
           <string>--dwell=0.2</string>
           <string>--no-test</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
   </dict>
   </plist>
   ```

3. Load the launch agent:
   ```
   launchctl load ~/Library/LaunchAgents/com.user.firecorners.plist
   ```

## Building from Source

### Building a Python Package

```
pip install setuptools wheel
python setup.py sdist bdist_wheel
```

The package will be available in the `dist` directory.

### Building a Standalone Binary

```
./build_binary.sh
```

This will create:

- A standalone application at `dist/FireCorners.app`
- A DMG installer at `dist/FireCorners.dmg`

To create a custom DMG with a professional background:

```
./create_dmg.sh
```

This creates a polished DMG installer with:

- Custom background image with installation instructions
- Properly positioned application and Applications folder icons
- Professional appearance for better user experience

### Build Scripts

The project includes several build scripts:

- `build_binary.sh`: Creates a standalone application using PyInstaller and a basic DMG
- `create_dmg.sh`: Creates a professional DMG with custom background and layout
- `firecorners/resources/convert_background.py`: Converts SVG background to PNG for the DMG
- `firecorners/resources/generate_icon.py`: Generates the application icon

## Troubleshooting

- If actions aren't triggering, try increasing the threshold value
- If actions trigger too easily, decrease the threshold and/or increase the dwell time
- Check the terminal output for any error messages
- Ensure your config.json file is properly formatted

## Development

### Project Structure

```
firecorners/
├── __init__.py
├── simple_hot_corners.py
├── config.json
└── resources/
    ├── logo.png
    ├── logo.svg
    ├── FireCorners.icns
    ├── dmg_background.svg
    ├── dmg_background.png
    ├── convert_background.py
    └── generate_icon.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

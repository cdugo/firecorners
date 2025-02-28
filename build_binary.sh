#!/bin/bash
# FireCorners Binary Builder
# This script builds a macOS app bundle that includes both the daemon and UI

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Create dist directory
mkdir -p dist

# Build the app bundle
echo "Building FireCorners.app..."
pyinstaller \
    --name "FireCorners" \
    --onefile \
    --windowed \
    --icon "firecorners/resources/FireCorners.icns" \
    --add-data "firecorners:firecorners" \
    --add-data "firecorners/resources/*:resources" \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PyQt6.QtGui \
    --hidden-import firecorners.ui \
    --hidden-import firecorners.ui.config_window \
    --hidden-import firecorners.ui.screen_preview \
    --hidden-import firecorners.ui.action_dialog \
    --hidden-import firecorners.ui.action_editor \
    --hidden-import firecorners.ui.config_manager \
    --osx-bundle-identifier "com.firecorners.app" \
    --add-binary "configure_ui.py:." \
    --collect-all firecorners \
    firecorners/simple_hot_corners.py

# Copy helper scripts into the app bundle
mkdir -p "dist/FireCorners.app/Contents/Resources/scripts"
cp run_firecorners.sh "dist/FireCorners.app/Contents/Resources/scripts/"
cp install_autostart.sh "dist/FireCorners.app/Contents/Resources/scripts/"

# Copy icon to Resources
cp "firecorners/resources/FireCorners.icns" "dist/FireCorners.app/Contents/Resources/"

# Make scripts executable
chmod +x "dist/FireCorners.app/Contents/Resources/scripts/run_firecorners.sh"
chmod +x "dist/FireCorners.app/Contents/Resources/scripts/install_autostart.sh"

# Update the Info.plist to add LSUIElement (makes the app run in background)
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "dist/FireCorners.app/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Set :LSUIElement true" "dist/FireCorners.app/Contents/Info.plist"

echo "Build complete! App bundle is in dist/FireCorners.app"

# Create DMG if create_dmg.sh exists
if [ -f "create_dmg.sh" ]; then
    echo "Creating DMG installer..."
    ./create_dmg.sh
fi 
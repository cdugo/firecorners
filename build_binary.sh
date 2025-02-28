#!/bin/bash
# FireCorners Binary Builder
# This script builds a standalone binary for FireCorners

# Check if PyInstaller is installed
if ! pip3 show pyinstaller > /dev/null 2>&1; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Check if pyobjc is installed
if ! pip3 show pyobjc > /dev/null 2>&1; then
    echo "Installing pyobjc..."
    pip3 install pyobjc
fi

# Create build directory
mkdir -p build

# Copy config file to build directory
cp config.json build/

# Build the binary
echo "Building FireCorners binary..."
pyinstaller --clean --onefile --windowed \
    --name="FireCorners" \
    --icon="firecorners/resources/FireCorners.icns" \
    --add-data="build/config.json:." \
    --hidden-import="pkg_resources.py2_warn" \
    simple_hot_corners.py

# Generate the background image
echo "Generating background image..."
python3 firecorners/resources/convert_background.py

# Create a DMG file
echo "Creating DMG file..."

# Create a temporary directory for DMG contents
rm -rf temp_dmg
mkdir -p temp_dmg

# Copy the application bundle to the temporary directory
cp -r dist/FireCorners.app temp_dmg/

# Add a symbolic link to /Applications
ln -s /Applications temp_dmg/

# Create a temporary DMG first
TMP_DMG="dist/FireCorners_tmp.dmg"
FINAL_DMG="dist/FireCorners.dmg"

# Create temporary DMG
hdiutil create -volname "FireCorners" -srcfolder temp_dmg -ov -format UDRW "$TMP_DMG"

# Mount the temporary DMG
MOUNT_POINT="/Volumes/FireCorners"
hdiutil attach -readwrite -noverify -noautoopen "$TMP_DMG"

# Wait for the mount to complete
sleep 2

# Set the custom icon arrangement
echo "Setting DMG appearance..."

# Set background image
mkdir -p "$MOUNT_POINT/.background"
cp firecorners/resources/dmg_background.png "$MOUNT_POINT/.background/"

# Create Apple Script to set DMG appearance
cat > /tmp/dmg_setup.applescript << EOF
tell application "Finder"
  tell disk "FireCorners"
    open
    set current view of container window to icon view
    set toolbar visible of container window to false
    set statusbar visible of container window to false
    set the bounds of container window to {400, 100, 940, 480}
    set theViewOptions to the icon view options of container window
    set arrangement of theViewOptions to not arranged
    set icon size of theViewOptions to 80
    set background picture of theViewOptions to file ".background:dmg_background.png"
    
    -- Position the icons
    set position of item "FireCorners.app" of container window to {140, 190}
    set position of item "Applications" of container window to {400, 190}
    
    update without registering applications
    delay 5
    close
  end tell
end tell
EOF

# Run the Apple Script
osascript /tmp/dmg_setup.applescript

# Make sure the changes persist
sync

# Unmount the DMG
hdiutil detach "$MOUNT_POINT"

# Convert the DMG to read-only
hdiutil convert "$TMP_DMG" -format UDZO -o "$FINAL_DMG"

# Remove the temporary DMG
rm "$TMP_DMG"

# Clean up
rm -rf temp_dmg

echo "Build complete!"
echo "Binary: dist/FireCorners.app"
echo "DMG: dist/FireCorners.dmg" 
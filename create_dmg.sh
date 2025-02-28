#!/bin/bash
# Create a custom DMG for FireCorners with a professional background

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

# Make sure we have the app bundle
if [ ! -d "dist/FireCorners.app" ]; then
    echo "Error: FireCorners.app not found in dist directory."
    echo "Please build the app first using build_binary.sh"
    exit 1
fi

# Generate the background image
echo "Generating background image..."
python3 firecorners/resources/convert_background.py

# Create the DMG
echo "Creating custom DMG with background image..."

# Remove existing DMG if it exists
rm -f dist/FireCorners.dmg

# Create the DMG with custom background
create-dmg \
    --volname "FireCorners" \
    --volicon "firecorners/resources/FireCorners.icns" \
    --background "firecorners/resources/dmg_background.png" \
    --window-pos 200 120 \
    --window-size 540 380 \
    --icon-size 128 \
    --text-size 12 \
    --icon "FireCorners.app" 140 190 \
    --app-drop-link 400 190 \
    --no-internet-enable \
    "dist/FireCorners.dmg" \
    "dist/FireCorners.app"

echo "DMG creation complete!"
echo "Installer: dist/FireCorners.dmg" 
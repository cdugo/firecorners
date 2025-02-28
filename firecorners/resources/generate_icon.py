#!/usr/bin/env python3
"""
Generate icon files for FireCorners from a base image.
This script creates .icns file for macOS from a base PNG image.
"""

import os
import sys
import subprocess
from pathlib import Path

def generate_icns(input_image, output_dir):
    """Generate .icns file from input image"""
    # Create temporary iconset directory
    iconset_dir = os.path.join(output_dir, "FireCorners.iconset")
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Define icon sizes
    icon_sizes = [
        (16, 16), (32, 32), (64, 64), (128, 128), 
        (256, 256), (512, 512), (1024, 1024)
    ]
    
    # Generate icons at different sizes
    for size in icon_sizes:
        width, height = size
        output_file = os.path.join(iconset_dir, f"icon_{width}x{height}.png")
        subprocess.run([
            "sips", 
            "-z", str(height), str(width), 
            input_image, 
            "--out", output_file
        ], check=True)
        
        # Also create @2x versions
        if width <= 512:
            output_file = os.path.join(iconset_dir, f"icon_{width}x{height}@2x.png")
            subprocess.run([
                "sips", 
                "-z", str(height*2), str(width*2), 
                input_image, 
                "--out", output_file
            ], check=True)
    
    # Convert iconset to icns
    icns_file = os.path.join(output_dir, "FireCorners.icns")
    subprocess.run([
        "iconutil", 
        "-c", "icns", 
        iconset_dir, 
        "-o", icns_file
    ], check=True)
    
    # Clean up
    subprocess.run(["rm", "-rf", iconset_dir])
    
    print(f"Icon generated at: {icns_file}")
    return icns_file

def main():
    """Main function"""
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Check if input image is provided
    if len(sys.argv) > 1:
        input_image = sys.argv[1]
    else:
        # Use default image in resources directory
        input_image = os.path.join(script_dir, "logo.png")
    
    # Check if input image exists
    if not os.path.exists(input_image):
        print(f"Error: Input image not found at {input_image}")
        print("Please provide a valid image path.")
        sys.exit(1)
    
    # Generate icon
    generate_icns(input_image, script_dir)

if __name__ == "__main__":
    main() 
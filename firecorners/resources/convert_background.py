#!/usr/bin/env python3
"""
Convert the SVG background to PNG for use in the DMG installer
"""

import os
import subprocess
from pathlib import Path

def convert_svg_to_png():
    """Convert SVG background to PNG using cairosvg"""
    try:
        # Try to import cairosvg
        import cairosvg
        
        # Get the directory of this script
        script_dir = Path(__file__).parent
        svg_path = script_dir / "dmg_background.svg"
        png_path = script_dir / "dmg_background.png"
        
        # Convert SVG to PNG
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=540, output_height=380)
        print(f"Successfully converted {svg_path} to {png_path}")
        
    except ImportError:
        # If cairosvg is not available, try using rsvg-convert
        try:
            script_dir = Path(__file__).parent
            svg_path = script_dir / "dmg_background.svg"
            png_path = script_dir / "dmg_background.png"
            
            # Try using rsvg-convert (comes with librsvg)
            subprocess.run(["rsvg-convert", "-o", str(png_path), str(svg_path)], check=True)
            print(f"Successfully converted {svg_path} to {png_path} using rsvg-convert")
            
        except (subprocess.SubprocessError, FileNotFoundError):
            # If rsvg-convert is not available, try using Inkscape
            try:
                subprocess.run(["inkscape", "-o", str(png_path), str(svg_path)], check=True)
                print(f"Successfully converted {svg_path} to {png_path} using Inkscape")
                
            except (subprocess.SubprocessError, FileNotFoundError):
                # If all else fails, suggest manual conversion
                print("Error: Could not convert SVG to PNG automatically.")
                print("Please install one of the following:")
                print("  - cairosvg (pip install cairosvg)")
                print("  - librsvg (brew install librsvg)")
                print("  - Inkscape (brew install inkscape)")
                print("Or convert the SVG to PNG manually using an image editor.")
                return False
    
    return True

if __name__ == "__main__":
    convert_svg_to_png() 
"""
FireCorners - Hot Corners for macOS

A lightweight hot corners daemon that detects when your mouse cursor reaches
the corners of your screen and triggers configured actions.
"""

from .ui import ConfigWindow
from .simple_hot_corners import main

__version__ = "1.0.0"
__all__ = ["ConfigWindow", "main"] 
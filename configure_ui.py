#!/usr/bin/env python3
"""
FireCorners Configuration UI

This script launches the FireCorners configuration window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from firecorners.ui import ConfigWindow

def main():
    """Launch the configuration UI"""
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
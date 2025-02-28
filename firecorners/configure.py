#!/usr/bin/env python3
"""
FireCorners Configuration UI

A graphical interface for configuring the FireCorners hot corners daemon.
"""

import sys
from PyQt6.QtWidgets import QApplication
from .ui import ConfigWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("FireCorners")
    app.setApplicationDisplayName("FireCorners Configuration")
    app.setOrganizationName("FireCorners")
    app.setOrganizationDomain("firecorners.local")
    
    # Create and show the main window
    window = ConfigWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 
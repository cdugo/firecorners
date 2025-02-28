#!/usr/bin/env python3
"""
Setup script for FireCorners
"""

from setuptools import setup, find_packages

setup(
    name="firecorners",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyobjc>=9.0",
        "pyobjc-framework-Cocoa>=9.0",
        "pyobjc-framework-Quartz>=9.0",
        "PyQt6>=6.4.0",
        "pynput>=1.7.6",
        "pillow>=9.0.0"
    ],
    entry_points={
        "console_scripts": [
            "firecorners=firecorners.simple_hot_corners:main",
            "firecorners-config=firecorners.configure:main"
        ]
    },
    package_data={
        "firecorners": ["*.sh", "*.plist"]
    },
    author="FireCorners Team",
    author_email="info@firecorners.local",
    description="A lightweight hot corners daemon for macOS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="macos,hot corners,automation",
    url="https://github.com/firecorners/firecorners",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Desktop Environment :: Window Managers",
    ],
    python_requires=">=3.6"
)

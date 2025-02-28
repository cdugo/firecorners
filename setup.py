#!/usr/bin/env python3
"""
Setup script for FireCorners
"""

from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="firecorners",
    version="1.0.0",
    author="FireCorners Team",
    author_email="your.email@example.com",
    description="A lightweight, customizable hot corners implementation for macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/firecorners",
    packages=find_namespace_packages(include=["firecorners", "firecorners.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: MacOS X",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyobjc",
    ],
    entry_points={
        "console_scripts": [
            "firecorners=firecorners.simple_hot_corners:main",
        ],
    },
    include_package_data=True,
    package_data={
        "firecorners": ["config.json", "resources/*"],
    },
)

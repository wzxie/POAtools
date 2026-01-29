#!/usr/bin/env python3

import importlib
import sys

required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn']

missing_packages = []
for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"? {package} is installed")
    except ImportError:
        missing_packages.append(package)
        print(f"? {package} is missing")

if missing_packages:
    print(f"\nMissing packages: {', '.join(missing_packages)}")
    print("Please install them using:")
    print(f"pip3 install {' '.join(missing_packages)}")
    sys.exit(1)
else:
    print("\nAll required Python packages are installed!")
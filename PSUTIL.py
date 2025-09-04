#!/usr/bin/env python3
"""
PSUTIL.py — Dependency installer for SCDelete
Installs required third-party dependencies for securely_deleter.py
"""

import subprocess
import sys

def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
        print(f"{package_name} installed successfully!\n")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}.\n")

def main():
    # Core dependencies
    install_package("psutil")
    install_package("requests")

    print("✅ All dependencies are installed. You can now run securely_deleter.py")

if __name__ == "__main__":
    main()

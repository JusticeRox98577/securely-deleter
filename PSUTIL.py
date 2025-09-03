import subprocess
import sys

def install_package(package_name):
    """Function to install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} installed successfully!")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}.")

# Install psutil
install_package("psutil")

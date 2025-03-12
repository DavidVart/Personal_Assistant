#!/usr/bin/env python3
"""
Environment Check Script for Personal Assistant

This script checks if the environment is properly set up for the Personal Assistant
and provides solutions to fix any issues detected.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def check_python_version():
    """Check if the Python version is compatible."""
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print("   Solution: Install Python 3.8 or higher from https://www.python.org/downloads/")
        return False
    print("✅ Python version is compatible.")
    return True

def check_virtual_env():
    """Check if running in a virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in a virtual environment.")
        return True
    print("❌ Not running in a virtual environment.")
    print("   Solution: Create and activate a virtual environment with:")
    print("   python -m venv venv")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    print("   Alternatively, run the setup script:")
    if os.name == 'nt':  # Windows
        print("   setup.bat")
    else:  # macOS/Linux
        print("   ./setup.sh")
    return False

def check_openai_api_key():
    """Check if the OpenAI API key is set."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:4] + "..." + api_key[-4:]
        print(f"✅ OPENAI_API_KEY is set: {masked_key}")
        return True
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file exists, but OPENAI_API_KEY is not loaded.")
        print("   Solution: Load the .env file with python-dotenv by adding:")
        print("   from dotenv import load_dotenv")
        print("   load_dotenv()")
        print("   Or restart your terminal/IDE after creating the .env file.")
        return False
    
    print("❌ OPENAI_API_KEY is not set.")
    print("   Solution: Create a .env file with your API key:")
    print("   echo \"OPENAI_API_KEY=your-api-key-here\" > .env")
    print("   Or set it as an environment variable:")
    if os.name == 'nt':  # Windows
        print("   set OPENAI_API_KEY=your-api-key-here")
    else:  # macOS/Linux
        print("   export OPENAI_API_KEY=your-api-key-here")
    return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "openai-agents",
        "openai",
        "python-dotenv",
        "flask",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "icalendar",
        "vobject",
        "pytz"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            print(f"✅ {package} is installed.")
        except ImportError:
            print(f"❌ {package} is not installed.")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nMissing packages:")
        install_cmd = "pip install " + " ".join(missing_packages)
        print(f"   {install_cmd}")
        
        print("\nSolution:")
        print(f"   Run: {install_cmd}")
        print("   Or install all dependencies at once:")
        print("   pip install -r requirements.txt")
        
        # Offer to install the missing packages
        if input("\nWould you like to install the missing packages now? (y/n): ").lower() == 'y':
            try:
                print(f"\nRunning: {install_cmd}")
                subprocess.run(install_cmd, shell=True, check=True)
                print("✅ Packages installed successfully.")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install packages.")
                return False
        return False
    
    return True

def check_directories():
    """Check if required directories exist."""
    required_dirs = ["data", "credentials", "integrations", "templates", "static"]
    
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"✅ {directory}/ directory exists.")
        else:
            print(f"❌ {directory}/ directory does not exist.")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print("\nSolution:")
        for directory in missing_dirs:
            print(f"   mkdir -p {directory}")
        
        # Offer to create the missing directories
        if input("\nWould you like to create the missing directories now? (y/n): ").lower() == 'y':
            try:
                for directory in missing_dirs:
                    os.makedirs(directory, exist_ok=True)
                    print(f"✅ Created {directory}/ directory.")
                return True
            except Exception as e:
                print(f"❌ Failed to create directories: {str(e)}")
                return False
        return False
    
    return True

def check_files():
    """Check if required files exist."""
    required_files = [
        "assistant.py",
        "advanced_assistant.py",
        "web_assistant.py",
        "integrated_assistant.py",
        "run.py",
        "setup_integrations.py",
        "requirements.txt"
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.isfile(file):
            print(f"✅ {file} exists.")
        else:
            print(f"❌ {file} does not exist.")
            missing_files.append(file)
    
    if missing_files:
        print("\nSolution:")
        print("   The following files are missing and need to be created or downloaded:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n   You can clone the repository again or download the missing files from:")
        print("   https://github.com/yourusername/personal-assistant")
        return False
    
    return True

def check_google_calendar_credentials():
    """Check if Google Calendar credentials are set up."""
    credentials_path = Path("credentials/credentials.json")
    example_path = Path("credentials/credentials.example.json")
    
    if credentials_path.exists():
        print("✅ Google Calendar credentials file exists.")
        return True
    
    print("❌ Google Calendar credentials file does not exist.")
    print("   Solution:")
    print("   1. Create a project in the Google Cloud Console: https://console.cloud.google.com/")
    print("   2. Enable the Google Calendar API")
    print("   3. Create OAuth 2.0 credentials (Desktop application)")
    print("   4. Download the credentials.json file")
    print("   5. Place it in the 'credentials' directory")
    
    if example_path.exists():
        print("\n   An example credentials file is available at:")
        print("   credentials/credentials.example.json")
        print("   Use it as a template for the format required.")
    
    return False

def check_executable_permissions():
    """Check if scripts have executable permissions."""
    executable_files = [
        "run.py",
        "setup_integrations.py",
        "integrated_assistant.py",
        "test_integrated_assistant.py",
        "check_environment.py"
    ]
    
    # Skip on Windows as executable permissions don't apply
    if os.name == 'nt':
        return True
    
    non_executable = []
    
    for file in executable_files:
        if os.path.isfile(file):
            if os.access(file, os.X_OK):
                print(f"✅ {file} is executable.")
            else:
                print(f"❌ {file} is not executable.")
                non_executable.append(file)
    
    if non_executable:
        print("\nSolution:")
        chmod_cmd = "chmod +x " + " ".join(non_executable)
        print(f"   {chmod_cmd}")
        
        # Offer to make the files executable
        if input("\nWould you like to make these files executable now? (y/n): ").lower() == 'y':
            try:
                subprocess.run(chmod_cmd, shell=True, check=True)
                print("✅ Files are now executable.")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to make files executable.")
                return False
        return False
    
    return True

def main():
    """Main function to run all checks."""
    print("=== Personal Assistant Environment Check ===\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("OpenAI API Key", check_openai_api_key),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Files", check_files),
        ("Google Calendar Credentials", check_google_calendar_credentials)
    ]
    
    # Add executable permissions check only for non-Windows systems
    if os.name != 'nt':
        checks.append(("Executable Permissions", check_executable_permissions))
    
    results = {}
    
    for name, check_func in checks:
        print(f"\n--- {name} Check ---")
        results[name] = check_func()
    
    print("\n=== Summary ===")
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    if all(results.values()):
        print("\n✅ All checks passed! Your environment is ready.")
    else:
        print("\n❌ Some checks failed. Please fix the issues using the suggested solutions.")
        print("\nQuick Fix Commands:")
        
        # Provide a summary of all commands to fix issues
        if "Dependencies" in results and not results["Dependencies"]:
            print("   pip install -r requirements.txt")
        
        missing_dirs = [d for d in ["data", "credentials", "integrations", "templates", "static"] if not os.path.isdir(d)]
        if missing_dirs:
            for directory in missing_dirs:
                print(f"   mkdir -p {directory}")
        
        if os.name != 'nt' and "Executable Permissions" in results and not results["Executable Permissions"]:
            print("   chmod +x run.py setup_integrations.py integrated_assistant.py test_integrated_assistant.py check_environment.py")
        
        if "OpenAI API Key" in results and not results["OpenAI API Key"]:
            print("   echo \"OPENAI_API_KEY=your-api-key-here\" > .env")

if __name__ == "__main__":
    main() 
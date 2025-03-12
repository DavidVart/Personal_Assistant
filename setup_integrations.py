#!/usr/bin/env python3
"""
Integration Setup Script for Personal Assistant

This script helps set up integrations with various services.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

def setup_google_calendar():
    """Set up Google Calendar integration."""
    try:
        from integrations.google_calendar import setup_google_calendar
        return setup_google_calendar()
    except ImportError as e:
        print(f"Error importing Google Calendar module: {str(e)}")
        print("Make sure you have installed the required dependencies:")
        print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False

def setup_contacts():
    """Set up contacts integration."""
    try:
        from integrations.contacts import list_contacts
        contacts = list_contacts()
        print("\n=== Contacts Integration Setup ===")
        print(f"Found {len(contacts)} existing contacts.")
        print("Contacts integration is ready to use.")
        return True
    except ImportError as e:
        print(f"Error importing contacts module: {str(e)}")
        return False

def setup_notes():
    """Set up notes integration."""
    try:
        from integrations.notes import list_notes
        notes = list_notes()
        print("\n=== Notes Integration Setup ===")
        print(f"Found {len(notes)} existing notes.")
        print("Notes integration is ready to use.")
        return True
    except ImportError as e:
        print(f"Error importing notes module: {str(e)}")
        return False

def main():
    """Main entry point for the setup script."""
    print("=== Personal Assistant Integration Setup ===")
    print("This script will help you set up integrations with various services.")
    print("You can choose which integrations to set up.")
    
    # Create necessary directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    credentials_dir = Path("credentials")
    credentials_dir.mkdir(exist_ok=True)
    
    # Menu
    while True:
        print("\nAvailable integrations:")
        print("1. Google Calendar")
        print("2. Contacts")
        print("3. Notes")
        print("4. Set up all integrations")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            setup_google_calendar()
        elif choice == "2":
            setup_contacts()
        elif choice == "3":
            setup_notes()
        elif choice == "4":
            print("\nSetting up all integrations...")
            setup_google_calendar()
            setup_contacts()
            setup_notes()
            print("\nAll integrations have been set up.")
        elif choice == "5":
            print("\nExiting setup. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 
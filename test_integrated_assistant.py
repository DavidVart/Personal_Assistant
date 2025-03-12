#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
import json

# Check if the script is running in a virtual environment
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("Warning: It seems you are not running this script in a virtual environment.")
    response = input("Do you want to continue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# Check if OPENAI_API_KEY is set
if 'OPENAI_API_KEY' not in os.environ:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    api_key = input("Please enter your OpenAI API key: ")
    os.environ['OPENAI_API_KEY'] = api_key

# Import the integrated assistant functions
try:
    from integrated_assistant import (
        check_integration_status,
        add_event, list_events, delete_event,
        add_contact, find_contact, list_all_contacts,
        add_note, find_note, get_note_by_id, list_all_notes
    )
    print("Successfully imported integrated assistant functions.")
except ImportError as e:
    print(f"Error importing integrated assistant functions: {e}")
    sys.exit(1)

def test_calendar_integration():
    print("\n=== Testing Calendar Integration ===")
    
    # Check integration status
    print("\nChecking integration status...")
    status = check_integration_status()
    print(f"Integration status: {status}")
    
    # Add an event
    print("\nAdding a test event...")
    tomorrow = datetime.now() + timedelta(days=1)
    event_start = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    event_end = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)
    
    event_result = add_event(
        "Test Event",
        event_start.isoformat(),
        event_end.isoformat(),
        "This is a test event created by the test script"
    )
    print(f"Add event result: {event_result}")
    
    # List events
    print("\nListing events for tomorrow...")
    events = list_events(tomorrow.strftime("%Y-%m-%d"))
    print(f"Events: {events}")
    
    # Delete the test event if it was created
    if "event_id" in event_result:
        print(f"\nDeleting test event {event_result['event_id']}...")
        delete_result = delete_event(event_result["event_id"])
        print(f"Delete result: {delete_result}")

def test_contacts_integration():
    print("\n=== Testing Contacts Integration ===")
    
    # Add a contact
    print("\nAdding a test contact...")
    contact_result = add_contact(
        "Test Contact",
        "test@example.com",
        "555-1234",
        "123 Test St, Test City",
        "This is a test contact"
    )
    print(f"Add contact result: {contact_result}")
    
    # Find the contact
    print("\nFinding contact with 'Test' in the name...")
    found_contacts = find_contact("Test")
    print(f"Found contacts: {found_contacts}")
    
    # List all contacts
    print("\nListing all contacts...")
    all_contacts = list_all_contacts()
    print(f"All contacts: {all_contacts}")

def test_notes_integration():
    print("\n=== Testing Notes Integration ===")
    
    # Add a note
    print("\nAdding a test note...")
    note_result = add_note(
        "Test Note",
        "This is a test note created by the test script",
        ["test", "integration"]
    )
    print(f"Add note result: {note_result}")
    
    # Find the note
    print("\nFinding notes with 'test' in the content...")
    found_notes = find_note("test")
    print(f"Found notes: {found_notes}")
    
    # Get note by ID
    if "note_id" in note_result:
        print(f"\nGetting note by ID {note_result['note_id']}...")
        note = get_note_by_id(note_result["note_id"])
        print(f"Note: {note}")
    
    # List all notes
    print("\nListing all notes...")
    all_notes = list_all_notes()
    print(f"All notes: {all_notes}")

def main():
    print("=== Integrated Assistant Test Script ===")
    print("This script will test the functionality of the integrated assistant.")
    
    try:
        test_calendar_integration()
    except Exception as e:
        print(f"Calendar integration test failed: {e}")
    
    try:
        test_contacts_integration()
    except Exception as e:
        print(f"Contacts integration test failed: {e}")
    
    try:
        test_notes_integration()
    except Exception as e:
        print(f"Notes integration test failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 
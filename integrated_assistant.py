#!/usr/bin/env python3
"""
Integrated Personal Assistant

This script provides a personal assistant with integrations for Google Calendar,
contacts, and notes.
"""

import os
import sys
import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional, Any

from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

# Import integrations
try:
    from integrations.google_calendar import add_event as gc_add_event
    from integrations.google_calendar import get_events as gc_get_events
    from integrations.google_calendar import delete_event as gc_delete_event
    from integrations.google_calendar import update_event as gc_update_event
    from integrations.google_calendar import get_calendar_service
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

from integrations.contacts import add_contact as contacts_add_contact
from integrations.contacts import get_contact as contacts_get_contact
from integrations.contacts import update_contact as contacts_update_contact
from integrations.contacts import delete_contact as contacts_delete_contact
from integrations.contacts import search_contacts as contacts_search_contacts
from integrations.contacts import list_contacts as contacts_list_contacts

from integrations.notes import add_note as notes_add_note
from integrations.notes import get_note as notes_get_note
from integrations.notes import update_note as notes_update_note
from integrations.notes import delete_note as notes_delete_note
from integrations.notes import search_notes as notes_search_notes
from integrations.notes import list_notes as notes_list_notes
from integrations.notes import get_tags as notes_get_tags

# Load environment variables from .env file
load_dotenv()

# Check if API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set your OpenAI API key in the .env file or as an environment variable.")
    exit(1)

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Define function tools for the assistant

@function_tool
def schedule_event(date: str, time: str, event: str, description: Optional[str] = None, 
                  location: Optional[str] = None, duration_minutes: Optional[int] = None) -> str:
    """
    Schedule an event on a specific date and time.
    
    Args:
        date: The date in YYYY-MM-DD format
        time: The time in HH:MM format
        event: The name or title of the event
        description: Optional detailed description of the event
        location: Optional location of the event
        duration_minutes: Optional duration of the event in minutes (default: 60)
    
    Returns:
        A confirmation message
    """
    try:
        # Parse the date and time
        event_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Set default values
        description = description or ""
        location = location or ""
        duration_minutes = duration_minutes or 60
        
        # Calculate end time
        end_datetime = event_datetime + datetime.timedelta(minutes=duration_minutes)
        
        # Use Google Calendar integration if available
        if GOOGLE_CALENDAR_AVAILABLE:
            # Check if Google Calendar service is available
            if get_calendar_service():
                result = gc_add_event(
                    summary=event,
                    start_time=event_datetime,
                    end_time=end_datetime,
                    description=description,
                    location=location
                )
                
                if "error" in result:
                    return f"Error scheduling event in Google Calendar: {result['error']}"
                
                return f"Scheduled '{event}' on {event_datetime.strftime('%A, %B %d, %Y at %I:%M %p')} in Google Calendar."
        
        # Fallback to local storage
        # Load existing events
        events_file = data_dir / "events.json"
        if events_file.exists():
            with open(events_file, "r") as f:
                events = json.load(f)
        else:
            events = []
        
        # Create new event
        new_event = {
            "id": len(events) + 1,
            "title": event,
            "description": description,
            "location": location,
            "date": date,
            "time": time,
            "duration_minutes": duration_minutes,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Add to events list
        events.append(new_event)
        
        # Save updated events
        with open(events_file, "w") as f:
            json.dump(events, f, indent=2)
        
        return f"Scheduled '{event}' on {event_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}."
    
    except ValueError as e:
        return f"Error: {str(e)}. Please provide date in YYYY-MM-DD format and time in HH:MM format."

@function_tool
def list_events(date: Optional[str] = None, days: Optional[int] = None) -> str:
    """
    List scheduled events, optionally filtered by date.
    
    Args:
        date: Optional date in YYYY-MM-DD format to filter events
        days: Optional number of days to look ahead (default: 7)
    
    Returns:
        A list of events
    """
    # Set default values
    days = days or 7
    
    # Use Google Calendar integration if available
    if GOOGLE_CALENDAR_AVAILABLE:
        # Check if Google Calendar service is available
        if get_calendar_service():
            # Set up time range
            if date:
                try:
                    start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    return f"Error: Invalid date format. Please provide date in YYYY-MM-DD format."
            else:
                start_date = datetime.datetime.now()
            
            end_date = start_date + datetime.timedelta(days=days)
            
            # Get events from Google Calendar
            events = gc_get_events(time_min=start_date, time_max=end_date)
            
            if not events:
                return "No events found in Google Calendar." if date else "You have no scheduled events in Google Calendar."
            
            # Format events for display
            result = "Here are your scheduled events from Google Calendar:\n\n"
            for event in events:
                if "error" in event:
                    return f"Error retrieving events from Google Calendar: {event['error']}"
                
                result += f"- {event['summary']} on {event['start']}\n"
                if event.get('location'):
                    result += f"  Location: {event['location']}\n"
                if event.get('description'):
                    result += f"  Description: {event['description']}\n"
            
            return result
    
    # Fallback to local storage
    events_file = data_dir / "events.json"
    if not events_file.exists():
        return "No events found." if date else "You have no scheduled events."
    
    with open(events_file, "r") as f:
        events = json.load(f)
    
    # Filter by date if provided
    if date:
        events = [event for event in events if event["date"] == date]
    
    if not events:
        return "No events found." if date else "You have no scheduled events."
    
    # Format events for display
    result = "Here are your scheduled events:\n\n"
    for event in events:
        event_date = event["date"]
        event_time = event["time"]
        event_datetime = datetime.datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")
        formatted_date = event_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        
        result += f"- {event['title']} on {formatted_date}\n"
        if event.get("location"):
            result += f"  Location: {event['location']}\n"
        if event.get("description"):
            result += f"  Description: {event['description']}\n"
    
    return result

@function_tool
def add_contact(name: str, email: Optional[str] = None, phone: Optional[str] = None, 
               address: Optional[str] = None, notes: Optional[str] = None) -> str:
    """
    Add a contact to your contacts list.
    
    Args:
        name: The name of the contact
        email: Optional email address of the contact
        phone: Optional phone number of the contact
        address: Optional address of the contact
        notes: Optional additional notes about the contact
    
    Returns:
        A confirmation message
    """
    result = contacts_add_contact(name, email, phone, address, notes)
    
    if "error" in result:
        return f"Error adding contact: {result['error']}"
    
    return f"Added contact '{name}' to your contacts list."

@function_tool
def find_contact(query: str) -> str:
    """
    Search for contacts by name, email, phone, or address.
    
    Args:
        query: The search query
    
    Returns:
        A list of matching contacts
    """
    contacts = contacts_search_contacts(query)
    
    if not contacts:
        return f"No contacts found matching '{query}'."
    
    result = f"Found {len(contacts)} contacts matching '{query}':\n\n"
    for contact in contacts:
        result += f"- {contact['name']}\n"
        if contact.get("email"):
            result += f"  Email: {contact['email']}\n"
        if contact.get("phone"):
            result += f"  Phone: {contact['phone']}\n"
        if contact.get("address"):
            result += f"  Address: {contact['address']}\n"
        if contact.get("notes"):
            result += f"  Notes: {contact['notes']}\n"
    
    return result

@function_tool
def list_all_contacts() -> str:
    """
    List all contacts.
    
    Returns:
        A list of all contacts
    """
    contacts = contacts_list_contacts()
    
    if not contacts:
        return "You have no contacts."
    
    result = f"You have {len(contacts)} contacts:\n\n"
    for contact in contacts:
        result += f"- {contact['name']}\n"
        if contact.get("email"):
            result += f"  Email: {contact['email']}\n"
        if contact.get("phone"):
            result += f"  Phone: {contact['phone']}\n"
    
    return result

@function_tool
def add_note(title: str, content: str, tags: Optional[str] = None) -> str:
    """
    Add a note.
    
    Args:
        title: The title of the note
        content: The content of the note
        tags: Optional comma-separated list of tags
    
    Returns:
        A confirmation message
    """
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    result = notes_add_note(title, content, tag_list)
    
    if "error" in result:
        return f"Error adding note: {result['error']}"
    
    return f"Added note '{title}' to your notes."

@function_tool
def find_note(query: str) -> str:
    """
    Search for notes by title, content, or tags.
    
    Args:
        query: The search query
    
    Returns:
        A list of matching notes
    """
    notes = notes_search_notes(query)
    
    if not notes:
        return f"No notes found matching '{query}'."
    
    result = f"Found {len(notes)} notes matching '{query}':\n\n"
    for note in notes:
        result += f"- ID: {note['id']} - {note['title']}\n"
        if note.get("tags"):
            result += f"  Tags: {', '.join(note['tags'])}\n"
        
        # Add a preview of the content (first 100 characters)
        content_preview = note['content'][:100] + "..." if len(note['content']) > 100 else note['content']
        result += f"  Preview: {content_preview}\n"
    
    return result

@function_tool
def get_note_by_id(note_id: int) -> str:
    """
    Get a note by its ID.
    
    Args:
        note_id: The ID of the note to retrieve
    
    Returns:
        The note content
    """
    result = notes_get_note(note_id)
    
    if "error" in result:
        return f"Error retrieving note: {result['error']}"
    
    note = result["note"]
    
    result_str = f"Title: {note['title']}\n"
    if note.get("tags"):
        result_str += f"Tags: {', '.join(note['tags'])}\n"
    
    created_at = datetime.datetime.fromisoformat(note["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
    result_str += f"Created: {created_at}\n\n"
    
    result_str += note["content"]
    
    return result_str

@function_tool
def list_all_notes() -> str:
    """
    List all notes.
    
    Returns:
        A list of all notes
    """
    notes = notes_list_notes()
    
    if not notes:
        return "You have no notes."
    
    result = f"You have {len(notes)} notes:\n\n"
    for note in notes:
        result += f"- ID: {note['id']} - {note['title']}\n"
        if note.get("tags"):
            result += f"  Tags: {', '.join(note['tags'])}\n"
    
    return result

@function_tool
def get_current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        The current date and time
    """
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

@function_tool
def get_integration_status() -> str:
    """
    Get the status of integrations.
    
    Returns:
        The status of all integrations
    """
    result = "Integration Status:\n\n"
    
    # Google Calendar
    if GOOGLE_CALENDAR_AVAILABLE:
        if get_calendar_service():
            result += "✅ Google Calendar: Connected\n"
        else:
            result += "❌ Google Calendar: Not connected (credentials missing or invalid)\n"
    else:
        result += "❌ Google Calendar: Not available (dependencies missing)\n"
    
    # Contacts
    contacts = contacts_list_contacts()
    result += f"✅ Contacts: Available ({len(contacts)} contacts)\n"
    
    # Notes
    notes = notes_list_notes()
    result += f"✅ Notes: Available ({len(notes)} notes)\n"
    
    return result

# Define the personal assistant agent
assistant = Agent(
    name="Integrated Personal Assistant",
    instructions="""
    You are a helpful personal assistant that can help with scheduling events, managing contacts, 
    taking notes, and answering questions. You should be polite, helpful, and concise in your responses.
    
    You have the following capabilities:
    
    1. Calendar Management:
       - Schedule events with dates, times, and optional details
       - List upcoming events
       - If Google Calendar integration is available, you'll use that; otherwise, you'll use local storage
    
    2. Contact Management:
       - Add contacts with names, emails, phone numbers, and addresses
       - Search for contacts
       - List all contacts
    
    3. Note Taking:
       - Add notes with titles, content, and optional tags
       - Search for notes by content or tags
       - Retrieve notes by ID
       - List all notes
    
    4. General Assistance:
       - Get the current time
       - Check the status of integrations
    
    When scheduling events, ask for the date, time, and event description if not provided.
    When adding contacts, ask for the name and other details if not provided.
    When taking notes, ask for the title and content if not provided.
    
    Always confirm actions with the user and provide helpful feedback.
    """,
    tools=[
        schedule_event,
        list_events,
        add_contact,
        find_contact,
        list_all_contacts,
        add_note,
        find_note,
        get_note_by_id,
        list_all_notes,
        get_current_time,
        get_integration_status
    ]
)

# Run the assistant
if __name__ == "__main__":
    print("Integrated Personal Assistant is ready to help!")
    print("Type 'exit' or 'quit' to end the conversation.")
    
    while True:
        user_input = input("\nHow can I assist you today? ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day!")
            break
        
        result = Runner.run_sync(assistant, user_input)
        print(result.final_output) 
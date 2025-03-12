"""
Google Calendar Integration for Personal Assistant

This module provides functions to interact with Google Calendar API.
"""

import os
import datetime
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Any

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path to store credentials
CREDENTIALS_DIR = Path("credentials")
CREDENTIALS_DIR.mkdir(exist_ok=True)

TOKEN_PATH = CREDENTIALS_DIR / "token.pickle"
CREDENTIALS_PATH = CREDENTIALS_DIR / "credentials.json"

def get_calendar_service():
    """
    Get an authorized Google Calendar service.
    
    Returns:
        A Google Calendar service object or None if authorization fails.
    """
    creds = None
    
    # Load the token.pickle file if it exists
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                print("Error: credentials.json file not found.")
                print("Please download your OAuth 2.0 credentials from the Google Cloud Console")
                print("and save them as 'credentials/credentials.json'.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building calendar service: {str(e)}")
        return None

def add_event(summary: str, start_time: datetime.datetime, 
              end_time: Optional[datetime.datetime] = None, 
              description: str = "", location: str = "") -> Dict[str, Any]:
    """
    Add an event to Google Calendar.
    
    Args:
        summary: The title of the event
        start_time: The start time of the event
        end_time: The end time of the event (defaults to 1 hour after start_time if not provided)
        description: Optional description of the event
        location: Optional location of the event
    
    Returns:
        The created event or an error message
    """
    service = get_calendar_service()
    if not service:
        return {"error": "Failed to authenticate with Google Calendar."}
    
    # Set end_time to 1 hour after start_time if not provided
    if not end_time:
        end_time = start_time + datetime.timedelta(hours=1)
    
    # Convert to UTC timezone for Google Calendar
    timezone = pytz.timezone('UTC')
    start_time_utc = timezone.localize(start_time) if start_time.tzinfo is None else start_time
    end_time_utc = timezone.localize(end_time) if end_time.tzinfo is None else end_time
    
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time_utc.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time_utc.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return {
            "success": True,
            "event_id": event.get('id'),
            "html_link": event.get('htmlLink'),
            "summary": summary,
            "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}

def get_events(time_min: Optional[datetime.datetime] = None, 
               time_max: Optional[datetime.datetime] = None, 
               max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Get events from Google Calendar.
    
    Args:
        time_min: The start time to retrieve events from (defaults to now)
        time_max: The end time to retrieve events to (defaults to 7 days from time_min)
        max_results: Maximum number of events to retrieve
    
    Returns:
        A list of events or an error message
    """
    service = get_calendar_service()
    if not service:
        return [{"error": "Failed to authenticate with Google Calendar."}]
    
    # Set default time range if not provided
    now = datetime.datetime.utcnow()
    if not time_min:
        time_min = now
    if not time_max:
        time_max = time_min + datetime.timedelta(days=7)
    
    # Convert to UTC timezone for Google Calendar
    timezone = pytz.timezone('UTC')
    time_min_utc = timezone.localize(time_min) if time_min.tzinfo is None else time_min
    time_max_utc = timezone.localize(time_max) if time_max.tzinfo is None else time_max
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min_utc.isoformat(),
            timeMax=time_max_utc.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return []
        
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Parse the datetime strings
            if 'T' in start:  # This is a dateTime, not just a date
                start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                # Convert to local timezone
                local_tz = datetime.datetime.now().astimezone().tzinfo
                start_dt = start_dt.astimezone(local_tz)
                end_dt = end_dt.astimezone(local_tz)
                start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                start_str = start
                end_str = end
            
            formatted_events.append({
                'summary': event.get('summary', 'No title'),
                'start': start_str,
                'end': end_str,
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'html_link': event.get('htmlLink', ''),
                'id': event.get('id', '')
            })
        
        return formatted_events
    
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

def delete_event(event_id: str) -> Dict[str, Any]:
    """
    Delete an event from Google Calendar.
    
    Args:
        event_id: The ID of the event to delete
    
    Returns:
        A success message or an error message
    """
    service = get_calendar_service()
    if not service:
        return {"error": "Failed to authenticate with Google Calendar."}
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"success": True, "message": f"Event {event_id} deleted successfully."}
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}

def update_event(event_id: str, summary: Optional[str] = None, 
                 start_time: Optional[datetime.datetime] = None,
                 end_time: Optional[datetime.datetime] = None, 
                 description: Optional[str] = None, 
                 location: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an event in Google Calendar.
    
    Args:
        event_id: The ID of the event to update
        summary: The new title of the event (if provided)
        start_time: The new start time of the event (if provided)
        end_time: The new end time of the event (if provided)
        description: The new description of the event (if provided)
        location: The new location of the event (if provided)
    
    Returns:
        The updated event or an error message
    """
    service = get_calendar_service()
    if not service:
        return {"error": "Failed to authenticate with Google Calendar."}
    
    try:
        # Get the existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update the fields that were provided
        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        
        # Update start and end times if provided
        timezone = pytz.timezone('UTC')
        if start_time:
            start_time_utc = timezone.localize(start_time) if start_time.tzinfo is None else start_time
            event['start'] = {
                'dateTime': start_time_utc.isoformat(),
                'timeZone': 'UTC',
            }
        if end_time:
            end_time_utc = timezone.localize(end_time) if end_time.tzinfo is None else end_time
            event['end'] = {
                'dateTime': end_time_utc.isoformat(),
                'timeZone': 'UTC',
            }
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary', eventId=event_id, body=event).execute()
        
        return {
            "success": True,
            "event_id": updated_event.get('id'),
            "html_link": updated_event.get('htmlLink'),
            "summary": updated_event.get('summary'),
            "message": "Event updated successfully."
        }
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}

def setup_google_calendar():
    """
    Guide the user through setting up Google Calendar integration.
    
    Returns:
        True if setup was successful, False otherwise
    """
    print("\n=== Google Calendar Integration Setup ===")
    print("To use Google Calendar integration, you need to:")
    print("1. Create a project in the Google Cloud Console")
    print("2. Enable the Google Calendar API")
    print("3. Create OAuth 2.0 credentials")
    print("4. Download the credentials.json file")
    print("5. Place the credentials.json file in the 'credentials' directory")
    
    if not CREDENTIALS_PATH.exists():
        print("\nCredentials file not found. Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Google Calendar API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download the credentials.json file")
        print("6. Place the file in the 'credentials' directory as 'credentials.json'")
        
        response = input("\nHave you completed these steps? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Test the connection
    service = get_calendar_service()
    if service:
        print("\nGoogle Calendar integration set up successfully!")
        return True
    else:
        print("\nFailed to set up Google Calendar integration.")
        return False

if __name__ == "__main__":
    # Run setup if executed directly
    setup_google_calendar() 
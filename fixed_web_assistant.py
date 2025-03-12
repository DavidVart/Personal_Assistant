#!/usr/bin/env python3
"""
Fixed Web Assistant - A reliable implementation
"""

import os
import datetime
import json
import re
import pickle
import pytz
from pathlib import Path
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session

# For Google Calendar integration
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Check if API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set your OpenAI API key in the .env file or as an environment variable.")
    exit(1)

# Set up OpenAI client
client = openai.OpenAI(api_key=api_key)

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Create credentials directory if it doesn't exist
credentials_dir = Path("credentials")
credentials_dir.mkdir(exist_ok=True)

# File paths for storing data
TODO_FILE = data_dir / "todos.json"
EVENTS_FILE = data_dir / "events.json"
NOTES_FILE = data_dir / "notes.json"
CONVERSATION_FILE = data_dir / "conversations.json"

# Google Calendar credentials
TOKEN_PATH = credentials_dir / "token.pickle"
CREDENTIALS_PATH = credentials_dir / "credentials.json"
# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Initialize data files if they don't exist
for file_path in [TODO_FILE, EVENTS_FILE, NOTES_FILE, CONVERSATION_FILE]:
    if not file_path.exists():
        with open(file_path, "w") as f:
            json.dump({} if file_path == CONVERSATION_FILE else [], f)

# Helper functions for data management
def load_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return [] if file_path != CONVERSATION_FILE else {}

def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def get_calendar_service():
    """
    Get an authorized Google Calendar service.
    
    Returns:
        A Google Calendar service object or None if authorization fails.
    """
    if not GOOGLE_CALENDAR_AVAILABLE:
        print("Google Calendar libraries not available. Please install them with:")
        print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
        
    creds = None
    
    # Load the token.pickle file if it exists
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {str(e)}")
                # If refresh fails, force re-authentication
                creds = None
                if TOKEN_PATH.exists():
                    os.remove(TOKEN_PATH)
        
        if not creds:
            if not CREDENTIALS_PATH.exists():
                print("Error: credentials.json file not found.")
                print("Please download your OAuth 2.0 credentials from the Google Cloud Console")
                print("and save them as 'credentials/credentials.json'.")
                return None
            
            try:
                # Set up the flow with offline access and force approval prompt
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, 
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                
                # Run the OAuth flow with browser
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(TOKEN_PATH, 'wb') as token:
                    pickle.dump(creds, token)
                    
                print("Successfully authenticated with Google Calendar!")
            except Exception as e:
                print(f"Error during authentication: {str(e)}")
                return None
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        # Test the connection with a simple API call
        service.calendarList().list().execute()
        print("Successfully connected to Google Calendar API")
        return service
    except Exception as e:
        print(f"Error building calendar service: {str(e)}")
        # If there's an error, try to delete the token and force re-authentication next time
        if TOKEN_PATH.exists():
            os.remove(TOKEN_PATH)
            print("Removed invalid token. Please try again to re-authenticate.")
        return None

def add_event_to_google_calendar(summary, start_time, end_time=None, description="", location=""):
    """
    Add an event to Google Calendar.
    
    Args:
        summary: The title of the event
        start_time: The start time of the event (datetime object)
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
        print(f"Attempting to add event to Google Calendar: {summary}")
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")
        
        return {
            "success": True,
            "event_id": event_result.get('id'),
            "html_link": event_result.get('htmlLink'),
            "summary": summary,
            "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
    except HttpError as error:
        error_details = f"An error occurred: {error}"
        print(f"Google Calendar API error: {error_details}")
        return {"error": error_details}
    except Exception as e:
        error_details = f"Unexpected error: {str(e)}"
        print(f"Unexpected error adding event to Google Calendar: {error_details}")
        return {"error": error_details}

# Function to schedule an event
def schedule_event(date, time, event, description="", location=""):
    try:
        # Convert 12-hour time format to 24-hour format if needed
        if "pm" in time.lower() and ":" in time:
            hour, minute = time.lower().replace("pm", "").strip().split(":")
            hour = int(hour)
            if hour < 12:
                hour += 12
            time = f"{hour}:{minute}"
        elif "pm" in time.lower():
            hour = int(time.lower().replace("pm", "").strip())
            if hour < 12:
                hour += 12
            time = f"{hour}:00"
        elif "am" in time.lower() and ":" in time:
            time = time.lower().replace("am", "").strip()
        elif "am" in time.lower():
            hour = time.lower().replace("am", "").strip()
            time = f"{hour}:00"
        
        # Handle times without minutes
        if ":" not in time:
            time = f"{time}:00"
        
        # Handle relative dates
        if date.lower() == "today":
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        elif date.lower() == "tomorrow":
            date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        print(f"DEBUG: Scheduling event with date={date}, time={time}, event={event}, location={location}")
        
        event_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Load existing events
        events = load_data(EVENTS_FILE)
        
        # Create new event
        new_event = {
            "id": len(events) + 1,
            "title": event,
            "description": description,
            "location": location,
            "date": date,
            "time": time,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Try to add to Google Calendar first if available
        google_calendar_result = None
        if GOOGLE_CALENDAR_AVAILABLE:
            try:
                print("Attempting to add event to Google Calendar...")
                end_time = event_datetime + datetime.timedelta(hours=1)
                google_calendar_result = add_event_to_google_calendar(
                    summary=event,
                    start_time=event_datetime,
                    end_time=end_time,
                    description=description,
                    location=location
                )
                
                if google_calendar_result and "success" in google_calendar_result:
                    print(f"DEBUG: Successfully added event to Google Calendar: {google_calendar_result}")
                    # Add Google Calendar ID to local event
                    new_event["google_calendar_id"] = google_calendar_result.get("event_id")
                    new_event["google_calendar_link"] = google_calendar_result.get("html_link")
                else:
                    print(f"DEBUG: Failed to add event to Google Calendar: {google_calendar_result}")
            except Exception as e:
                print(f"DEBUG: Error adding event to Google Calendar: {str(e)}")
        
        # Add to events list
        events.append(new_event)
        
        # Save updated events
        save_data(EVENTS_FILE, events)
        
        result = f"Scheduled '{event}' on {event_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}."
        if google_calendar_result and "success" in google_calendar_result:
            result += f" Event has been added to your Google Calendar: {google_calendar_result.get('html_link')}"
        
        return result
    except ValueError as e:
        print(f"DEBUG: Error scheduling event: {str(e)}")
        return f"Error: {str(e)}. Please provide date in YYYY-MM-DD format and time in HH:MM format."

def test_google_calendar_connection():
    """Test the Google Calendar connection and return detailed status"""
    status = {
        "google_calendar_available": GOOGLE_CALENDAR_AVAILABLE,
        "credentials_exist": CREDENTIALS_PATH.exists(),
        "token_exists": TOKEN_PATH.exists(),
        "connected": False,
        "calendars": [],
        "error": None
    }
    
    if not GOOGLE_CALENDAR_AVAILABLE:
        status["error"] = "Google Calendar libraries not installed"
        return status
    
    if not CREDENTIALS_PATH.exists():
        status["error"] = "credentials.json file not found"
        return status
    
    try:
        service = get_calendar_service()
        if not service:
            status["error"] = "Failed to get calendar service"
            return status
        
        # Test the connection by listing calendars
        calendar_list = service.calendarList().list().execute()
        status["connected"] = True
        
        # Get list of calendars
        for calendar_entry in calendar_list.get('items', []):
            status["calendars"].append({
                "id": calendar_entry['id'],
                "summary": calendar_entry['summary'],
                "primary": calendar_entry.get('primary', False)
            })
        
        # Test creating a temporary event
        now = datetime.datetime.utcnow()
        test_event = {
            'summary': 'Test Event - Please ignore',
            'description': 'This is a test event to verify calendar access',
            'start': {
                'dateTime': now.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (now + datetime.timedelta(minutes=5)).isoformat() + 'Z',
                'timeZone': 'UTC',
            },
        }
        
        try:
            test_result = service.events().insert(calendarId='primary', body=test_event).execute()
            status["test_event_created"] = True
            status["test_event_link"] = test_result.get('htmlLink')
            
            # Delete the test event
            service.events().delete(calendarId='primary', eventId=test_result['id']).execute()
            status["test_event_deleted"] = True
        except Exception as e:
            status["test_event_created"] = False
            status["test_event_error"] = str(e)
    
    except Exception as e:
        status["error"] = str(e)
    
    return status

# Function to list events
def list_events(date=None):
    events = load_data(EVENTS_FILE)
    
    if date:
        # Filter events by date
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
        if event.get("google_calendar_link"):
            result += f"  Google Calendar: {event['google_calendar_link']}\n"
    
    return result

# Function to add a todo
def add_todo(task, priority=None, due_date=None):
    # Use medium as the default priority if none is provided
    if priority is None:
        priority = "medium"
    
    # Validate priority
    if priority.lower() not in ["low", "medium", "high"]:
        return f"Error: Priority must be 'low', 'medium', or 'high'. Got '{priority}'."
    
    # Validate due_date if provided
    if due_date:
        try:
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return "Error: Due date must be in YYYY-MM-DD format."
    
    # Load existing todos
    todos = load_data(TODO_FILE)
    
    # Create new todo
    new_todo = {
        "id": len(todos) + 1,
        "task": task,
        "priority": priority.lower(),
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Add to todos list
    todos.append(new_todo)
    
    # Save updated todos
    save_data(TODO_FILE, todos)
    
    due_date_msg = f" (due on {due_date})" if due_date else ""
    return f"Added task '{task}' with {priority} priority{due_date_msg} to your to-do list."

# Function to list todos
def list_todos(priority=None, show_completed=False):
    todos = load_data(TODO_FILE)
    
    # Filter by completion status
    if not show_completed:
        todos = [todo for todo in todos if not todo["completed"]]
    
    # Filter by priority if specified
    if priority:
        if priority.lower() not in ["low", "medium", "high"]:
            return f"Error: Priority must be 'low', 'medium', or 'high'. Got '{priority}'."
        todos = [todo for todo in todos if todo["priority"] == priority.lower()]
    
    if not todos:
        return "No tasks found." if priority else "Your to-do list is empty."
    
    # Format todos for display
    result = "Here are your to-do items:\n\n"
    for todo in todos:
        status = "[✓]" if todo["completed"] else "[ ]"
        priority_symbol = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(todo["priority"], "")
        
        due_date = f" (due: {todo['due_date']})" if todo["due_date"] else ""
        result += f"{todo['id']}. {status} {priority_symbol} {todo['task']}{due_date}\n"
    
    return result

# Function to add a note
def add_note(title, content):
    # Load existing notes
    notes = load_data(NOTES_FILE)
    
    # Create new note
    new_note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    # Add to notes list
    notes.append(new_note)
    
    # Save updated notes
    save_data(NOTES_FILE, notes)
    
    return f"Added note '{title}' to your notes."

# Function to list notes
def list_notes():
    notes = load_data(NOTES_FILE)
    
    if not notes:
        return "You have no notes."
    
    # Format notes for display
    result = "Here are your notes:\n\n"
    for note in notes:
        created_at = datetime.datetime.fromisoformat(note["created_at"]).strftime("%Y-%m-%d %H:%M")
        result += f"ID: {note['id']} - {note['title']} (created: {created_at})\n"
    
    return result

# Function to save conversation history
def save_conversation(session_id, messages):
    conversations = load_data(CONVERSATION_FILE)
    conversations[session_id] = messages
    save_data(CONVERSATION_FILE, conversations)

# Function to load conversation history
def load_conversation(session_id):
    conversations = load_data(CONVERSATION_FILE)
    return conversations.get(session_id, [])

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'response': 'Please provide a message.'}), 400
        
        print(f"Received message: {user_message}")
        
        # Load conversation history for this session
        conversation_history = load_conversation(session_id)
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare messages for OpenAI API
        messages = [
            {"role": "system", "content": f"""
            You are a helpful personal assistant with a web interface that can help with scheduling events, 
            managing to-do lists, taking notes, and answering questions. You should be polite, helpful, 
            and concise in your responses.
            
            The current date and time is: {datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
            
            You have access to the following functions:
            - schedule_event(date, time, event, description, location): Schedule an event on a specific date and time
            - list_events(date): List scheduled events, optionally filtered by date
            - add_todo(task, priority, due_date): Add a task to the to-do list
            - list_todos(priority, show_completed): List tasks in the to-do list
            - add_note(title, content): Add a note with a title and content
            - list_notes(): List all notes
            
            When the user asks to perform one of these actions, I will actually perform them.
            For example, if they ask to schedule a meeting, I will extract the details and schedule it.
            
            When users ask about their calendar or events, you can list events from the local storage.
            """}
        ]
        
        # Add conversation history (limited to last 10 messages to avoid token limits)
        messages.extend(conversation_history[-10:])
        
        # Process the message with OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Save updated conversation history
        save_conversation(session_id, conversation_history)
        
        # Check if we need to perform any actions based on the user's message and response
        lower_message = user_message.lower()
        
        # Handle scheduling events
        if ("schedule" in lower_message or "add to calendar" in lower_message or "put on calendar" in lower_message) and \
           ("meeting" in lower_message or "event" in lower_message or "appointment" in lower_message or "chat" in lower_message):
            try:
                # Extract date
                date_str = None
                if "tomorrow" in lower_message:
                    date_str = "tomorrow"
                elif "today" in lower_message:
                    date_str = "today"
                else:
                    # Try to find a date in YYYY-MM-DD format
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', lower_message)
                    if date_match:
                        date_str = date_match.group(0)
                
                # Extract time
                time_str = None
                time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', lower_message, re.IGNORECASE)
                if time_match:
                    if time_match.group(2):  # Has minutes
                        time_str = f"{time_match.group(1)}{time_match.group(2)} {time_match.group(3)}"
                    else:  # No minutes
                        time_str = f"{time_match.group(1)} {time_match.group(3)}"
                
                # Extract event title
                event_title = "Meeting"
                if "coffee" in lower_message and "chat" in lower_message:
                    event_title = "Coffee Chat"
                    if "with" in lower_message:
                        parts = lower_message.split("with")
                        if len(parts) > 1:
                            person = parts[1].split()[0].strip()
                            event_title = f"Coffee Chat with {person}"
                
                # Extract location
                location = ""
                if "at" in lower_message:
                    parts = lower_message.split("at")
                    if len(parts) > 1:
                        location_parts = parts[1].split()
                        if len(location_parts) > 0:
                            # Take up to 3 words after "at" as the location
                            location = " ".join(location_parts[:3])
                
                print(f"DEBUG: Extracted date={date_str}, time={time_str}, event={event_title}, location={location}")
                
                # If we have enough information, schedule the event
                if date_str and time_str:
                    result = schedule_event(date_str, time_str, event_title, "", location)
                    print(f"DEBUG: Schedule result: {result}")
                    # Update the response to confirm the scheduling
                    response_text = f"I've scheduled the {event_title} for {date_str} at {time_str}"
                    if location:
                        response_text += f" at {location}"
                    response_text += "."
                    
                    # Add Google Calendar info if available
                    if "Google Calendar" in result:
                        response_text += " The event has also been added to your Google Calendar."
            except Exception as e:
                print(f"DEBUG: Error scheduling event: {str(e)}")
        
        # Handle listing events
        elif "list events" in lower_message or "show events" in lower_message or "what events" in lower_message or "my calendar" in lower_message:
            try:
                date_str = None
                if "tomorrow" in lower_message:
                    date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                elif "today" in lower_message:
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                
                events_list = list_events(date_str)
                response_text = events_list
            except Exception as e:
                print(f"Error listing events: {str(e)}")
        
        # Handle adding todos
        elif "add todo" in lower_message or "add task" in lower_message or "add to my to-do list" in lower_message:
            try:
                # Simple extraction of task
                task = "Task"
                if "'" in lower_message:
                    task = lower_message.split("'")[1]
                
                # Extract priority
                priority = "medium"
                if "high priority" in lower_message:
                    priority = "high"
                elif "low priority" in lower_message:
                    priority = "low"
                
                add_todo(task, priority)
            except Exception as e:
                print(f"Error adding todo: {str(e)}")
        
        # Handle listing todos
        elif "list todos" in lower_message or "show todos" in lower_message or "show my to-do list" in lower_message:
            try:
                todos_list = list_todos()
                response_text = todos_list
            except Exception as e:
                print(f"Error listing todos: {str(e)}")
        
        print(f"Response: {response_text}")
        return jsonify({'response': response_text})
    except Exception as e:
        import traceback
        print(f"Error processing message: {str(e)}")
        traceback.print_exc()
        return jsonify({'response': f"I'm sorry, I encountered an error: {str(e)}"}), 500

# Run the app
if __name__ == "__main__":
    print("Fixed Web Assistant is starting...")
    print("Open http://localhost:5000 in your browser")
    
    # Check Google Calendar availability
    if GOOGLE_CALENDAR_AVAILABLE:
        print("Google Calendar integration is available.")
        # Test Google Calendar connection
        service = get_calendar_service()
        if service:
            print("Successfully connected to Google Calendar.")
        else:
            print("Failed to connect to Google Calendar. Please check your credentials.")
    else:
        print("Google Calendar integration is not available. Install required packages:")
        print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz")
    
    # Add debug endpoints
    @app.route('/api/debug/events')
    def debug_events():
        """Debug endpoint to list all events"""
        events = load_data(EVENTS_FILE)
        return jsonify(events)
    
    @app.route('/api/debug/clear-events', methods=['POST'])
    def debug_clear_events():
        """Debug endpoint to clear all events"""
        save_data(EVENTS_FILE, [])
        return jsonify({"status": "success", "message": "All events cleared"})
    
    @app.route('/api/debug/conversations')
    def debug_conversations():
        """Debug endpoint to list all conversations"""
        conversations = load_data(CONVERSATION_FILE)
        return jsonify(conversations)
    
    @app.route('/api/debug/google-calendar-status')
    def debug_google_calendar_status():
        """Debug endpoint to check Google Calendar status"""
        status = test_google_calendar_connection()
        return jsonify(status)
    
    @app.route('/api/debug/reset-google-auth', methods=['POST'])
    def debug_reset_google_auth():
        """Debug endpoint to reset Google Calendar authentication"""
        if TOKEN_PATH.exists():
            os.remove(TOKEN_PATH)
            return jsonify({"status": "success", "message": "Google Calendar authentication reset. Please try scheduling an event again to re-authenticate."})
        else:
            return jsonify({"status": "error", "message": "No token file found to reset."})
    
    app.run(debug=True, port=5000) 
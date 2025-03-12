import os
import datetime
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

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

# File paths for storing data
TODO_FILE = data_dir / "todos.json"
EVENTS_FILE = data_dir / "events.json"
NOTES_FILE = data_dir / "notes.json"

# Initialize data files if they don't exist
for file_path in [TODO_FILE, EVENTS_FILE, NOTES_FILE]:
    if not file_path.exists():
        with open(file_path, "w") as f:
            json.dump([], f)

# Helper functions for data management
def load_data(file_path: Path) -> List[Dict]:
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(file_path: Path, data: List[Dict]) -> None:
    """Save data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# Define function tools for the assistant

@function_tool
def schedule_event(date: str, time: str, event: str, description: str = ""):
    """
    Schedule an event on a specific date and time.
    
    Args:
        date: The date in YYYY-MM-DD format
        time: The time in HH:MM format
        event: The name or title of the event
        description: Optional detailed description of the event
    
    Returns:
        A confirmation message
    """
    try:
        event_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Load existing events
        events = load_data(EVENTS_FILE)
        
        # Create new event
        new_event = {
            "id": len(events) + 1,
            "title": event,
            "description": description,
            "date": date,
            "time": time,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Add to events list
        events.append(new_event)
        
        # Save updated events
        save_data(EVENTS_FILE, events)
        
        return f"Scheduled '{event}' on {event_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}."
    except ValueError as e:
        return f"Error: {str(e)}. Please provide date in YYYY-MM-DD format and time in HH:MM format."

@function_tool
def list_events(date: Optional[str] = None):
    """
    List scheduled events, optionally filtered by date.
    
    Args:
        date: Optional date in YYYY-MM-DD format to filter events
    
    Returns:
        A list of events
    """
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
        if event["description"]:
            result += f"  Description: {event['description']}\n"
    
    return result

@function_tool
def add_todo(task: str, priority: Optional[str] = None, due_date: Optional[str] = None):
    """
    Add a task to the to-do list.
    
    Args:
        task: The task description
        priority: The priority level (low, medium, high)
        due_date: Optional due date in YYYY-MM-DD format
    
    Returns:
        A confirmation message
    """
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

@function_tool
def list_todos(priority: Optional[str] = None, show_completed: bool = False):
    """
    List tasks in the to-do list, optionally filtered by priority.
    
    Args:
        priority: Optional priority level to filter tasks (low, medium, high)
        show_completed: Whether to include completed tasks
    
    Returns:
        A list of tasks
    """
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
        result += f"{status} {priority_symbol} {todo['task']}{due_date}\n"
    
    return result

@function_tool
def complete_todo(task_id: int):
    """
    Mark a task as completed.
    
    Args:
        task_id: The ID of the task to mark as completed
    
    Returns:
        A confirmation message
    """
    todos = load_data(TODO_FILE)
    
    # Find the task by ID
    for todo in todos:
        if todo["id"] == task_id:
            if todo["completed"]:
                return f"Task '{todo['task']}' is already marked as completed."
            
            todo["completed"] = True
            save_data(TODO_FILE, todos)
            return f"Marked task '{todo['task']}' as completed."
    
    return f"Error: No task found with ID {task_id}."

@function_tool
def add_note(title: str, content: str):
    """
    Add a note with a title and content.
    
    Args:
        title: The title of the note
        content: The content of the note
    
    Returns:
        A confirmation message
    """
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

@function_tool
def list_notes():
    """
    List all notes.
    
    Returns:
        A list of notes
    """
    notes = load_data(NOTES_FILE)
    
    if not notes:
        return "You have no notes."
    
    # Format notes for display
    result = "Here are your notes:\n\n"
    for note in notes:
        created_at = datetime.datetime.fromisoformat(note["created_at"]).strftime("%Y-%m-%d %H:%M")
        result += f"ID: {note['id']} - {note['title']} (created: {created_at})\n"
    
    return result

@function_tool
def get_note(note_id: int):
    """
    Get the content of a specific note.
    
    Args:
        note_id: The ID of the note to retrieve
    
    Returns:
        The note content
    """
    notes = load_data(NOTES_FILE)
    
    # Find the note by ID
    for note in notes:
        if note["id"] == note_id:
            created_at = datetime.datetime.fromisoformat(note["created_at"]).strftime("%Y-%m-%d %H:%M")
            return f"Title: {note['title']}\nCreated: {created_at}\n\n{note['content']}"
    
    return f"Error: No note found with ID {note_id}."

@function_tool
def get_current_time():
    """
    Get the current date and time.
    
    Returns:
        The current date and time
    """
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

# Define the personal assistant agent
assistant = Agent(
    name="Advanced Personal Assistant",
    instructions="""
    You are a helpful personal assistant that can help with scheduling events, managing to-do lists, 
    taking notes, and answering questions. You should be polite, helpful, and concise in your responses.
    
    When scheduling events, ask for the date, time, and event description if not provided.
    When adding tasks to the to-do list, ask for the task description and priority if not provided.
    When taking notes, ask for the title and content if not provided.
    
    Always confirm actions with the user and provide helpful feedback.
    
    Here are some examples of what you can do:
    - Schedule an event: "Schedule a meeting with John on Friday at 2pm"
    - List events: "What events do I have scheduled for tomorrow?"
    - Add a task: "Add 'Buy groceries' to my to-do list with high priority"
    - List tasks: "Show me my to-do list"
    - Mark a task as completed: "Mark task 3 as completed"
    - Add a note: "Take a note about the project meeting"
    - List notes: "Show me my notes"
    - Get a note: "Show me note 2"
    - Get the current time: "What time is it?"
    """,
    tools=[
        schedule_event, 
        list_events, 
        add_todo, 
        list_todos, 
        complete_todo, 
        add_note, 
        list_notes, 
        get_note, 
        get_current_time
    ]
)

# Run the assistant
if __name__ == "__main__":
    print("Advanced Personal Assistant is ready to help!")
    print("Type 'exit' or 'quit' to end the conversation.")
    
    while True:
        user_input = input("\nHow can I assist you today? ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day!")
            break
        
        result = Runner.run_sync(assistant, user_input)
        print(result.final_output) 
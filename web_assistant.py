import os
import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
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
    name="Web Personal Assistant",
    instructions="""
    You are a helpful personal assistant with a web interface that can help with scheduling events, 
    managing to-do lists, taking notes, and answering questions. You should be polite, helpful, 
    and concise in your responses.
    
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

# Create Flask app
app = Flask(__name__)

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Create static directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Create HTML template
with open(templates_dir / "index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Assistant</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>Personal Assistant</h1>
        </header>
        
        <div class="chat-container">
            <div id="chat-messages" class="chat-messages">
                <div class="message assistant">
                    <div class="message-content">
                        Hello! I'm your personal assistant. How can I help you today?
                    </div>
                </div>
            </div>
            
            <div class="chat-input">
                <form id="message-form">
                    <input type="text" id="user-input" placeholder="Type your message here..." autocomplete="off">
                    <button type="submit">Send</button>
                </form>
            </div>
        </div>
        
        <div class="examples">
            <h3>Examples:</h3>
            <ul>
                <li><a href="#" class="example-link">Schedule a meeting with John on Friday at 2pm</a></li>
                <li><a href="#" class="example-link">What events do I have scheduled for tomorrow?</a></li>
                <li><a href="#" class="example-link">Add 'Buy groceries' to my to-do list with high priority</a></li>
                <li><a href="#" class="example-link">Show me my to-do list</a></li>
                <li><a href="#" class="example-link">Take a note about the project meeting</a></li>
            </ul>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
    """)

# Create CSS file
with open(static_dir / "style.css", "w") as f:
    f.write("""
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background-color: #f5f5f5;
    color: #333;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 20px;
}

header h1 {
    color: #2c3e50;
}

.chat-container {
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 20px;
}

.chat-messages {
    height: 400px;
    overflow-y: auto;
    padding: 20px;
}

.message {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
}

.message.user {
    align-items: flex-end;
}

.message.assistant {
    align-items: flex-start;
}

.message-content {
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 80%;
    word-wrap: break-word;
}

.message.user .message-content {
    background-color: #3498db;
    color: white;
    border-bottom-right-radius: 5px;
}

.message.assistant .message-content {
    background-color: #e9e9eb;
    color: #333;
    border-bottom-left-radius: 5px;
}

.chat-input {
    padding: 15px;
    border-top: 1px solid #e0e0e0;
}

#message-form {
    display: flex;
}

#user-input {
    flex: 1;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 20px;
    outline: none;
    font-size: 16px;
}

button {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 20px;
    margin-left: 10px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #2980b9;
}

.examples {
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.examples h3 {
    margin-bottom: 10px;
    color: #2c3e50;
}

.examples ul {
    list-style-type: none;
}

.examples li {
    margin-bottom: 8px;
}

.example-link {
    color: #3498db;
    text-decoration: none;
    cursor: pointer;
}

.example-link:hover {
    text-decoration: underline;
}

pre {
    white-space: pre-wrap;
    font-family: monospace;
    background-color: #f8f8f8;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
    """)

# Create JavaScript file
with open(static_dir / "script.js", "w") as f:
    f.write("""
document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const exampleLinks = document.querySelectorAll('.example-link');
    
    // Function to add a message to the chat
    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Replace newlines with <br> tags
        content = content.replace(/\\n/g, '<br>');
        
        messageContent.innerHTML = content;
        messageDiv.appendChild(messageContent);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to send a message to the assistant
    async function sendMessage(message) {
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input field
        userInput.value = '';
        
        try {
            // Show loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant';
            const loadingContent = document.createElement('div');
            loadingContent.className = 'message-content';
            loadingContent.textContent = 'Thinking...';
            loadingDiv.appendChild(loadingContent);
            chatMessages.appendChild(loadingDiv);
            
            // Send request to server
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            if (response.ok) {
                const data = await response.json();
                // Add assistant response to chat
                addMessage(data.response, false);
            } else {
                // Add error message
                addMessage('Sorry, I encountered an error. Please try again.', false);
            }
        } catch (error) {
            console.error('Error:', error);
            // Add error message
            addMessage('Sorry, I encountered an error. Please try again.', false);
        }
    }
    
    // Handle form submission
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    });
    
    // Handle example link clicks
    exampleLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.textContent;
            userInput.value = message;
            sendMessage(message);
        });
    });
    
    // Focus on input field when page loads
    userInput.focus();
});
    """)

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please provide a message.'}), 400
    
    try:
        # Process the message with the assistant
        result = Runner.run_sync(assistant, user_message)
        return jsonify({'response': result.final_output})
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'response': f"I'm sorry, I encountered an error: {str(e)}"}), 500

# Run the app
if __name__ == "__main__":
    print("Web Personal Assistant is starting...")
    app.run(debug=True, port=5000) 
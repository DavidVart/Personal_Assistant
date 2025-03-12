import os
import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Check if API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set your OpenAI API key in the .env file or as an environment variable.")
    exit(1)

# Define function tools for the assistant

@function_tool
def schedule_event(date: str, time: str, event: str):
    """
    Schedule an event on a specific date and time.
    
    Args:
        date: The date in YYYY-MM-DD format
        time: The time in HH:MM format
        event: The name or description of the event
    
    Returns:
        A confirmation message
    """
    try:
        event_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        # Here you would integrate with a calendar API to actually schedule the event
        return f"Scheduled '{event}' on {event_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}."
    except ValueError as e:
        return f"Error: {str(e)}. Please provide date in YYYY-MM-DD format and time in HH:MM format."

@function_tool
def get_date_info(days_offset: int = 0):
    """
    Get information about a specific date relative to today.
    
    Args:
        days_offset: Number of days from today (0 = today, 1 = tomorrow, -1 = yesterday)
    
    Returns:
        Information about the date
    """
    target_date = datetime.datetime.now() + datetime.timedelta(days=days_offset)
    
    if days_offset == 0:
        day_name = "Today"
    elif days_offset == 1:
        day_name = "Tomorrow"
    elif days_offset == -1:
        day_name = "Yesterday"
    else:
        day_name = target_date.strftime("%A")
    
    return {
        "date_string": target_date.strftime("%Y-%m-%d"),
        "formatted_date": target_date.strftime("%A, %B %d, %Y"),
        "day_name": day_name,
        "day_of_week": target_date.strftime("%A"),
        "month": target_date.strftime("%B"),
        "day": target_date.day,
        "year": target_date.year
    }

@function_tool
def explain_calendar_capabilities():
    """
    Explain the calendar capabilities of the basic assistant.
    
    Returns:
        An explanation of calendar capabilities
    """
    return """
    In the basic assistant mode, I can help you schedule events, but I don't have access to your actual calendar.
    
    The events you schedule with me are not integrated with any external calendar service like Google Calendar.
    
    If you need actual calendar integration, please use the integrated assistant mode:
    ./run.py --mode integrated
    
    The integrated mode connects with Google Calendar and provides real calendar management.
    """

@function_tool
def add_todo(task: str, priority: Optional[str] = None):
    """
    Add a task to the to-do list.
    
    Args:
        task: The task description
        priority: The priority level (low, medium, high)
    
    Returns:
        A confirmation message
    """
    # Use medium as the default priority if none is provided
    if priority is None:
        priority = "medium"
    
    # Here you would integrate with a to-do list API or database
    return f"Added task '{task}' with {priority} priority to your to-do list."

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
    name="Personal Assistant",
    instructions="""
    You are a helpful personal assistant that can help with scheduling events, managing to-do lists, 
    and answering questions. You should be polite, helpful, and concise in your responses.
    
    When scheduling events, ask for the date, time, and event description if not provided.
    When adding tasks to the to-do list, ask for the task description and priority if not provided.
    
    Always confirm actions with the user and provide helpful feedback.
    
    Important notes about calendar functionality:
    - In basic mode, you can schedule events but they are not connected to any real calendar system
    - If the user asks about their calendar or events, explain that the basic assistant doesn't have access to their actual calendar
    - Suggest using the integrated assistant mode for real calendar integration
    
    You have access to the current date and time, and can provide information about dates (today, tomorrow, etc.).
    """,
    tools=[schedule_event, get_date_info, explain_calendar_capabilities, add_todo, get_current_time]
)

# Run the assistant
if __name__ == "__main__":
    print("Personal Assistant is ready to help!")
    print("Type 'exit' or 'quit' to end the conversation.")
    
    while True:
        user_input = input("\nHow can I assist you today? ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day!")
            break
        
        result = Runner.run_sync(assistant, user_input)
        print(result.final_output) 
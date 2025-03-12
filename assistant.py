import os
import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

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
def add_todo(task: str, priority: str = "medium"):
    """
    Add a task to the to-do list.
    
    Args:
        task: The task description
        priority: The priority level (low, medium, high)
    
    Returns:
        A confirmation message
    """
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
    """,
    tools=[schedule_event, add_todo, get_current_time]
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
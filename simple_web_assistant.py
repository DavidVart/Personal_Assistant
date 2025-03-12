#!/usr/bin/env python3
"""
Simple Web Assistant for debugging purposes
"""

import os
import datetime
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

# Define a simple function tool
@function_tool
def get_current_time():
    """
    Get the current date and time.
    
    Returns:
        The current date and time
    """
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

@function_tool
def echo_message(message: str):
    """
    Echo back the user's message.
    
    Args:
        message: The message to echo back
    
    Returns:
        The echoed message
    """
    return f"You said: {message}"

# Define the personal assistant agent
assistant = Agent(
    name="Simple Web Assistant",
    instructions="""
    You are a simple web assistant for debugging purposes.
    You can tell the current time and echo back messages.
    Be concise in your responses.
    """,
    tools=[get_current_time, echo_message]
)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'response': 'Please provide a message.'}), 400
        
        print(f"Received message: {user_message}")
        
        # Process the message with the assistant
        result = Runner.run_sync(assistant, user_message)
        response_text = result.final_output
        
        print(f"Response: {response_text}")
        
        return jsonify({'response': response_text})
    except Exception as e:
        import traceback
        print(f"Error processing message: {str(e)}")
        traceback.print_exc()
        return jsonify({'response': f"Debug error: {str(e)}"}), 500

# Run the app
if __name__ == "__main__":
    print("Simple Web Assistant is starting...")
    print("Open http://localhost:5001 in your browser")
    app.run(debug=True, port=5001) 
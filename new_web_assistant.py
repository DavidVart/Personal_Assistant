#!/usr/bin/env python3
"""
New Web Assistant - A completely new implementation
"""

import os
import datetime
import json
from pathlib import Path
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

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
def load_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

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
        
        # Process the message with OpenAI directly
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                You are a helpful personal assistant with a web interface that can help with scheduling events, 
                managing to-do lists, taking notes, and answering questions. You should be polite, helpful, 
                and concise in your responses.
                
                The current date and time is: """ + datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p') + """
                
                When users ask about their calendar or events, explain that you're a basic assistant and don't have 
                access to their actual calendar. Suggest using the integrated assistant mode for real calendar integration.
                """},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        print(f"Response: {response_text}")
        
        return jsonify({'response': response_text})
    except Exception as e:
        import traceback
        print(f"Error processing message: {str(e)}")
        traceback.print_exc()
        return jsonify({'response': f"Debug error: {str(e)}"}), 500

# Run the app
if __name__ == "__main__":
    print("New Web Assistant is starting...")
    print("Open http://localhost:5002 in your browser")
    app.run(debug=True, port=5002) 
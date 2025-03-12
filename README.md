# Personal Assistant

A personal assistant built using OpenAI's Agents SDK that helps manage schedules, tasks, and more.

## Features

- Schedule events and appointments
- Manage to-do lists
- Take and retrieve notes
- Answer questions
- Web interface for easy interaction

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal-assistant.git
   cd personal-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'  # On Windows: set OPENAI_API_KEY='your-api-key-here'
   ```
   
   Alternatively, you can create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Running the Assistant

You can run the assistant in three different modes:

1. **Basic Mode** - Simple command-line assistant with basic functionality:
   ```bash
   ./run.py --mode basic
   ```

2. **Advanced Mode** - Command-line assistant with advanced functionality:
   ```bash
   ./run.py --mode advanced
   ```

3. **Web Mode** - Web interface for the assistant:
   ```bash
   ./run.py --mode web
   ```
   
   By default, the web server runs on port 5000. You can specify a different port:
   ```bash
   ./run.py --mode web --port 8080
   ```

### Example Commands

Here are some examples of what you can ask the assistant:

- "Schedule a meeting with John on Friday at 2pm"
- "What events do I have scheduled for tomorrow?"
- "Add 'Buy groceries' to my to-do list with high priority"
- "Show me my to-do list"
- "Mark task 3 as completed"
- "Take a note about the project meeting"
- "Show me my notes"
- "Show me note 2"
- "What time is it?"

## Project Structure

- `assistant.py` - Basic personal assistant implementation
- `advanced_assistant.py` - Advanced personal assistant with more features
- `web_assistant.py` - Web interface for the personal assistant
- `run.py` - Script to run the assistant in different modes
- `data/` - Directory for storing assistant data (events, todos, notes)
- `templates/` - HTML templates for the web interface
- `static/` - Static files (CSS, JavaScript) for the web interface

## Requirements

- Python 3.8+
- OpenAI API key

## License

This project is licensed under the MIT License - see the LICENSE file for details.
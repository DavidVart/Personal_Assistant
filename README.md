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

2. Run the setup script:
   
   On macOS/Linux:
   ```bash
   ./setup.sh
   ```
   
   On Windows:
   ```
   setup.bat
   ```
   
   This script will:
   - Create a virtual environment
   - Install dependencies
   - Create necessary directories
   - Prompt for your OpenAI API key if not already set
   - Make scripts executable (on macOS/Linux)

3. Alternatively, you can set up manually:

   a. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

   b. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   c. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'  # On Windows: set OPENAI_API_KEY='your-api-key-here'
   ```
   
   Alternatively, you can create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. Verify your environment:
   ```bash
   ./check_environment.py
   ```
   This script will check if your environment is properly set up and provide guidance on fixing any issues.

## Usage

### Running the Assistant

You can run the assistant in four different modes:

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

4. **Integrated Mode** - Command-line assistant with integrations for Google Calendar, contacts, and notes:
   ```bash
   ./run.py --mode integrated
   ```
   
   To set up the integrations, run:
   ```bash
   ./run.py --mode integrated --setup
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
- "Add John Doe to my contacts with email john@example.com and phone 555-1234"
- "Find contacts with 'John' in their name"
- "Show me all my contacts"
- "Check integration status"

## Integrations

The integrated assistant supports the following integrations:

### Google Calendar

To use Google Calendar integration, you need to:

1. Create a project in the Google Cloud Console
2. Enable the Google Calendar API
3. Create OAuth 2.0 credentials
4. Download the credentials.json file
5. Place the credentials.json file in the 'credentials' directory

You can set up the Google Calendar integration by running:
```bash
./run.py --mode integrated --setup
```

### Contacts

The contacts integration allows you to:

- Add contacts with names, emails, phone numbers, and addresses
- Search for contacts
- List all contacts

### Notes

The notes integration allows you to:

- Add notes with titles, content, and optional tags
- Search for notes by content or tags
- Retrieve notes by ID
- List all notes

## Project Structure

- `assistant.py` - Basic personal assistant implementation
- `advanced_assistant.py` - Advanced personal assistant with more features
- `web_assistant.py` - Web interface for the personal assistant
- `integrated_assistant.py` - Integrated personal assistant with external integrations
- `run.py` - Script to run the assistant in different modes
- `setup_integrations.py` - Script to set up integrations
- `test_integrated_assistant.py` - Script to test the integrated assistant
- `check_environment.py` - Script to check if the environment is properly set up
- `setup.sh` / `setup.bat` - Setup scripts for macOS/Linux and Windows
- `data/` - Directory for storing assistant data (events, todos, notes, contacts)
- `credentials/` - Directory for storing API credentials
- `integrations/` - Directory containing integration modules
  - `__init__.py` - Integration package initialization
  - `google_calendar.py` - Google Calendar integration
  - `contacts.py` - Contacts management
  - `notes.py` - Notes management
- `templates/` - HTML templates for the web interface
- `static/` - Static files (CSS, JavaScript) for the web interface
- `CONTRIBUTING.md` - Guidelines for contributing to the project
- `INTEGRATIONS.md` - Detailed information about the integrations

## Requirements

- Python 3.8+
- OpenAI API key
- For Google Calendar integration: Google Cloud project with Calendar API enabled

## Future Plans

- Add more integrations:
  - Email integration
  - Weather API
  - Task management platforms (Trello, Asana, etc.)
  - Music services
- Improve the web interface with more interactive features
- Add voice input/output capabilities
- Create a mobile app interface
- Add support for multiple users
- Implement natural language processing for better understanding of user requests

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the Agents SDK
- All contributors to the project
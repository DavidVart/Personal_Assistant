# Integrations Guide

This document provides detailed information about the integrations available in the Personal Assistant.

## Setting Up Integrations

To set up the integrations, run:

```bash
./run.py --mode integrated --setup
```

This will guide you through the setup process for each integration.

## Google Calendar Integration

The Google Calendar integration allows you to manage your calendar events directly from the assistant.

### Setup

1. Create a project in the Google Cloud Console
2. Enable the Google Calendar API
3. Create OAuth 2.0 credentials
4. Download the credentials.json file
5. Place the credentials.json file in the 'credentials' directory
6. Run the setup script to authenticate with Google Calendar

### Usage

Once set up, you can use the following commands:

- **Add an event**:
  ```
  Schedule a meeting with John on Friday at 2pm
  ```
  or
  ```
  Add an event called "Team Meeting" on June 15 from 10am to 11am
  ```

- **List events**:
  ```
  What events do I have tomorrow?
  ```
  or
  ```
  Show me my calendar for next week
  ```

- **Delete an event**:
  ```
  Delete the meeting with John on Friday
  ```
  or
  ```
  Cancel my 2pm appointment
  ```

## Contacts Integration

The contacts integration allows you to manage your contacts.

### Usage

- **Add a contact**:
  ```
  Add John Doe to my contacts with email john@example.com and phone 555-1234
  ```
  or
  ```
  Create a new contact for Jane Smith with email jane@example.com
  ```

- **Find contacts**:
  ```
  Find contacts with "John" in their name
  ```
  or
  ```
  Search for contacts with gmail.com in their email
  ```

- **List all contacts**:
  ```
  Show me all my contacts
  ```
  or
  ```
  List my contacts
  ```

## Notes Integration

The notes integration allows you to create and manage notes.

### Usage

- **Add a note**:
  ```
  Take a note about the project meeting
  ```
  or
  ```
  Create a note titled "Ideas" with content "1. Improve UI 2. Add new features"
  ```

- **Find notes**:
  ```
  Find notes about projects
  ```
  or
  ```
  Search for notes with the tag "work"
  ```

- **Get a note by ID**:
  ```
  Show me note 2
  ```
  or
  ```
  Display note with ID 5
  ```

- **List all notes**:
  ```
  Show me all my notes
  ```
  or
  ```
  List my notes
  ```

## Data Storage

All integration data is stored locally in JSON files in the `data` directory:

- Calendar events: `data/events.json`
- Contacts: `data/contacts.json`
- Notes: `data/notes.json`

## Testing Integrations

You can test the integrations using the provided test script:

```bash
./test_integrated_assistant.py
```

This script will test each integration by:
1. Adding test data
2. Retrieving and displaying the data
3. For calendar events, it will also delete the test event

## Troubleshooting

### Google Calendar Integration Issues

- If you encounter authentication issues, delete the `token.json` file in the `credentials` directory and run the setup script again.
- Make sure your credentials.json file is valid and has the correct permissions.

### General Issues

- Check that the data files exist and are readable/writable.
- Ensure that the OPENAI_API_KEY environment variable is set.
- Make sure you're running the assistant in a virtual environment with all dependencies installed. 
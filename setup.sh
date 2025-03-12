#!/bin/bash

# Personal Assistant Setup Script

echo "=== Personal Assistant Setup ==="
echo "This script will help you set up the Personal Assistant."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment
echo -e "\nCreating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo -e "\nActivating virtual environment..."
source venv/bin/activate

# Install dependencies
echo -e "\nInstalling dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo -e "\nCreating necessary directories..."
mkdir -p data
mkdir -p credentials

# Check for OpenAI API key
if [ -f .env ]; then
    echo -e "\nFound .env file."
else
    echo -e "\nCreating .env file..."
    echo -n "Please enter your OpenAI API key: "
    read api_key
    echo "OPENAI_API_KEY=$api_key" > .env
    echo "Created .env file with API key."
fi

# Make scripts executable
echo -e "\nMaking scripts executable..."
chmod +x run.py
chmod +x setup_integrations.py
chmod +x integrated_assistant.py
chmod +x test_integrated_assistant.py

echo -e "\n=== Setup Complete ==="
echo "To start using the Personal Assistant:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "2. Run the assistant:"
echo "   ./run.py --mode basic"
echo ""
echo "For more information, see the README.md and INTEGRATIONS.md files." 
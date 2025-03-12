#!/usr/bin/env python3
"""
Personal Assistant Runner

This script provides a simple command-line interface to run different versions
of the personal assistant.
"""

import os
import sys
import argparse

def main():
    """Main entry point for the runner script."""
    parser = argparse.ArgumentParser(description="Run the Personal Assistant")
    parser.add_argument(
        "--mode", 
        choices=["basic", "advanced", "web"], 
        default="basic",
        help="Mode to run the assistant in (basic, advanced, or web)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port to run the web server on (only applicable in web mode)"
    )
    
    args = parser.parse_args()
    
    # Check if the virtual environment is activated
    if not os.environ.get("VIRTUAL_ENV"):
        print("Warning: Virtual environment not detected.")
        print("It's recommended to run this script within the virtual environment.")
        print("Activate it with: source venv/bin/activate")
        
        # Ask for confirmation
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(0)
    
    # Check if the OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("You can set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("Or add it to the .env file.")
        
        # Ask for API key
        api_key = input("Enter your OpenAI API key (or press Enter to exit): ")
        if not api_key:
            sys.exit(0)
        
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Run the appropriate assistant
    if args.mode == "basic":
        print("Starting basic personal assistant...")
        import assistant
    elif args.mode == "advanced":
        print("Starting advanced personal assistant...")
        import advanced_assistant
    elif args.mode == "web":
        print(f"Starting web personal assistant on port {args.port}...")
        from web_assistant import app
        app.run(debug=True, port=args.port)

if __name__ == "__main__":
    main() 
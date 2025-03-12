#!/usr/bin/env python3
"""
Personal Assistant Runner

This script provides a simple command-line interface to run different versions
of the personal assistant.
"""

import os
import sys
import argparse
import importlib
import subprocess

def main():
    """Main entry point for the runner script."""
    parser = argparse.ArgumentParser(description="Run the Personal Assistant")
    parser.add_argument(
        "--mode", 
        choices=["basic", "advanced", "web", "integrated"], 
        default="basic",
        help="Mode to run the assistant in (basic, advanced, web, or integrated)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port to run the web server on (only applicable in web mode)"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the setup script for integrations (only applicable in integrated mode)"
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
    
    # Run setup script if requested
    if args.setup and args.mode == "integrated":
        print("Running setup script for integrations...")
        import setup_integrations
        setup_integrations.main()
        return
    
    # Run the appropriate assistant
    if args.mode == "basic":
        print("Starting basic personal assistant...")
        # Execute the assistant.py script directly
        exec(open("assistant.py").read())
    elif args.mode == "advanced":
        print("Starting advanced personal assistant...")
        # Execute the advanced_assistant.py script directly
        exec(open("advanced_assistant.py").read())
    elif args.mode == "web":
        print(f"Starting web personal assistant on port {args.port}...")
        # For web mode, we need to import and run the Flask app
        # with the specified port
        try:
            # Try to use the fixed web assistant first
            if os.path.exists("fixed_web_assistant.py"):
                print("Using fixed web assistant...")
                subprocess.run([sys.executable, "fixed_web_assistant.py"], check=True)
            else:
                # Fall back to the original web assistant
                from web_assistant import app
                app.run(debug=True, port=args.port)
        except Exception as e:
            print(f"Error starting web assistant: {str(e)}")
            print("Falling back to new web assistant...")
            try:
                subprocess.run([sys.executable, "new_web_assistant.py"], check=True)
            except Exception as e2:
                print(f"Error starting new web assistant: {str(e2)}")
                print("Falling back to simple web assistant...")
                subprocess.run([sys.executable, "simple_web_assistant.py"], check=True)
    elif args.mode == "integrated":
        print("Starting integrated personal assistant...")
        # Execute the integrated_assistant.py script directly
        exec(open("integrated_assistant.py").read())

if __name__ == "__main__":
    main() 
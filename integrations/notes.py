"""
Notes Integration for Personal Assistant

This module provides functions to manage notes.
"""

import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# Path to store notes
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

NOTES_FILE = DATA_DIR / "notes.json"

# Initialize notes file if it doesn't exist
if not NOTES_FILE.exists():
    with open(NOTES_FILE, "w") as f:
        json.dump([], f)

def load_notes() -> List[Dict[str, Any]]:
    """
    Load notes from the JSON file.
    
    Returns:
        A list of notes
    """
    try:
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_notes(notes: List[Dict[str, Any]]) -> None:
    """
    Save notes to the JSON file.
    
    Args:
        notes: The list of notes to save
    """
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)

def add_note(title: str, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Add a new note.
    
    Args:
        title: The title of the note
        content: The content of the note
        tags: Optional list of tags for the note
    
    Returns:
        The created note or an error message
    """
    # Load existing notes
    notes = load_notes()
    
    # Create new note
    new_note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    # Add to notes list
    notes.append(new_note)
    
    # Save updated notes
    save_notes(notes)
    
    return {
        "success": True,
        "note_id": new_note["id"],
        "title": title,
        "message": f"Note '{title}' added successfully."
    }

def get_note(note_id: int) -> Dict[str, Any]:
    """
    Get a note by ID.
    
    Args:
        note_id: The ID of the note to retrieve
    
    Returns:
        The note or an error message
    """
    notes = load_notes()
    
    # Find the note by ID
    for note in notes:
        if note["id"] == note_id:
            return {
                "success": True,
                "note": note
            }
    
    return {"error": f"No note found with ID {note_id}."}

def update_note(note_id: int, title: Optional[str] = None, content: Optional[str] = None, 
               tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Update a note.
    
    Args:
        note_id: The ID of the note to update
        title: The new title of the note (if provided)
        content: The new content of the note (if provided)
        tags: The new tags for the note (if provided)
    
    Returns:
        The updated note or an error message
    """
    notes = load_notes()
    
    # Find the note by ID
    for note in notes:
        if note["id"] == note_id:
            # Update the fields that were provided
            if title is not None:
                note["title"] = title
            if content is not None:
                note["content"] = content
            if tags is not None:
                note["tags"] = tags
            
            # Update the updated_at timestamp
            note["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save updated notes
            save_notes(notes)
            
            return {
                "success": True,
                "note_id": note_id,
                "note": note,
                "message": f"Note updated successfully."
            }
    
    return {"error": f"No note found with ID {note_id}."}

def delete_note(note_id: int) -> Dict[str, Any]:
    """
    Delete a note.
    
    Args:
        note_id: The ID of the note to delete
    
    Returns:
        A success message or an error message
    """
    notes = load_notes()
    
    # Find the note by ID
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            # Remove the note
            deleted_note = notes.pop(i)
            
            # Save updated notes
            save_notes(notes)
            
            return {
                "success": True,
                "note_id": note_id,
                "title": deleted_note["title"],
                "message": f"Note '{deleted_note['title']}' deleted successfully."
            }
    
    return {"error": f"No note found with ID {note_id}."}

def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Search for notes by title, content, or tags.
    
    Args:
        query: The search query
    
    Returns:
        A list of matching notes
    """
    notes = load_notes()
    
    # Convert query to lowercase for case-insensitive search
    query = query.lower()
    
    # Search for notes that match the query
    matching_notes = []
    for note in notes:
        if (query in note["title"].lower() or
            query in note["content"].lower() or
            any(query in tag.lower() for tag in note["tags"])):
            matching_notes.append(note)
    
    return matching_notes

def list_notes(tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all notes, optionally filtered by tag.
    
    Args:
        tag: Optional tag to filter notes by
    
    Returns:
        A list of notes
    """
    notes = load_notes()
    
    # Filter by tag if provided
    if tag:
        return [note for note in notes if tag.lower() in [t.lower() for t in note["tags"]]]
    
    return notes

def get_tags() -> List[str]:
    """
    Get a list of all unique tags used in notes.
    
    Returns:
        A list of unique tags
    """
    notes = load_notes()
    
    # Collect all tags
    all_tags = []
    for note in notes:
        all_tags.extend(note["tags"])
    
    # Return unique tags
    return list(set(all_tags))

def export_notes_to_markdown(directory: str) -> Dict[str, Any]:
    """
    Export all notes to Markdown files in the specified directory.
    
    Args:
        directory: The directory to save the Markdown files
    
    Returns:
        A success message or an error message
    """
    notes = load_notes()
    
    try:
        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Export each note to a Markdown file
        exported_count = 0
        for note in notes:
            # Create a filename from the note title
            filename = f"{note['id']}_{note['title'].replace(' ', '_')}.md"
            file_path = os.path.join(directory, filename)
            
            # Format the note as Markdown
            created_at = datetime.datetime.fromisoformat(note["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
            updated_at = datetime.datetime.fromisoformat(note["updated_at"]).strftime("%Y-%m-%d %H:%M:%S")
            
            markdown_content = f"# {note['title']}\n\n"
            markdown_content += f"Created: {created_at}\n"
            markdown_content += f"Updated: {updated_at}\n"
            
            if note["tags"]:
                markdown_content += f"Tags: {', '.join(note['tags'])}\n"
            
            markdown_content += f"\n{note['content']}\n"
            
            # Write to file
            with open(file_path, "w") as f:
                f.write(markdown_content)
            
            exported_count += 1
        
        return {
            "success": True,
            "exported_count": exported_count,
            "directory": directory,
            "message": f"Exported {exported_count} notes to '{directory}' successfully."
        }
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def import_notes_from_markdown(directory: str) -> Dict[str, Any]:
    """
    Import notes from Markdown files in the specified directory.
    
    Args:
        directory: The directory containing the Markdown files
    
    Returns:
        A success message or an error message
    """
    import re
    
    try:
        # Check if the directory exists
        if not os.path.isdir(directory):
            return {"error": f"The directory '{directory}' does not exist."}
        
        # Load existing notes
        notes = load_notes()
        
        # Get the highest existing ID
        max_id = 0
        for note in notes:
            if note["id"] > max_id:
                max_id = note["id"]
        
        # Import each Markdown file as a note
        imported_count = 0
        for filename in os.listdir(directory):
            if not filename.endswith(".md"):
                continue
            
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse the Markdown content
            title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
            if not title_match:
                continue
            
            title = title_match.group(1)
            
            # Extract tags if present
            tags = []
            tags_match = re.search(r"^Tags: (.+)$", content, re.MULTILINE)
            if tags_match:
                tags = [tag.strip() for tag in tags_match.group(1).split(",")]
            
            # Extract the main content
            # This is a simple approach; a more robust parser might be needed for complex Markdown
            content_parts = content.split("\n\n")
            main_content = "\n\n".join(content_parts[2:]) if len(content_parts) > 2 else ""
            
            # Create new note
            new_note = {
                "id": max_id + 1,
                "title": title,
                "content": main_content,
                "tags": tags,
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            # Add to notes list
            notes.append(new_note)
            max_id += 1
            imported_count += 1
        
        # Save updated notes
        save_notes(notes)
        
        return {
            "success": True,
            "imported_count": imported_count,
            "message": f"Imported {imported_count} notes from '{directory}' successfully."
        }
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    print("Notes Management")
    print("1. Add a note")
    print("2. List all notes")
    print("3. Search for notes")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        title = input("Enter title: ")
        content = input("Enter content: ")
        tags_input = input("Enter tags (comma-separated, optional): ")
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        result = add_note(title, content, tags)
        print(result["message"] if "message" in result else result["error"])
    
    elif choice == "2":
        notes = list_notes()
        if not notes:
            print("No notes found.")
        else:
            for note in notes:
                print(f"{note['id']}. {note['title']} - Tags: {', '.join(note['tags'])}")
    
    elif choice == "3":
        query = input("Enter search query: ")
        notes = search_notes(query)
        if not notes:
            print("No matching notes found.")
        else:
            for note in notes:
                print(f"{note['id']}. {note['title']} - Tags: {', '.join(note['tags'])}")
    
    elif choice == "4":
        print("Goodbye!")
    
    else:
        print("Invalid choice.") 
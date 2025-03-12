"""
Contacts Integration for Personal Assistant

This module provides functions to manage contacts.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any

# Path to store contacts
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CONTACTS_FILE = DATA_DIR / "contacts.json"

# Initialize contacts file if it doesn't exist
if not CONTACTS_FILE.exists():
    with open(CONTACTS_FILE, "w") as f:
        json.dump([], f)

def load_contacts() -> List[Dict[str, Any]]:
    """
    Load contacts from the JSON file.
    
    Returns:
        A list of contacts
    """
    try:
        with open(CONTACTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_contacts(contacts: List[Dict[str, Any]]) -> None:
    """
    Save contacts to the JSON file.
    
    Args:
        contacts: The list of contacts to save
    """
    with open(CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

def add_contact(name: str, email: Optional[str] = None, phone: Optional[str] = None, 
                address: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new contact.
    
    Args:
        name: The name of the contact
        email: The email address of the contact
        phone: The phone number of the contact
        address: The address of the contact
        notes: Additional notes about the contact
    
    Returns:
        The created contact or an error message
    """
    # Validate email if provided
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"error": "Invalid email address format."}
    
    # Load existing contacts
    contacts = load_contacts()
    
    # Check if contact with the same name already exists
    for contact in contacts:
        if contact["name"].lower() == name.lower():
            return {"error": f"A contact with the name '{name}' already exists."}
    
    # Create new contact
    new_contact = {
        "id": len(contacts) + 1,
        "name": name,
        "email": email or "",
        "phone": phone or "",
        "address": address or "",
        "notes": notes or ""
    }
    
    # Add to contacts list
    contacts.append(new_contact)
    
    # Save updated contacts
    save_contacts(contacts)
    
    return {
        "success": True,
        "contact_id": new_contact["id"],
        "name": name,
        "message": f"Contact '{name}' added successfully."
    }

def get_contact(contact_id: Optional[int] = None, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a contact by ID or name.
    
    Args:
        contact_id: The ID of the contact to retrieve
        name: The name of the contact to retrieve
    
    Returns:
        The contact or an error message
    """
    if contact_id is None and name is None:
        return {"error": "Either contact_id or name must be provided."}
    
    contacts = load_contacts()
    
    # Search by ID
    if contact_id is not None:
        for contact in contacts:
            if contact["id"] == contact_id:
                return {
                    "success": True,
                    "contact": contact
                }
        return {"error": f"No contact found with ID {contact_id}."}
    
    # Search by name
    if name is not None:
        for contact in contacts:
            if contact["name"].lower() == name.lower():
                return {
                    "success": True,
                    "contact": contact
                }
        return {"error": f"No contact found with name '{name}'."}

def update_contact(contact_id: int, name: Optional[str] = None, email: Optional[str] = None, 
                  phone: Optional[str] = None, address: Optional[str] = None, 
                  notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Update a contact.
    
    Args:
        contact_id: The ID of the contact to update
        name: The new name of the contact (if provided)
        email: The new email address of the contact (if provided)
        phone: The new phone number of the contact (if provided)
        address: The new address of the contact (if provided)
        notes: The new notes about the contact (if provided)
    
    Returns:
        The updated contact or an error message
    """
    # Validate email if provided
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"error": "Invalid email address format."}
    
    contacts = load_contacts()
    
    # Find the contact by ID
    for i, contact in enumerate(contacts):
        if contact["id"] == contact_id:
            # Update the fields that were provided
            if name:
                # Check if the new name conflicts with another contact
                for other_contact in contacts:
                    if other_contact["id"] != contact_id and other_contact["name"].lower() == name.lower():
                        return {"error": f"A contact with the name '{name}' already exists."}
                contact["name"] = name
            if email is not None:
                contact["email"] = email
            if phone is not None:
                contact["phone"] = phone
            if address is not None:
                contact["address"] = address
            if notes is not None:
                contact["notes"] = notes
            
            # Save updated contacts
            save_contacts(contacts)
            
            return {
                "success": True,
                "contact_id": contact_id,
                "contact": contact,
                "message": f"Contact updated successfully."
            }
    
    return {"error": f"No contact found with ID {contact_id}."}

def delete_contact(contact_id: int) -> Dict[str, Any]:
    """
    Delete a contact.
    
    Args:
        contact_id: The ID of the contact to delete
    
    Returns:
        A success message or an error message
    """
    contacts = load_contacts()
    
    # Find the contact by ID
    for i, contact in enumerate(contacts):
        if contact["id"] == contact_id:
            # Remove the contact
            deleted_contact = contacts.pop(i)
            
            # Save updated contacts
            save_contacts(contacts)
            
            return {
                "success": True,
                "contact_id": contact_id,
                "name": deleted_contact["name"],
                "message": f"Contact '{deleted_contact['name']}' deleted successfully."
            }
    
    return {"error": f"No contact found with ID {contact_id}."}

def search_contacts(query: str) -> List[Dict[str, Any]]:
    """
    Search for contacts by name, email, phone, or address.
    
    Args:
        query: The search query
    
    Returns:
        A list of matching contacts
    """
    contacts = load_contacts()
    
    # Convert query to lowercase for case-insensitive search
    query = query.lower()
    
    # Search for contacts that match the query
    matching_contacts = []
    for contact in contacts:
        if (query in contact["name"].lower() or
            query in contact["email"].lower() or
            query in contact["phone"].lower() or
            query in contact["address"].lower() or
            query in contact["notes"].lower()):
            matching_contacts.append(contact)
    
    return matching_contacts

def list_contacts() -> List[Dict[str, Any]]:
    """
    List all contacts.
    
    Returns:
        A list of all contacts
    """
    return load_contacts()

def import_contacts_from_csv(file_path: str) -> Dict[str, Any]:
    """
    Import contacts from a CSV file.
    
    Args:
        file_path: The path to the CSV file
    
    Returns:
        A success message or an error message
    """
    import csv
    
    try:
        # Load existing contacts
        contacts = load_contacts()
        
        # Get the highest existing ID
        max_id = 0
        for contact in contacts:
            if contact["id"] > max_id:
                max_id = contact["id"]
        
        # Read the CSV file
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            
            # Check if the required fields are present
            required_fields = ["name"]
            for field in required_fields:
                if field not in reader.fieldnames:
                    return {"error": f"The CSV file is missing the required field '{field}'."}
            
            # Import contacts
            imported_count = 0
            for row in reader:
                # Skip rows without a name
                if not row["name"]:
                    continue
                
                # Check if a contact with the same name already exists
                name_exists = False
                for contact in contacts:
                    if contact["name"].lower() == row["name"].lower():
                        name_exists = True
                        break
                
                if name_exists:
                    continue
                
                # Create new contact
                new_contact = {
                    "id": max_id + 1,
                    "name": row["name"],
                    "email": row.get("email", ""),
                    "phone": row.get("phone", ""),
                    "address": row.get("address", ""),
                    "notes": row.get("notes", "")
                }
                
                # Add to contacts list
                contacts.append(new_contact)
                max_id += 1
                imported_count += 1
            
            # Save updated contacts
            save_contacts(contacts)
            
            return {
                "success": True,
                "imported_count": imported_count,
                "message": f"Imported {imported_count} contacts successfully."
            }
    
    except FileNotFoundError:
        return {"error": f"The file '{file_path}' was not found."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def export_contacts_to_csv(file_path: str) -> Dict[str, Any]:
    """
    Export contacts to a CSV file.
    
    Args:
        file_path: The path to save the CSV file
    
    Returns:
        A success message or an error message
    """
    import csv
    
    try:
        # Load contacts
        contacts = load_contacts()
        
        # Write to CSV file
        with open(file_path, "w", newline="") as f:
            fieldnames = ["id", "name", "email", "phone", "address", "notes"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for contact in contacts:
                writer.writerow(contact)
        
        return {
            "success": True,
            "exported_count": len(contacts),
            "file_path": file_path,
            "message": f"Exported {len(contacts)} contacts to '{file_path}' successfully."
        }
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    print("Contacts Management")
    print("1. Add a contact")
    print("2. List all contacts")
    print("3. Search for contacts")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        name = input("Enter name: ")
        email = input("Enter email (optional): ")
        phone = input("Enter phone (optional): ")
        address = input("Enter address (optional): ")
        notes = input("Enter notes (optional): ")
        
        result = add_contact(name, email, phone, address, notes)
        print(result["message"] if "message" in result else result["error"])
    
    elif choice == "2":
        contacts = list_contacts()
        if not contacts:
            print("No contacts found.")
        else:
            for contact in contacts:
                print(f"{contact['id']}. {contact['name']} - {contact['email']} - {contact['phone']}")
    
    elif choice == "3":
        query = input("Enter search query: ")
        contacts = search_contacts(query)
        if not contacts:
            print("No matching contacts found.")
        else:
            for contact in contacts:
                print(f"{contact['id']}. {contact['name']} - {contact['email']} - {contact['phone']}")
    
    elif choice == "4":
        print("Goodbye!")
    
    else:
        print("Invalid choice.") 
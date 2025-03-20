from db.repositories import UserRepository, NoteRepository, db
from typing import Dict, List, Any, Optional


# Facade Pattern - provides a simplified interface to the complex subsystem
class FirebaseDB:
    """Facade for all Firestore interactions for the Notes app"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.note_repo = NoteRepository()
    
    # User operations
    def add_user(self, user_id: str, email: str) -> bool:
        """Adds a new user"""
        return self.user_repo.create_user(user_id, email)
    
    def get_categories(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Gets all categories with notes for a user"""
        return self.user_repo.get_categories(user_id)
    
    # Note operations
    def get_notes(self, user_id: str) -> List[Dict[str, Any]]:
        """Gets all notes for a user"""
        return self.note_repo.get_user_notes(user_id)
    
    def add_note(self, user_id: str, category: str, note_text: str, font_family: str = "Arial", tags: List[str] = None) -> Optional[str]:
        """
        Adds a note to a category with optional font family and tags
        
        Args:
            user_id (str): The user ID
            category (str): The category name
            note_text (str): The text content of the note
            font_family (str, optional): Font family for the note. Defaults to "Arial".
            tags (List[str], optional): List of users tagged in the note. Defaults to None.
            
        Returns:
            Optional[str]: The note ID if successful, None otherwise
        """
        # Initialize tags if None
        if tags is None:
            tags = []
            
        # First add the note to the general collection
        note_ref = self.note_repo.create_note(user_id, note_text, font_family, tags)
        
        if not note_ref:
            return None
        
        # Add the note reference to the user's category
        success = self.user_repo.add_note_to_category(user_id, category, note_ref)
        
        if not success:
            # Rollback - delete the note if we couldn't add it to the category
            self.note_repo.delete_note(note_ref.id)
            return None
        
        return note_ref.id
    
    def edit_note(self, note_id: str, note_text: str, user_id: str, category: str, font_family: str = "Arial", tags: List[str] = None) -> bool:
        """
        Edits a note with updated text, font family, and tags
        
        Args:
            note_id (str): The note ID
            note_text (str): The updated text content
            user_id (str): The user ID for verification
            category (str): The category name
            font_family (str, optional): Font family for the note. Defaults to "Arial".
            tags (List[str], optional): List of users tagged in the note. Defaults to None.
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Initialize tags if None
        if tags is None:
            tags = []
            
        note_data = self.note_repo.get_note(note_id)
        
        # Verify the note belongs to the user
        if not note_data or note_data.get("user_id") != user_id:
            return False
        
        return self.note_repo.update_note(note_id, note_text, font_family, tags)
    
    def delete_note(self, user_id: str, note_id: str, category: str) -> bool:
        """
        Deletes a note and removes it from the category
        
        Args:
            user_id (str): The user ID
            note_id (str): The note ID to delete
            category (str): The category name
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get note reference
        note_ref = db.collection("notes").document(note_id)
        
        # Remove from category
        removed = self.user_repo.remove_note_from_category(user_id, category, note_ref)
        
        if not removed:
            return False
        
        # Delete the actual note
        return self.note_repo.delete_note(note_id)
    
    def share_note(self, note_id: str, user_id: str, platform: str) -> bool:
        """
        Records a note share event
        
        Args:
            note_id (str): The note ID being shared
            user_id (str): The user ID sharing the note
            platform (str): The platform where the note is shared
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Verify the note belongs to the user
        note_data = self.note_repo.get_note(note_id)
        if not note_data or note_data.get("user_id") != user_id:
            return False
            
        # Create a share record
        share_data = {
            "note_id": note_id,
            "user_id": user_id,
            "platform": platform,
            "timestamp": db.field_value.server_timestamp()
        }
        
        try:
            db.collection("note_shares").add(share_data)
            return True
        except Exception:
            return False
    
    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific note by ID
        
        Args:
            note_id (str): The note ID to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The note data if found, None otherwise
        """
        return self.note_repo.get_note(note_id)
    
    def get_user_tags(self, user_id: str) -> List[str]:
        """
        Gets a list of all tags used by a user
        
        Args:
            user_id (str): The user ID
            
        Returns:
            List[str]: List of unique tags used by the user
        """
        # Get all the user's notes
        notes = self.note_repo.get_user_notes(user_id)
        
        # Extract all tags
        all_tags = []
        for note in notes:
            if "tags" in note and note["tags"]:
                all_tags.extend(note["tags"])
        
        # Return unique tags
        return list(set(all_tags))
    
    def search_notes(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Searches for notes containing the search term
        
        Args:
            user_id (str): The user ID
            search_term (str): The term to search for
            
        Returns:
            List[Dict[str, Any]]: List of notes matching the search term
        """
        notes = self.note_repo.get_user_notes(user_id)
        
        # Filter notes that contain the search term
        matching_notes = [
            note for note in notes 
            if search_term.lower() in note.get("text", "").lower()
        ]
        
        return matching_notes
    
    def upload_note_to_drive(self, note_id: str, user_id: str, drive_file_id: str) -> bool:
        """
        Records a Google Drive upload event for a note
        
        Args:
            note_id (str): The note ID being uploaded
            user_id (str): The user ID uploading the note
            drive_file_id (str): The Google Drive file ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Verify the note belongs to the user
        note_data = self.note_repo.get_note(note_id)
        if not note_data or note_data.get("user_id") != user_id:
            return False
            
        # Create an upload record
        upload_data = {
            "note_id": note_id,
            "user_id": user_id,
            "drive_file_id": drive_file_id,
            "timestamp": db.field_value.server_timestamp()
        }
        
        try:
            db.collection("drive_uploads").add(upload_data)
            
            # Update the note with drive_file_id reference
            note_ref = db.collection("notes").document(note_id)
            note_ref.update({"drive_file_id": drive_file_id})
            
            return True
        except Exception:
            return False
    
    def get_notes_by_tag(self, user_id: str, tag: str) -> List[Dict[str, Any]]:
        """
        Gets all notes that contain a specific tag
        
        Args:
            user_id (str): The user ID
            tag (str): The tag to search for
            
        Returns:
            List[Dict[str, Any]]: List of notes containing the tag
        """
        notes = self.note_repo.get_user_notes(user_id)
        
        # Filter notes that contain the tag
        matching_notes = [
            note for note in notes 
            if "tags" in note and tag in note.get("tags", [])
        ]
        
        return matching_notes
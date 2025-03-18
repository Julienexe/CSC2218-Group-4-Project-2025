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
    
    def add_note(self, user_id: str, category: str, note_text: str, font_family: str = "Arial") -> Optional[str]:
        """Adds a note to a category"""
        # First add the note to the general collection
        note_ref = self.note_repo.create_note(user_id, note_text, font_family)
        
        if not note_ref:
            return None
        
        # Add the note reference to the user's category
        success = self.user_repo.add_note_to_category(user_id, category, note_ref)
        
        if not success:
            # Rollback - delete the note if we couldn't add it to the category
            self.note_repo.delete_note(note_ref.id)
            return None
        
        return note_ref.id
    
    def edit_note(self, note_id: str, note_text: str, user_id: str, category: str, font_family: str = "Arial") -> bool:
        """Edits a note"""
        note_data = self.note_repo.get_note(note_id)
        
        # Verify the note belongs to the user
        if not note_data or note_data.get("user_id") != user_id:
            return False
        
        return self.note_repo.update_note(note_id, note_text, font_family)
    
    def delete_note(self, user_id: str, note_id: str, category: str) -> bool:
        """Deletes a note and removes it from the category"""
        # Get note reference
        note_ref = db.collection("notes").document(note_id)
        
        # Remove from category
        removed = self.user_repo.remove_note_from_category(user_id, category, note_ref)
        
        if not removed:
            return False
        
        # Delete the actual note
        return self.note_repo.delete_note(note_id)
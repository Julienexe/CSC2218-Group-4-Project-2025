from firebase_admin import firestore
from modules.decorators import handle_firestore_errors
from modules.loggers import LoggerSingleton
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypeVar, Generic

# Type definitions for better type hinting
T = TypeVar('T')
DocumentDict = Dict[str, Any]

db = firestore.client()

# Utility class for common operations
class FirestoreUtils:
    @staticmethod
    @handle_firestore_errors
    def get_dict_from_ref(ref) -> Optional[DocumentDict]:
        """Returns a dictionary from a Firestore reference"""
        return ref.get().to_dict() if ref else None

# Repository Interface (Repository Pattern)
class Repository(ABC, Generic[T]):
    @abstractmethod
    def create(self, id: str, data: T) -> bool:
        pass
    
    @abstractmethod
    def read(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    def update(self, id: str, data: T) -> bool:
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        pass
    
    @abstractmethod
    def list(self, filter_field: Optional[str] = None, filter_value: Optional[str] = None) -> List[T]:
        pass

# Data Access Object implementation (DAO Pattern)
class FirestoreDAO(Repository[DocumentDict]):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.logger = LoggerSingleton.get_instance()
    
    @handle_firestore_errors
    def create(self, id: str, data: DocumentDict) -> bool:
        db.collection(self.collection_name).document(id).set(data)
        return True
    
    @handle_firestore_errors
    def read(self, id: str) -> Optional[DocumentDict]:
        doc_ref = db.collection(self.collection_name).document(id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    @handle_firestore_errors
    def update(self, id: str, data: DocumentDict) -> bool:
        db.collection(self.collection_name).document(id).update(data)
        return True
    
    @handle_firestore_errors
    def delete(self, id: str) -> bool:
        db.collection(self.collection_name).document(id).delete()
        return True
    
    @handle_firestore_errors
    def list(self, filter_field: Optional[str] = None, filter_value: Optional[str] = None) -> List[DocumentDict]:
        collection_ref = db.collection(self.collection_name)
        
        if filter_field and filter_value:
            query = collection_ref.where(filter_field, "==", filter_value)
        else:
            query = collection_ref
            
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    @handle_firestore_errors
    def add_with_auto_id(self, data: DocumentDict) -> Optional[str]:
        """Creates a document with auto-generated ID"""
        _, doc_ref = db.collection(self.collection_name).add(data)
        return doc_ref

# Domain-specific repositories (Repository Pattern + Factory Pattern)
class UserRepository:
    def __init__(self):
        self.dao = FirestoreDAO("users")
    
    def create_user(self, user_id: str, email: str) -> bool:
        """Creates a new user"""
        return self.dao.create(user_id, {"email": email})
    
    def get_user(self, user_id: str) -> Optional[DocumentDict]:
        """Gets a user's data"""
        return self.dao.read(user_id)
    
    @handle_firestore_errors
    def add_note_to_category(self, user_id: str, category: str, note_ref) -> bool:
        """Adds a note reference to a user's category"""
        user_data = self.get_user(user_id) or {}
        
        if category in user_data:
            # Category exists, append the new note reference
            category_refs = user_data[category]
            category_refs.append(note_ref)
        else:
            # Category doesn't exist, create it with the new note reference
            category_refs = [note_ref]
        
        # Update the user document with the new category data
        return self.dao.update(user_id, {category: category_refs})
    
    @handle_firestore_errors
    def remove_note_from_category(self, user_id: str, category: str, note_ref) -> bool:
        """Removes a note reference from a user's category"""
        user_data = self.get_user(user_id) or {}
        
        if category in user_data and isinstance(user_data[category], list):
            # Remove the reference from the array using ArrayRemove
            self.dao.update(user_id, {category: firestore.ArrayRemove([note_ref])})
            
            # If the category is now empty, remove it completely
            updated_user = self.get_user(user_id)
            if category in updated_user and len(updated_user[category]) == 0:
                self.dao.update(user_id, {category: firestore.DELETE_FIELD})
            return True
        return False
    
    @handle_firestore_errors
    def get_categories(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Gets all categories with notes for a user"""
        categories_dict = {}
        user_data = self.get_user(user_id) or {}
        
        for field_name, field_value in user_data.items():
            if isinstance(field_value, list):
                notes_list = self._load_category_notes(field_name, field_value)
                if notes_list:
                    categories_dict[field_name] = notes_list
        
        return categories_dict
    
    @staticmethod
    @handle_firestore_errors
    def _load_category_notes(field_name: str, field_value: List) -> List[Dict[str, Any]]:
        """Loads notes from a category field in a user document"""
        notes_list = []
        
        for note_ref in field_value:
            note_dict = FirestoreUtils.get_dict_from_ref(note_ref)
            
            if note_dict:
                notes_list.append({
                    "id": note_ref.id,
                    "text": note_dict.get("text", ""),
                    "font_family": note_dict.get("font_family", "Arial")
                })
        
        return notes_list

class NoteRepository:
    def __init__(self):
        self.dao = FirestoreDAO("notes")
    
    @handle_firestore_errors
    def create_note(self, user_id: str, note_text: str, font_family: str = "Arial") -> Optional[object]:
        """Creates a new note and returns the reference"""
        note_data = {
            "text": note_text,
            "user_id": user_id,
            "font_family": font_family,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        
        return self.dao.add_with_auto_id(note_data)
    
    def get_note(self, note_id: str) -> Optional[DocumentDict]:
        """Gets a note by ID"""
        return self.dao.read(note_id)
    
    def update_note(self, note_id: str, note_text: str, font_family: str = "Arial") -> bool:
        """Updates a note's text and font"""
        update_data = {
            "text": note_text,
            "font_family": font_family,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        
        return self.dao.update(note_id, update_data)
    
    def delete_note(self, note_id: str) -> bool:
        """Deletes a note"""
        return self.dao.delete(note_id)
    
    def get_user_notes(self, user_id: str) -> List[Dict[str, Any]]:
        """Gets all notes for a user"""
        notes_list = self.dao.list("user_id", user_id)
        return [{"id": note.get("id", ""), "text": note.get("text", "")} for note in notes_list]
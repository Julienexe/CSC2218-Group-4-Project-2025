import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Initialize Firebase
cred = credentials.Certificate(r"serviceAccountKey.json")
# Initialize Firebase Admin SDK
# firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseDB:
    """Handles all Firestore interactions for the Notes app"""
    logger = logger

    #method to return a dictionary from a firebase reference
    @staticmethod
    def get_dict_from_ref(ref):
        """Returns a dictionary from a Firestore reference"""
        return ref.get().to_dict() if ref else None
    

    #method to read a document from firestore and return it
    @staticmethod
    def read_document(collection_name: str, document_id: str)-> dict:
        """Reads a document from Firestore"""
        try:
            doc_ref = db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            FirebaseDB.logger.error(f"Error reading document: {e}")
            return None
    
    #read all documents in a collection and apply a filter if needed
    @staticmethod
    def read_collection(collection_name: str, filter_field: str = None, filter_value: str = None):
        """Reads all documents from a Firestore collection"""


        try:
            collection_ref = db.collection(collection_name)
            if filter_field and filter_value:
                query = collection_ref.where(filter_field, "==", filter_value)
            else:
                query = collection_ref
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            FirebaseDB.logger.error(f"Error reading collection: {e}")
            return []
    

    @staticmethod
    def get_notes(user_id: str) -> list:
        """Fetches all notes for a given user from Firestore"""
        try:
            notes_list = FirebaseDB.read_collection("notes", "user_id", user_id)
            #return a list of notes with an id and text
            return [{"id": note["id"], "text": note["text"]} for note in notes_list]

        except Exception as e:
            FirebaseDB.logger.error(f"Error getting notes: {e}")
            return []
    
    @staticmethod
    def add_user(user_id:str, email:str):
        """Adds a new user to Firestore
        ARGS:
        user_id (str): The unique ID of the user
        email (str): The email of the user
        """
        try:
            # Add user to users collection, create it if it does not exist
            users_ref = db.collection("users")
            users_ref.document(user_id).set({"email": email})
        except Exception as e:
            FirebaseDB.logger.error(f"Error adding user: {e}")
            
    @staticmethod
    def add_note(user_id, category, note_text, font_family="Arial"):
        """
        Adds a note to the general notes collection and updates the user's document 
        with a reference to the note under the specified category
        """
        try:
            # First add the note to the general collection
            note_ref = FirebaseDB.add_note_to_general_collection(user_id, note_text, font_family)
            
            if not note_ref:
                FirebaseDB.logger.error("Failed to create note in general collection")
                return None
                
            # Now update the user's document to include this note reference in the specified category
            user_doc_ref = db.collection("users").document(user_id)
            
            # Get the current user document
            user_doc = user_doc_ref.get()
            
            if user_doc.exists:
                # User document exists, update it
                user_data = user_doc.to_dict() or {}
                
                # Check if this category already exists in the user document
                if category in user_data:
                    # Category exists, append the new note reference
                    category_refs = user_data[category]
                    category_refs.append(note_ref)
                else:
                    # Category doesn't exist, create it with the new note reference
                    category_refs = [note_ref]
                
                # Update the user document with the new category data
                user_doc_ref.update({
                    category: category_refs
                })
            else:
                # User document doesn't exist, create it
                user_doc_ref.set({
                    category: [note_ref]
                })
            
            return note_ref.id  # Return the ID of the new note
            
        except Exception as e:
            FirebaseDB.logger.error(f"Error adding note: {e}")
            return None
        
    @staticmethod
    def add_note_to_general_collection(user_id: str, note_text: str, font_family: str = "Arial"):
        """
        Adds a new note to Firestore
        Returns the document reference for the newly created note
        """
        try:
            # Add note to Firestore under the 'notes' collection
            notes_ref = db.collection("notes")
            _, new_note_ref = notes_ref.add({
                "text": note_text,
                "user_id": user_id,
                "font_family": font_family,  # Include the font family
                "timestamp": firestore.SERVER_TIMESTAMP  # Adding a timestamp for sorting if needed
            })
            
            # Return the document reference rather than just the ID
            return new_note_ref
            
        except Exception as e:
            FirebaseDB.logger.error(f"Error adding note: {e}")
            return None
        
    @staticmethod
    def edit_note(note_id: str, note_text: str, user_id: str, category: str, font_family: str = "Arial"):
        """
        Edits a note in the general notes collection
        
        Parameters:
        - note_id: The ID of the note to edit
        - note_text: The new text for the note
        - user_id: The ID of the user who owns the note (for validation)
        - category: The category the note belongs to (not used in this implementation but kept for compatibility)
        - font_family: The font family to use for the note
        
        Returns:
        - True if the edit was successful, False otherwise
        """
        try:
            # Reference to the note in the general notes collection
            note_ref = db.collection("notes").document(note_id)
            
            # Get the note to verify it belongs to the user
            note_doc = note_ref.get()
            
            if not note_doc.exists:
                FirebaseDB.logger.error(f"Note {note_id} does not exist")
                return False
                
            note_data = note_doc.to_dict()
            
            # Verify the note belongs to the user
            if note_data.get("user_id") != user_id:
                FirebaseDB.logger.error(f"Note {note_id} does not belong to user {user_id}")
                return False
            
            # Update the note text and font family
            note_ref.update({
                "text": note_text,
                "font_family": font_family,  # Update the font family
                "timestamp": firestore.SERVER_TIMESTAMP  # Update timestamp for sorting
            })
            
            return True
            
        except Exception as e:
            FirebaseDB.logger.error(f"Error editing note: {e}")
            return False
        
    @staticmethod
    def delete_note(user_id: str, note_id: str, category: str):
        """
        Deletes a note by:
        1. Removing the reference from the user's document category array
        2. Deleting the actual note from the general notes collection
        
        Parameters:
        - user_id: The ID of the user who owns the note
        - note_id: The ID of the note to delete
        - category: The category the note belongs to
        """
        try:
            # Step 1: Get the user document
            user_doc_ref = db.collection("users").document(user_id)
            user_doc = user_doc_ref.get()
            
            if not user_doc.exists:
                FirebaseDB.logger.error(f"User document for {user_id} does not exist")
                return
            
            # Step 2: Get the note reference to remove
            note_ref = db.collection("notes").document(note_id)
            
            # Step 3: Remove the note reference from the category array in the user document
            user_data = user_doc.to_dict()
            
            if category in user_data and isinstance(user_data[category], list):
                # Remove the reference from the array
                # Using arrayRemove is the best way to remove items from a Firestore array
                user_doc_ref.update({
                    category: firestore.ArrayRemove([note_ref])
                })
                
                # If the category is now empty, you might want to remove it completely
                # This requires a separate get and update operation
                updated_user = user_doc_ref.get().to_dict()
                if category in updated_user and len(updated_user[category]) == 0:
                    # Remove the empty category field
                    user_doc_ref.update({
                        category: firestore.DELETE_FIELD
                    })
                    
            else:
                FirebaseDB.logger.error(f"Category {category} not found in user document or is not an array")
            
            # Step 4: Delete the actual note from the general collection
            note_ref.delete()
            
            FirebaseDB.logger.info(f"Successfully deleted note {note_id} from category {category}")
            
        except Exception as e:
            FirebaseDB.logger.error(f"Error deleting note: {e}")
                
    @staticmethod
    def get_categories(user_id) -> dict:
        """
        Fetch all categories with their notes from Firestore
        Returns a dictionary where:
        - Keys are category names
        - Values are lists of note objects with 'id', 'text', and 'font_family' fields
        """
        # Create a dictionary to store categories and their notes
        categories_dict = {}
        
        try:
            # Get the user data
            user_data = FirebaseDB.read_document("users", user_id) or {}
            
            # Iterate through each field in the user document
            for field_name, field_value in user_data.items():
                # Check if the field value is an array (potential category)
                if isinstance(field_value, list):
                    # This field is likely a category with an array of note references
                    notes_list = FirebaseDB.load_category_notes(field_name, field_value)
                    # Only add the category if it has notes
                    if notes_list:
                        categories_dict[field_name] = notes_list
        
        except Exception as e:
            FirebaseDB.logger.error(f"Error fetching categories for user {user_id}: {e}")
        return categories_dict

    @staticmethod
    def load_category_notes(field_name, field_value )-> list:
        """ Load notes from a category field in a user document """
        notes_list=[]
        for note_ref in field_value:
            try:
                            # Get the note dictionary
                note_dict = FirebaseDB.get_dict_from_ref(note_ref)
                            
                if note_dict:
                                # Add the note ID, text, and font_family to our list
                    notes_list.append({
                                    "id": note_ref.id,
                                    "text": note_dict.get("text", ""),
                                    "font_family": note_dict.get("font_family", "Arial")  # Include the font family
                                })
                else:    
                    FirebaseDB.logger.error(f"Note {note_ref.id} referenced in {field_name} doesn't exist")
            except Exception as e:
                FirebaseDB.logger.error(f"Error fetching note {note_ref.id}: {e}")
        return notes_list
                            
                            
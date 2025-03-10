import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate(r"CSC2218-Group-4-Project-2025/serviceAccountKey.json")
# Initialize Firebase Admin SDK
# firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

class FirebaseDB:
    """Handles all Firestore interactions for the Notes app"""

    @staticmethod
    def get_notes(user_id: str):
        """Fetches all notes for a given user from Firestore"""
        try:
            notes_ref = db.collection("notes").where("user_id", "==", user_id).stream()
            # Return a list of notes with id and text
            return [{"id": note.id, "text": note.to_dict()["text"]} for note in notes_ref]
        except Exception as e:
            print(f"Error getting notes: {e}")
            return []

    @staticmethod
    def add_note(user_id: str, note_text: str):
        """Adds a new note to Firestore"""
        try:
            # Add note to Firestore under the 'notes' collection
            notes_ref = db.collection("notes")
            date_added,new_note = notes_ref.add({
                "text": note_text,
                "user_id": user_id,
                "timestamp": firestore.SERVER_TIMESTAMP  # Adding a timestamp for sorting if needed
            })
            return new_note.id
            # Return the document ID

        except Exception as e:
            print(f"Error adding note: {e}")
            return None
    #edit notes
    @staticmethod
    def edit_note( note_id: str, note_text: str):
        """Edits a note in Firestore"""
        try:
            # Get the note document
            note_ref = db.collection("notes").document(note_id)
            # Update the note text
            note_ref.set({
                "text": note_text,
                "timestamp": firestore.SERVER_TIMESTAMP  # Adding a timestamp for sorting if needed
                }, merge= True)
            return True
        
        except Exception as e:
            print(f"Error editing note: {e}")
            return False
        
    @staticmethod
    def delete_note(user_id: str, note_id: str):
        """Deletes a note from Firestore"""
        try:
            # Reference the note by its ID
            note_ref = db.collection("notes").document(note_id)
            note_ref.delete()
        except Exception as e:
            print(f"Error deleting note: {e}")

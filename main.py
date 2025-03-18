import flet as ft
import firebase_admin
from firebase_admin import auth, credentials
from modules.loggers import Logger

# Initialize Firebase
cred = credentials.Certificate(r"serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from auth import AuthManager
from n0tes3 import NotesApp

# Set up logging
logger = Logger(__name__).get_logger()

# This function will navigate the user to the NotesApp after login
def navigate_to_notes(page: ft.Page, user_id: str):
    """Navigates to the NotesApp screen after login"""
    page.views.clear()
    page.views.append(NotesApp(page=page, userId=user_id))
    page.update()

# Function to check if user is already logged in
def check_existing_session():
    """Check if there is an existing logged-in user session"""
    try:
        # You'll need to implement how you're storing the user session
        # This could be a local storage mechanism, cookies, or some other method
        # For example, you might use something like:
        import os
        session_file = os.path.join(os.path.expanduser("~"), ".evonote_session")
        
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                user_id = f.read().strip()
                
            # Verify the user ID is still valid in Firebase
            try:
                auth.get_user(user_id)
                return {"success": True, "user_id": user_id}
            except:
                # User not found or token expired
                os.remove(session_file)  # Remove invalid session
                return {"success": False}
        return {"success": False}
    except Exception as e:
        logger.error(f"Error checking session: {e}")
        return {"success": False}

# Function to save user session
def save_session(user_id):
    """Save user session for auto-login next time"""
    try:
        import os
        session_file = os.path.join(os.path.expanduser("~"), ".evonote_session")
        with open(session_file, "w") as f:
            f.write(user_id)
        return True
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        return False

def main(page: ft.Page):
    page.title = "EvoNote"
    
    # Check if user is already logged in
    existing_session = check_existing_session()
    
    if existing_session["success"]:
        # User is already logged in, navigate directly to notes
        user_id = existing_session["user_id"]
        logger.info(f"Auto-login for user ID: {user_id}")
        navigate_to_notes(page, user_id)
        return
    
    # If not logged in, show the login form
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Password", password=True, width=300)
    message = ft.Text("")

    def handle_register(e):
        result = AuthManager.register_user(email_field.value, password_field.value)
        message.value = result["message"]
        page.update()

    def handle_login(e):
        result = AuthManager.login_user(email_field.value, password_field.value)
        if result["success"]:
            message.value = "Login Successful!"
            user_id = result["user_id"]
            logger.info(f"User ID: {user_id}")
            
            # Save the session for next time
            save_session(user_id)
            
            navigate_to_notes(page, user_id)  # Navigate to NotesApp after login
        else:
            message.value = result["message"]  # Show error message if login fails
        page.update()

    page.add(
        email_field,
        password_field,
        ft.Row([
            ft.ElevatedButton("Register", on_click=handle_register),
            ft.ElevatedButton("Login", on_click=handle_login),
        ]),
        message
    )

ft.app(target=main)
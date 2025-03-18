import flet as ft
import firebase_admin
from firebase_admin import auth, credentials
# Initialize Firebase
cred = credentials.Certificate(r"serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from auth import AuthManager
from n0tes3 import NotesApp
# This function will navigate the user to the NotesApp after login
def navigate_to_notes(page: ft.Page, user_id: str):
    """Navigates to the NotesApp screen after login"""
    page.views.clear()
    page.views.append(NotesApp(page=page,userId=user_id))
    page.update()
    # page.session["user_uid"] = user_id  # Store the user_id in the session
    # app = NotesApp(page)  # Create the NotesApp instance
    # page.add(app)  # Add the NotesApp to the page
    # page.update()  # Refresh the page to show the NotesApp screen

def main(page: ft.Page):
    page.title = "EvoNote"
    
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
            print(f"User ID: {user_id}")
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

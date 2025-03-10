import flet as ft
import firebase_admin
from firebase_admin import auth, credentials
import requests

# Initialize Firebase
cred = credentials.Certificate(r"CSC2218-Group-4-Project-2025/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


class AuthManager:
    """Handles user authentication with Firebase"""

    @staticmethod
    def register_user(email: str, password: str):
        """Registers a new user in Firebase Auth"""
        try:
            user = auth.create_user(email=email, password=password)
            return {"success": True, "message": f"User {user.uid} created successfully.", 'userid': user.uid}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def login_user(email: str, password: str):
        """Logs in user and generates a Firebase token"""
        firebase_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDd1qWlXMFU0kU0-98cIbiV34iIEbT44so"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(firebase_url, json=payload)
        if response.status_code == 200:
            user = auth.get_user_by_email(email)
            user_id = user.uid
            return {"success": True, "data": response.json(), "user_id": user_id}
        else:
            return {"success": False, "message": response.json().get("error", {}).get("message", "Login failed")}

    @staticmethod
    def logout(page: ft.Page):
        """Clears user session"""
        page.session.clear()  # Clear session after logout
        page.go("/")  # Redirect to login page
        return {"success": True, "message": "User logged out successfully."}

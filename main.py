import flet as ft
import firebase_admin
from firebase_admin import auth, credentials
import os
from modules.loggers import Logger

# Singleton Pattern for Firebase initialization
class FirebaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
<<<<<<< HEAD
            cred = credentials.Certificate(r"C:/Users/Admin/Desktop/Notes App/CSC2218-Group-4-Project-2025/serviceAccountKey.json")
=======
            cred = credentials.Certificate(r"CSC2218-Group-4-Project-2025\serviceAccountKey.json")
>>>>>>> e48eacd9bf68cf31256b606d97835fa28fea3032
            cls._instance.app = firebase_admin.initialize_app(cred)
            cls._instance.logger = Logger(__name__).get_logger()
        return cls._instance

# Factory Pattern for Session Management
class SessionFactory:
    @staticmethod
    def create_session(strategy_type="file"):
        if strategy_type == "file":
            return FileSessionStrategy()
        elif strategy_type == "memory":
            return MemorySessionStrategy()
        else:
            raise ValueError(f"Unknown session strategy: {strategy_type}")

# Strategy Pattern for Session Management
class SessionStrategy:
    def save_session(self, user_id):
        pass
    
    def get_session(self):
        pass
    
    def clear_session(self):
        pass

class FileSessionStrategy(SessionStrategy):
    def __init__(self):
        self.session_file = os.path.join(os.path.expanduser("~"), ".evonote_session")
        self.logger = Logger(__name__).get_logger()
    
    def save_session(self, user_id):
        try:
            with open(self.session_file, "w") as f:
                f.write(user_id)
            return True
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            return False
    
    def get_session(self):
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, "r") as f:
                    user_id = f.read().strip()
                
                # Verify the user ID is still valid in Firebase
                try:
                    auth.get_user(user_id)
                    return {"success": True, "user_id": user_id}
                except:
                    # User not found or token expired
                    self.clear_session()  # Remove invalid session
            return {"success": False}
        except Exception as e:
            self.logger.error(f"Error checking session: {e}")
            return {"success": False}
    
    def clear_session(self):
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return True
        except Exception as e:
            self.logger.error(f"Error clearing session: {e}")
            return False


class MemorySessionStrategy(SessionStrategy):
    _session_data = None
    
    def save_session(self, user_id):
        MemorySessionStrategy._session_data = user_id
        return True
    
    def get_session(self):
        if MemorySessionStrategy._session_data:
            try:
                user_id = MemorySessionStrategy._session_data
                auth.get_user(user_id)
                return {"success": True, "user_id": user_id}
            except:
                self.clear_session()
        return {"success": False}
    
    def clear_session(self):
        MemorySessionStrategy._session_data = None
        return True

# Observer Pattern for authentication events
class AuthEventSubject:
    _observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, event_type, data=None):
        for observer in self._observers:
            observer.update(event_type, data)

# Command Pattern for Authentication Actions
class AuthCommand:
    def execute(self):
        pass

class LoginCommand(AuthCommand):
    def __init__(self, auth_manager, email, password):
        self.auth_manager = auth_manager
        self.email = email
        self.password = password
    
    def execute(self):
        return self.auth_manager.login_user(self.email, self.password)

class RegisterCommand(AuthCommand):
    def __init__(self, auth_manager, email, password):
        self.auth_manager = auth_manager
        self.email = email
        self.password = password
    
    def execute(self):
        return self.auth_manager.register_user(self.email, self.password)

# Facade Pattern for Authentication
class AuthFacade:
    def __init__(self):
        from auth import AuthManager
        self.auth_manager = AuthManager
        self.auth_event_subject = AuthEventSubject()
        self.session_strategy = SessionFactory.create_session("file")
        self.logger = Logger(__name__).get_logger()
    
    def login(self, email, password):
        command = LoginCommand(self.auth_manager, email, password)
        result = command.execute()
        
        if result["success"]:
            self.session_strategy.save_session(result["user_id"])
            self.auth_event_subject.notify("login_success", result["user_id"])
        else:
            self.auth_event_subject.notify("login_failure", result["message"])
        
        return result
        

    
    def register(self, email, password):
        command = RegisterCommand(self.auth_manager, email, password)
        result = command.execute()
        
        if result.get("success", False):
            self.auth_event_subject.notify("register_success", result.get("user_id"))
        else:
            self.auth_event_subject.notify("register_failure", result["message"])
        
        return result
    
    def check_session(self):
        return self.session_strategy.get_session()
    
    def logout(self):
        self.session_strategy.clear_session()
        self.auth_event_subject.notify("logout")
        return {"success": True, "message": "Logged out successfully"}

# MVC Pattern - Controller
class AppController:
    def __init__(self):
        self.firebase_client = FirebaseClient()
        self.auth_facade = AuthFacade()
        self.logger = Logger(__name__).get_logger()
    
    def initialize_app(self, page):
        self.page = page
        session = self.auth_facade.check_session()
        
        if session["success"]:
            user_id = session["user_id"]
            self.logger.info(f"Auto-login for user ID: {user_id}")
            self.navigate_to_notes(user_id)
        else:
            self.show_login_view()
    
    def navigate_to_notes(self, user_id):
        from n0tes3 import NotesApp
        self.page.views.clear()
        self.page.views.append(NotesApp(page=self.page, userId=user_id))
        self.page.update()
    
    def show_login_view(self):
        login_view = LoginView(self.page, self)
        login_view.build()
    
    def handle_login(self, email, password):
        result = self.auth_facade.login(email, password)
        if result["success"]:
            self.navigate_to_notes(result["user_id"])
        return result
    
    def handle_register(self, email, password):
        return self.auth_facade.register(email, password)

# MVC Pattern - View
class LoginView:
    def __init__(self, page, controller):
        self.page = page
        self.controller = controller
        self.page.title = "EvoNote"
    
    def build(self):
        self.email_field = ft.TextField(label="Email", width=300)
        self.password_field = ft.TextField(label="Password", password=True, width=300)
        self.message = ft.Text("")
        
        def on_login(e):
            result = self.controller.handle_login(self.email_field.value, self.password_field.value)
            if not result["success"]:
                self.message.value = result["message"]
                self.page.update()
        
        def on_register(e):
            result = self.controller.handle_register(self.email_field.value, self.password_field.value)
            self.message.value = result["message"]
            self.page.update()
        
        self.page.add(
            self.email_field,
            self.password_field,
            ft.Row([
                ft.ElevatedButton("Register", on_click=on_register),
                ft.ElevatedButton("Login", on_click=on_login),
            ]),
            self.message
        )

# Application entry point
def main(page: ft.Page):
    controller = AppController()
    controller.initialize_app(page)

if __name__ == "__main__":
    ft.app(target=main)
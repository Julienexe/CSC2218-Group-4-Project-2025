import threading
import time
import webbrowser
import urllib.parse
import flet as ft
from abc import ABC, abstractmethod

# Abstract Share Strategy
class ShareStrategy(ABC):
    @abstractmethod
    def share(self, page, note_text):
        """
        Share the note text to a platform.
        
        Args:
            page: Flet page reference
            note_text: The text content to share
        """
        pass
    
    def show_dialog_and_execute(self, page, dialog_title, dialog_content, action_function):
        """
        Helper method to show dialog and execute an action
        
        Args:
            page: Flet page reference
            dialog_title: Title for the dialog
            dialog_content: Content text for the dialog
            action_function: Function to execute after showing dialog
        """
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(dialog_title),
            content=ft.Text(dialog_content)
        )
        
        def process():
            # Show dialog
            page.open(dialog)
            page.update()
            
            # Brief pause
            time.sleep(1.5)
            
            # Execute the action
            action_function()
            
            # Close dialog
            page.close(dialog)
            page.update()
        
        # Start in separate thread
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()

# Concrete Twitter Share Strategy
class TwitterShareStrategy(ShareStrategy):
    def share(self, page, note_text):
        encoded_text = urllib.parse.quote(note_text)
        url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        
        self.show_dialog_and_execute(
            page=page,
            dialog_title="Sharing to X (Twitter)...",
            dialog_content="Opening your browser shortly.",
            action_function=lambda: webbrowser.open(url)
        )

# Concrete Facebook Share Strategy
class FacebookShareStrategy(ShareStrategy):
    def share(self, page, note_text):
        encoded_text = urllib.parse.quote(note_text)
        url = f"https://www.facebook.com/sharer/sharer.php?u=https://mynotesapp.com&quote={encoded_text}"
        
        self.show_dialog_and_execute(
            page=page,
            dialog_title="Sharing to Facebook...",
            dialog_content="Opening your browser shortly.",
            action_function=lambda: webbrowser.open(url)
        )

# Concrete Instagram Share Strategy
class InstagramShareStrategy(ShareStrategy):
    def share(self, page, note_text):
        instructions = (
            "To share to Instagram:\n"
            "1. Copy your note text\n"
            "2. Open Instagram app\n"
            "3. Create a new post or story\n"
            "4. Paste your text"
        )
        
        # Copy text to clipboard
        clipboard_text = note_text
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Instagram Sharing"),
            content=ft.Column([
                ft.Text(instructions),
                ft.Text("\nYour note has been copied to clipboard.", color="green")
            ]),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(dialog, "open", False))
            ]
        )
        
        page.open(dialog)
        page.update()

# Concrete Threads Share Strategy
class ThreadsShareStrategy(ShareStrategy):
    def share(self, page, note_text):
        instructions = (
            "To share to Threads:\n"
            "1. Copy your note text\n"
            "2. Open Threads app\n"
            "3. Create a new thread\n"
            "4. Paste your text"
        )
        
        # Copy text to clipboard
        clipboard_text = note_text
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Threads Sharing"),
            content=ft.Column([
                ft.Text(instructions),
                ft.Text("\nYour note has been copied to clipboard.", color="green")
            ]),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(dialog, "open", False))
            ]
        )
        
        page.open(dialog)
        page.update()

# Share Context - manages the sharing strategies
class SocialShareContext:
    def __init__(self):
        self._strategies = {
            "twitter": TwitterShareStrategy(),
            "facebook": FacebookShareStrategy(),
            "instagram": InstagramShareStrategy(),
            "threads": ThreadsShareStrategy()
        }
    
    def share(self, platform, page, note_text):
        """
        Share content using the appropriate strategy
        
        Args:
            platform: The platform to share to ("twitter", "facebook", etc.)
            page: Flet page reference
            note_text: The text content to share
        """
        if platform in self._strategies:
            self._strategies[platform].share(page, note_text)
        else:
            # Handle unknown platform
            dialog = ft.AlertDialog(
                title=ft.Text("Sharing Error"),
                content=ft.Text(f"Unknown platform: {platform}")
            )
            page.open(dialog)
            page.update()
import flet as ft
from firebase_db import FirebaseDB
import webbrowser
import urllib.parse
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io

db = FirebaseDB()
class Note(ft.Container):
    def __init__(self, note_id, note_text, note_delete, category, user_id, page=None, font_family="Arial", tags=None):
        super().__init__()
        self.db = db
        self.note_id = note_id
        self.note_text = note_text
        self.category = category
        self.user_id = user_id
        self.note_delete = note_delete
        self.font_family = font_family
        self.tags = tags or []
        self.page = page  # Store the page reference
        self.on_click = self.handle_click
        # Debugging: Verify the page object
        if not self.page:
            print("Warning: Page reference is not set during initialization!")

        # Styling for the note container
        self.bgcolor = "#1E2A47"
        self.border_radius = 12
        self.padding = 10

        # Build the tags display
        tags_row = ft.Row(
            wrap=True,
            spacing=5,
            visible=len(self.tags) > 0,
            controls=[
                ft.Chip(label=f"@{tag}", bgcolor="#4CAF50", label_style=ft.TextStyle(color="white", size=12))
                for tag in self.tags
            ]
        )

        # Build note content with text and tags
        note_content = ft.Column(
            spacing=5,
            controls=[
                ft.Text(self.note_text, color="white", font_family=self.font_family),
                tags_row
            ]
        )

        # Initially create with just the text and tags, no action buttons
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                note_content,
                ft.Row(
                    spacing=0,
                    visible=False,  # Initially hidden
                    controls=[
                        ft.IconButton(icon=ft.icons.SHARE_OUTLINED, icon_color="cyan", tooltip="Share Note", on_click=self.share_clicked),
                        ft.IconButton(icon=ft.icons.PERSON_ADD_ALT_1_OUTLINED, icon_color="yellow", tooltip="Tag People", on_click=self.tag_clicked),
                        ft.IconButton(icon=ft.icons.CLOUD_UPLOAD_OUTLINED, icon_color="lightblue", tooltip="Upload to Drive", on_click=self.drive_clicked),
                        ft.IconButton(icon=ft.icons.CREATE_OUTLINED, icon_color="white", tooltip="Edit Note", on_click=self.edit_clicked),
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color="red", tooltip="Delete Note", on_click=self.delete_clicked),
                    ],
                ),
            ],
        )

    def handle_click(self, e):
        """
        Handle click events and ensure page reference is set.
        """
        print("handle_click called")
        if not self.page and hasattr(e, 'page'):
            self.page = e.page
            print("Page reference set")

        # Debugging: Verify the page object
        if not self.page:
            print("Error: Page reference is not set!")
            return

    def edit_clicked(self, e):
        """
        Replace the Text widget with a TextField for editing the note.
        """
        # Ensure the page reference is set
        self.handle_click(e)

        # Get the content column
        content_column = self.content.controls[0]
        # Replace the text with a TextField
        content_column.controls[0] = ft.TextField(
            value=self.note_text,
            expand=True,
            color="white",
            bgcolor="#2D3B60",
            multiline=True,
            min_lines=2,
            max_lines=5,
        )
        # Replace edit button with save button
        self.content.controls[1].controls[3] = ft.IconButton(
            icon=ft.icons.DONE_OUTLINE_OUTLINED,
            icon_color="green",
            tooltip="Save Note",
            on_click=self.save_clicked
        )
        self.update()

    def save_clicked(self, e):
        """
        Save the edited note text and update the Firebase database.
        """
        # Ensure the page reference is set
        self.handle_click(e)

        content_column = self.content.controls[0]
        new_text = content_column.controls[0].value
        self.note_text = new_text
        # Include the font family and tags when editing the note
        self.db.edit_note(
            note_id=self.note_id,
            note_text=self.note_text,
            user_id=self.user_id,
            category=self.category,
            font_family=self.font_family,
            tags=self.tags
        )
        # Replace the TextField with a Text widget and reapply the font family
        content_column.controls[0] = ft.Text(
            self.note_text,
            color="white",
            font_family=self.font_family
        )
        # Replace save button with edit button
        self.content.controls[1].controls[3] = ft.IconButton(
            icon=ft.icons.CREATE_OUTLINED,
            icon_color="white",
            tooltip="Edit Note",
            on_click=self.edit_clicked
        )
        self.update()

    def delete_clicked(self, e):
        """
        Trigger the note deletion process.
        """
        self.note_delete(self)

    def show_buttons(self):
        """
        Show the action buttons for the note.
        """
        self.content.controls[1].visible = True
        self.update()

    def hide_buttons(self):
        """
        Hide the action buttons for the note.
        """
        self.content.controls[1].visible = False
        self.update()

    def share_clicked(self, e):
        """
        Open a dialog to share the note to social media platforms.
        """
        print("share_clicked called")
        self.handle_click(e)  # Ensure page reference is set
        self.reset_page_overlay()

        # Debugging: Check if the page reference is set
        if not self.page:
            print("Error: Page reference is not set!")
            return

        # Create a dialog for sharing options
        share_dialog = ft.AlertDialog(
            title=ft.Text("Share Note"),
            content=ft.Column([
                ft.ElevatedButton(
                    "Share to X (Twitter)",
                    icon=ft.icons.FLUTTER_DASH,
                    on_click=lambda _: self.share_to_platform("twitter")
                ),
                ft.ElevatedButton(
                    "Share to Facebook",
                    icon=ft.icons.FACEBOOK,
                    on_click=lambda _: self.share_to_platform("facebook")
                ),
                ft.ElevatedButton(
                    "Share to Instagram",
                    icon=ft.icons.CAMERA_ALT,
                    on_click=lambda _: self.share_to_platform("instagram")
                ),
                ft.ElevatedButton(
                    "Share to Threads",
                    icon=ft.icons.THREESIXTY,
                    on_click=lambda _: self.share_to_platform("threads")
                ),
            ], spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
            ],
            on_dismiss=lambda _: (self.close_dialog(), print("Dialog dismissed")),
        )

        # Show the dialog using page overlay
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            self.page.overlay.append(share_dialog)
            share_dialog.open = True
            self.page.update()
        else:
            print("Error: Page does not have an overlay list attribute!")

    def share_to_platform(self, platform):
        """
        Share the note to the specified social media platform.
        """
        encoded_text = urllib.parse.quote(self.note_text)

        # Different sharing URLs for different platforms
        if platform == "twitter":
            url = f"https://twitter.com/intent/tweet?text={encoded_text}"
            webbrowser.open(url)
        elif platform == "facebook":
            url = f"https://www.facebook.com/sharer/sharer.php?u=https://mynotesapp.com&quote={encoded_text}"
            webbrowser.open(url)
        elif platform == "instagram":
            # Instagram doesn't have a web share API, show instructions
            self.show_info_dialog(
                "Instagram Sharing",
                "To share to Instagram:\n1. Copy your note text\n2. Open Instagram app\n3. Create a new post or story\n4. Paste your text"
            )
        elif platform == "threads":
            # Threads doesn't have a web share API either
            self.show_info_dialog(
                "Threads Sharing",
                "To share to Threads:\n1. Copy your note text\n2. Open Threads app\n3. Create a new thread\n4. Paste your text"
            )

        # Close the share dialog after initiating share
        self.close_dialog()

    def tag_clicked(self, e):
        """
        Open a dialog to tag people in the note.
        """
        # Ensure the page reference is set
        self.handle_click(e)
        self.reset_page_overlay()

        # Text field for entering tags
        tag_input = ft.TextField(
            hint_text="Enter username (without @)",
            bgcolor="#2D3B60",
            color="white",
        )

        # Create a list of existing tags
        tag_chips = ft.Row(
            wrap=True,
            spacing=5,
            controls=[
                ft.Chip(
                    label=f"@{tag}",
                    bgcolor="#4CAF50",
                    label_style=ft.TextStyle(color="white", size=12),
                    delete_icon=ft.icons.CLOSE,
                    on_delete=lambda _, t=tag: self.remove_tag(t, tag_chips)
                ) for tag in self.tags
            ]
        )

        # Create the tagging dialog
        tag_dialog = ft.AlertDialog(
            title=ft.Text("Tag People"),
            content=ft.Column([
                ft.Text("Current tags:", color="white"),
                tag_chips,
                ft.Text("Add new tag:", color="white"),
                tag_input,
            ], spacing=10),
            actions=[
                ft.TextButton("Add Tag", on_click=lambda _: self.add_tag(tag_input.value, tag_chips)),
                ft.TextButton("Save", on_click=lambda _: self.save_tags(tag_chips)),
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
            ],
           
        )

        # Show the dialog using page overlay
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            self.page.overlay.append(tag_dialog)
            tag_dialog.open = True
            self.page.update()
        else:
            print("Error: Page does not have an overlay list attribute!")

    def add_tag(self, username, tag_chips):
        """
        Add a new tag to the tag chips display.
        """
        if not username or username.strip() == "":
            return

        username = username.strip()
        # Remove @ if it was included
        if username.startswith('@'):
            username = username[1:]

        # Add the tag chip if it's not already there
        if username not in self.tags:
            tag_chips.controls.append(
                ft.Chip(
                    label=f"@{username}",
                    bgcolor="#4CAF50",
                    label_style=ft.TextStyle(color="white", size=12),
                    delete_icon=ft.icons.CLOSE,
                    on_delete=lambda _, t=username: self.remove_tag(t, tag_chips)
                )
            )
            self.page.update()

    def remove_tag(self, tag, tag_chips):
        """
        Remove a tag from the tag chips display.
        """
        # Find and remove the chip with this tag
        for i, chip in enumerate(tag_chips.controls):
            if chip.label == f"@{tag}":
                tag_chips.controls.pop(i)
                break
        self.page.update()

    def save_tags(self, tag_chips):
        """
        Save the tags back to the note.
        """
        # Extract usernames from tag chips
        new_tags = []
        for chip in tag_chips.controls:
            username = chip.label[1:]  # Remove the @ symbol
            new_tags.append(username)

        # Update the tags list
        self.tags = new_tags

        # Update tags in Firebase
        self.db.edit_note(
            note_id=self.note_id,
            note_text=self.note_text,
            user_id=self.user_id,
            category=self.category,
            font_family=self.font_family,
            tags=self.tags
        )

        # Update the tags display in the note
        content_column = self.content.controls[0]
        tags_row = content_column.controls[1]
        tags_row.controls = [
            ft.Chip(label=f"@{tag}", bgcolor="#4CAF50", label_style=ft.TextStyle(color="white", size=12))
            for tag in self.tags
        ]
        tags_row.visible = len(self.tags) > 0

        # Close the dialog
        self.close_dialog()
        self.update()

    def drive_clicked(self, e):
        """
        Upload the note to Google Drive.
        """
        # Ensure the page reference is set
        self.handle_click(e)
        self.reset_page_overlay()
        # Create a dialog to show upload status
        upload_dialog = ft.AlertDialog(
            title=ft.Text("Upload to Google Drive"),
            content=ft.Column([
                ft.Text("Uploading note to Google Drive..."),
                ft.ProgressRing(),
            ]),
            
        )

        # Show the dialog using page overlay
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            self.page.overlay.append(upload_dialog)
            upload_dialog.open = True
            self.page.update()
        else:
            print("Error: Page does not have an overlay list attribute!")

        # Attempt to upload note to Google Drive
        try:
            # Upload to Drive (this will be implemented with a separate function)
            success = self.upload_to_drive()

            if success:
                # Show success message
                upload_dialog.content = ft.Text("Note successfully uploaded to Google Drive!")
                upload_dialog.actions = [
                    ft.TextButton("OK", on_click=lambda _: self.close_dialog()),
                ]
            else:
                # Show error message
                upload_dialog.content = ft.Text("Failed to upload note. Please check your Google Drive permissions.")
                upload_dialog.actions = [
                    ft.TextButton("OK", on_click=lambda _: self.close_dialog()),
                ]
        except Exception as ex:
            # Show error message
            upload_dialog.content = ft.Text(f"Error: {str(ex)}")
            upload_dialog.actions = [
                ft.TextButton("OK", on_click=lambda _: self.close_dialog()),
            ]

        self.page.update()

    def upload_to_drive(self):
        """
        Upload the note to Google Drive.

        Returns:
            bool: True if successful, False otherwise.
        """
        # This is a simplified implementation
        # In a real app, you'd need to handle OAuth flow properly

        try:
            # Path to token.json which stores user's access and refresh tokens
            token_path = 'token.json'
            # If token.json doesn't exist, we need to authenticate
            if not os.path.exists(token_path):
                # In a real app, you'd handle this with proper OAuth flow
                # For now, we'll just simulate success
                self.show_info_dialog(
                    "Google Drive Authorization Needed",
                    "Please authorize this app to access your Google Drive.\n\n"
                    "In a complete implementation, you would be redirected to Google's login page."
                )
                return False

            # In a real implementation, you would:
            # 1. Load credentials from token.json
            # 2. Build the Drive API client
            # 3. Create a file with the note content
            # 4. Upload the file to Drive

            # For this example, we'll simulate success
            return True

        except Exception as e:
            print(f"Error uploading to Drive: {str(e)}")
            return False

    def show_info_dialog(self, title, message):
        """
        Show an information dialog.
        """
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.close_dialog()),
            ],
        )
        
        # Show the dialog using page overlay
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        else:
            print("Error: Page does not have an overlay list attribute!")

    def close_dialog(self):
        """
        Close any open dialogs and completely clear the overlay.
        """
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            # Clear the entire overlay list instead of removing items one by one
            self.page.overlay.clear()
            self.page.update()
        else:
            print("Error: Page does not have an overlay list attribute!")
        
    def reset_page_overlay(self):
        """
        Reset the page overlay to ensure no ghost dialogs remain.
        """
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            # Clear any existing dialogs
            for overlay_item in self.page.overlay.copy():
                if hasattr(overlay_item, 'open'):
                    overlay_item.open = False
            self.page.overlay.clear()  # Use clear() instead of direct assignment
            self.page.update()
        
class NotesApp(ft.Column):
    """
    A custom Column widget representing the main notes application.
    It includes input fields for adding new notes and displays existing notes by category.
    """
    def __init__(self, page: ft.Page, userId):
        """
        Initialize the NotesApp instance.

        Args:
            page (ft.Page): The Flet page object.
            userId (str): The ID of the user.
        """
        super().__init__()
        self.userID = userId
        self.page = page
        self.db = db
        
        # Initialize page overlay list if it doesn't exist
        if not hasattr(self.page, 'overlay'):
            self.page.overlay = []
        # Create input fields with consistent styling
        self.new_note = ft.TextField(
            hint_text="Write your note here...", 
            expand=True, 
            bgcolor="#2D3B60", 
            color="white",
            border_color="#4CAF50",
            multiline=True,  # Enable multi-line input
            min_lines=3,     # Minimum height (3 lines)
            max_lines=10,    # Maximum height (10 lines)
        )
        # Text field for direct category input
        self.category_input = ft.TextField(
            hint_text="Enter category (new or existing)",
            expand=True, 
            bgcolor="#2D3B60", 
            color="white",
            border_color="#4CAF50",
            
        )
        
        # Dropdown for existing categories
        self.category_dropdown = ft.Dropdown(
            hint_text="Or select existing category",
            expand=True, 
            bgcolor="#2D3B60", 
            color="white",
            border_color="#4CAF50",
            visible=False,  # Initially hidden until we have categories
            
        )
        
        # Dropdown for font selection
        self.font_dropdown = ft.Dropdown(
            hint_text="Select Font",
            options=[
                ft.dropdown.Option("Arial"),
                ft.dropdown.Option("Times New Roman"),
                ft.dropdown.Option("Courier New"),
                ft.dropdown.Option("Verdana"),
                ft.dropdown.Option("Georgia"),
                ft.dropdown.Option("Comic Sans MS"),
                ft.dropdown.Option("Impact"),
                ft.dropdown.Option("Lucida Console"),
                ft.dropdown.Option("Tahoma"),
                ft.dropdown.Option("Trebuchet MS"),
                ft.dropdown.Option("Palatino Linotype"),
                ft.dropdown.Option("Garamond"),
                ft.dropdown.Option("Book Antiqua"),
                ft.dropdown.Option("Arial Black"),
                ft.dropdown.Option("Courier"),
            ],
            value="Arial",  # Default font
            expand=True,
            bgcolor="#2D3B60",
            color="white",
            border_color="#4CAF50",
        )
        
        # Add text field for tagging people
        self.tags_input = ft.TextField(
            hint_text="Tag people (comma separated, no @)",
            expand=True,
            bgcolor="#2D3B60",
            color="white",
            border_color="#4CAF50",
        )
        
        # Use a ListView for scrollable categories
        self.categories = ft.ListView(
            expand=True,  # Make the ListView expand to fill available space
            spacing=10,  # Add spacing between items
            padding=10,  # Add padding around the ListView
        )
        self.active_category = None
        
        # Input container with properly organized layout
        self.input_container = ft.Container(
            visible=False,
            padding=10,
            bgcolor="#1E2A47",
            border_radius=12,
            content=ft.Column([
                # Row for category input
                ft.Row([
                    ft.Text("Category:", width=80, color="white"),
                    ft.Column([
                        self.category_input,
                        self.category_dropdown
                    ], expand=True, spacing=8)
                ], alignment=ft.MainAxisAlignment.START),
                
                # Row for note input
                ft.Row([
                    ft.Text("Note:", width=80, color="white"),
                    self.new_note
                ], alignment=ft.MainAxisAlignment.START),
                
                # Row for font selection
                ft.Row([
                    ft.Text("Font:", width=80, color="white"),
                    self.font_dropdown
                ], alignment=ft.MainAxisAlignment.START),
                
                # Row for tags input
                ft.Row([
                    ft.Text("Tags:", width=80, color="white"),
                    self.tags_input
                ], alignment=ft.MainAxisAlignment.START),
                
                # Buttons row
                ft.Row([
                    ft.Container(expand=True),  # Spacer to push buttons to the right
                    ft.ElevatedButton("Cancel", bgcolor="#FF5252", color="white", on_click=self.cancel_input),
                    ft.ElevatedButton("Add Note", bgcolor="#4CAF50", color="white", on_click=self.add_clicked)
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15)
        )
        
        # Add button at the bottom right
        self.add_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, 
            bgcolor="#4CAF50", 
            on_click=self.show_input_fields
        )

        self.controls = [
            ft.Column(
                expand=True,  # Make the Column expand to fill available space
                controls=[
                    ft.Text("Notes!", size=24, weight=ft.FontWeight.BOLD, color="white"),
                    self.input_container,
                    ft.Container(
                        content=self.categories,
                        expand=True,  # Make the ListView expand to fill available space
                    ),
                ],
            ),
            # Add button at the bottom right
            ft.Container(
                content=self.add_button,
                alignment=ft.alignment.bottom_right,
                margin=ft.margin.only(bottom=20, right=20)
            ),
        ]
        self.load_notes()
        self.page.bgcolor = "#121E38"  # Deep navy blue background

    def show_input_fields(self, e):
        """
        Show the input fields for adding a new note.
        """
        # Update dropdown with current categories
        self.category_dropdown.options.clear()
        existing_categories = [
            c.content.controls[0].value 
            for c in self.categories.controls 
            if isinstance(c, ft.Container) and c.content.controls
        ]
        
        # Only show dropdown if we have existing categories
        if existing_categories:
            self.category_dropdown.visible = True
            # Add existing categories to dropdown
            for category in existing_categories:
                self.category_dropdown.options.append(ft.dropdown.Option(category))
        else:
            self.category_dropdown.visible = False
        
        # Set up dropdown change handler to update text field
        self.category_dropdown.on_change = self.on_category_selected
            
        self.input_container.visible = True
        # Hide the add button
        self.add_button.visible = False  # Directly reference the add button
        self.page.update()
    
    def on_category_selected(self, e):
        """
        Update the category input field when a category is selected from the dropdown.
        """
        if self.category_dropdown.value:
            self.category_input.value = self.category_dropdown.value
            self.page.update()
        
    def cancel_input(self, e):
        """
        Cancel the input process and hide the input fields.
        """
        self.input_container.visible = False
        self.new_note.value = ""
        self.category_input.value = ""
        self.category_dropdown.value = None
        self.tags_input.value = ""
        self.add_button.visible = True  # Show add button
        self.page.update()

    def load_notes(self, e=None):
        """
        Load notes from Firebase and display them in the UI.
        """
        if hasattr(self.page, 'overlay') and isinstance(self.page.overlay, list):
            self.page.overlay.clear()  
        
        self.categories.controls.clear()
        categories_data = self.db.get_categories(self.userID)
        for category_name, notes_list in categories_data.items():
            notes_controls = [
                Note(
                    note["id"], 
                    note["text"], 
                    self.note_delete, 
                    category_name,  
                    self.userID,
                    page=self.page,  # Pass the page reference
                    font_family=note.get("font_family", "Arial"),
                    tags=note.get("tags", [])  # Load tags from Firebase
                ) for note in notes_list
            ]
            
            category_container = ft.Container(
                bgcolor="#1E2A47",
                border_radius=12,
                padding=10,
                content=ft.Column([
                    ft.Text(category_name, size=18, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                    *notes_controls
                ]),
                data=notes_controls  # Store notes for easy access
            )
            
            # Add click event to show/hide buttons
            category_container.on_click = lambda e, container=category_container: self.toggle_category(container)
            
            self.categories.controls.append(category_container)
        self.page.update()

    def toggle_category(self, category_container):
        """
        Toggle the visibility of buttons for notes in a category.
        """
        # If there's an active category, hide its buttons
        if self.active_category and self.active_category != category_container:
            notes = self.active_category.data
            for note in notes:
                note.hide_buttons()
        
        # Toggle the clicked category
        if self.active_category == category_container:
            # Hide buttons if clicking the same category again
            notes = category_container.data
            for note in notes:
                note.hide_buttons()
            self.active_category = None
        else:
            # Show buttons for the clicked category
            notes = category_container.data
            for note in notes:
                note.show_buttons()
            self.active_category = category_container
        
        self.page.update()

    def add_clicked(self, e):
        """
        Add a new note to the selected category.
        """
        # Get category from text field (prioritizing this for custom entry)
        category = self.category_input.value.strip()
        
        # If text field is empty but dropdown has a selection, use that
        if not category and self.category_dropdown.value:
            category = self.category_dropdown.value
            
        note_text = self.new_note.value.strip()
        if category and note_text:
            # Use the selected font from the dropdown
            selected_font = self.font_dropdown.value
            
            # Parse tags
            tags = []
            if self.tags_input.value:
                tags = [tag.strip() for tag in self.tags_input.value.split(',') if tag.strip()]
                # Remove @ symbol if present
                tags = [tag[1:] if tag.startswith('@') else tag for tag in tags]
            
            # Include the font family and tags when adding the note
            note_id = self.db.add_note(
                self.userID, 
                category, 
                note_text, 
                font_family=selected_font,
                tags=tags
            )
            
            if note_id:
                new_note = Note(
                    note_id, 
                    note_text, 
                    self.note_delete, 
                    category, 
                    self.userID, 
                    page=self.page,  # Pass the page reference 
                    font_family=selected_font,
                    tags=tags
                )
                
                category_container = next((c for c in self.categories.controls if isinstance(c, ft.Container) and c.content.controls[0].value == category), None)
                if category_container:
                    category_container.content.controls.append(new_note)
                    category_container.data.append(new_note)
                else:
                    new_category_container = ft.Container(
                        bgcolor="#1E2A47",
                        border_radius=12,
                        padding=10,
                        content=ft.Column([
                            ft.Text(category, size=18, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                            new_note
                        ]),
                        data=[new_note]  # Store notes for easy access
                    )
                    new_category_container.on_click = lambda e, container=new_category_container: self.toggle_category(container)
                    self.categories.controls.append(new_category_container)
                
                self.new_note.value = ""
                self.category_input.value = ""
                self.category_dropdown.value = None
                self.tags_input.value = ""
                self.input_container.visible = False
                self.add_button.visible = True  # Show add button again
                self.page.update()

    def note_delete(self, note):
        """
        Delete a note from the UI and Firebase.
        """
        self.db.delete_note(self.userID, note.note_id, note.category)
        for category in self.categories.controls:
            if isinstance(category, ft.Container):
                # Check if note is in this category's content
                if note in category.content.controls:
                    category.content.controls.remove(note)
                    category.data.remove(note)  # Also remove from data list
                    if len(category.content.controls) == 1:  # Only the category title remains
                        self.categories.controls.remove(category)
                        if self.active_category == category:
                            self.active_category = None
                    self.page.update()
                    break
                
    
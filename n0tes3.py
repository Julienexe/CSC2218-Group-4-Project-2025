import flet as ft
from firebase_db import FirebaseDB

class Note(ft.Container):
    """
    A custom Container widget representing a single note.
    Each note contains text, an edit button, and a delete button.
    """
    def __init__(self, note_id, note_text, note_delete, category, user_id, font_family="Arial"):
        """
        Initialize a Note instance.

        Args:
            note_id (str): Unique identifier for the note.
            note_text (str): The text content of the note.
            note_delete (function): Callback function to delete the note.
            category (str): The category to which the note belongs.
            user_id (str): The ID of the user who owns the note.
            font_family (str, optional): The font family for the note text. Defaults to "Arial".
        """
        super().__init__()
        self.note_id = note_id
        self.note_text = note_text
        self.category = category
        self.user_id = user_id
        self.note_delete = note_delete
        self.font_family = font_family  # Store the font family

        # Styling for the note container
        self.bgcolor = "#1E2A47"  # Dark blue background for contrast
        self.border_radius = 12
        self.padding = 10
        
        # Initially create with just the text, no buttons
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(self.note_text, color="white", expand=True, font_family=self.font_family),  # Set font here
                ft.Row(
                    spacing=0,
                    visible=False,  # Initially hidden
                    controls=[
                        ft.IconButton(icon=ft.icons.CREATE_OUTLINED, icon_color="white", tooltip="Edit Note", on_click=self.edit_clicked),
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color="red", tooltip="Delete Note", on_click=self.delete_clicked),
                    ],
                ),
            ],
        )

    def edit_clicked(self, e):
        """
        Replace the Text widget with a TextField for editing the note.
        """
        self.content.controls[0] = ft.TextField(
            value=self.note_text, 
            expand=True, 
            color="white", 
            bgcolor="#2D3B60",
        )
        self.content.controls[1].controls[0] = ft.IconButton(
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
        new_text = self.content.controls[0].value
        self.note_text = new_text
        # Include the font family when editing the note
        FirebaseDB.edit_note(
            note_id=self.note_id, 
            note_text=self.note_text, 
            user_id=self.user_id, 
            category=self.category,
            font_family=self.font_family  # Pass the font family
        )
        # Replace the TextField with a Text widget and reapply the font family
        self.content.controls[0] = ft.Text(
            self.note_text, 
            color="white", 
            expand=True, 
            font_family=self.font_family  # Reapply the font family
        )
        self.content.controls[1].controls[0] = ft.IconButton(
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
        Show the edit and delete buttons for the note.
        """
        self.content.controls[1].visible = True
        self.update()
    
    def hide_buttons(self):
        """
        Hide the edit and delete buttons for the note.
        """
        self.content.controls[1].visible = False
        self.update()


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
        self.add_button.visible = True  # Show add button
        self.page.update()

    def load_notes(self, e=None):
        """
        Load notes from Firebase and display them in the UI.
        """
        self.categories.controls.clear()
        categories_data = FirebaseDB.get_categories(self.userID)
        for category_name, notes_list in categories_data.items():
            notes_controls = [
                Note(
                    note["id"], 
                    note["text"], 
                    self.note_delete, 
                    category_name,  
                    self.userID,
                    font_family=note.get("font_family", "Arial")  # Use the saved font family
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
            # Include the font family when adding the note
            note_id = FirebaseDB.add_note(self.userID, category, note_text, font_family=selected_font)
            if note_id:
                new_note = Note(note_id, note_text, self.note_delete, category, self.userID, font_family=selected_font)
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
                self.input_container.visible = False
                self.add_button.visible = True  # Show add button again
                self.page.update()

    def note_delete(self, note):
        """
        Delete a note from the UI and Firebase.
        """
        FirebaseDB.delete_note(self.userID, note.note_id, note.category)
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
import flet as ft
from firebase_db import FirebaseDB

class Note(ft.Column):
    def __init__(self, note_id, note_text, note_delete, category, user_id):
        super().__init__()
        self.note_id = note_id
        self.note_text = note_text
        self.category = category
        self.user_id = user_id
        self.note_delete = note_delete
        self.display_note = ft.Text(self.note_text, expand=True)
        self.edit_name = ft.TextField(value=self.note_text, expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_note,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit Note",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete Note",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )
        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Save Note",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_note.value
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_note.value = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        FirebaseDB.edit_note(note_id=self.note_id, note_text=self.display_note.value, user_id=self.user_id, category=self.category)
        self.update()

    def delete_clicked(self, e):
        self.note_delete(self)


class Category(ft.Column):
    def __init__(self, category_name, notes):
        super().__init__()
        self.category_name = category_name
        self.notes = notes
        self.expanded = False

        self.title = ft.Text(category_name, size=18, weight=ft.FontWeight.BOLD)
        self.expand_icon = ft.IconButton(icon=ft.icons.EXPAND_MORE, on_click=self.toggle_notes)

        self.header = ft.Row(
            controls=[self.title, self.expand_icon],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.notes_column = ft.Column(visible=False, controls=notes)

        self.controls = [self.header, self.notes_column]

    def toggle_notes(self, e):
        self.expanded = not self.expanded
        self.notes_column.visible = self.expanded
        self.expand_icon.icon = ft.icons.EXPAND_LESS if self.expanded else ft.icons.EXPAND_MORE
        self.update()


class NotesApp(ft.Column):
    def __init__(self, page: ft.Page, userId):
        super().__init__()
        self.userID = userId
        self.page = page
        self.new_note = ft.TextField(hint_text="Write your note here...", expand=True)
        self.new_category = ft.TextField(hint_text="Category", expand=True)
        self.categories = ft.Column()

        self.controls = [
            ft.Row(
                controls=[
                    self.new_category,
                    self.new_note,
                    ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                ],
            ),
            
            self.categories,
        ]
        self.load_notes()

    def load_notes(self, e=None):
        """Load notes grouped by categories"""
        self.categories.controls.clear()
        categories_data = FirebaseDB.get_categories(self.userID)
        
        # Debug: Print what we're getting from Firebase
        print(f"Loaded categories for user {self.userID}: {categories_data}")

        for category_name, notes_list in categories_data.items():
            notes_controls = [
                Note(
                    note["id"], 
                    note["text"], 
                    self.note_delete, 
                    category_name,  # Pass the category
                    self.userID     # Pass the user ID
                ) for note in notes_list
            ]
            category = Category(category_name, notes_controls)
            self.categories.controls.append(category)

        self.page.update()

    def add_clicked(self, e):
        """Add a new note to a category"""
        category = self.new_category.value.strip()
        note_text = self.new_note.value.strip()

        if category and note_text:
            note_id = FirebaseDB.add_note(self.userID, category, note_text)

            if note_id:
                # Check if category already exists
                category_found = False
                for category_widget in self.categories.controls:
                    if category_widget.category_name == category:
                        category_found = True
                        new_note = Note(note_id, note_text, self.note_delete, category, self.userID)
                        category_widget.notes.append(new_note)
                        category_widget.notes_column.controls.append(new_note)  # Add to visible controls
                        category_widget.update()
                        break
                
                # If category doesn't exist, create it
                if not category_found:
                    new_note = Note(note_id, note_text, self.note_delete, category, self.userID)
                    new_category = Category(category, [new_note])
                    self.categories.controls.append(new_category)

                self.new_note.value = ""
                self.new_category.value = ""
                self.page.update()

    def note_delete(self, note):
        """Delete note from Firestore and UI"""
        FirebaseDB.delete_note(self.userID, note.note_id, note.category)
        for category in self.categories.controls:
            if note in category.notes:
                category.notes.remove(note)  # Fixed typo: 'contols' -> 'controls'
                category.notes_column.controls.remove(note)  # Also remove from visible controls
                
                # If no notes left in this category, optionally remove the category
                if len(category.notes) == 0:
                    self.categories.controls.remove(category)
                
                category.update()
                break
        self.page.update()
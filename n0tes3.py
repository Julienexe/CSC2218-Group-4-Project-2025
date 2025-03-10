import flet as ft
from firebase_db import FirebaseDB

USER_ID = ''  # This will be dynamically set based on the logged-in user


class Note(ft.Column):
    def __init__(self, note_id, note_text, note_delete):
        super().__init__()
        self.note_id = note_id
        self.note_text = note_text
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
        FirebaseDB.edit_note(note_id=self.note_id, note_text=self.display_note.value )
        self.update()

    def delete_clicked(self, e):
        self.note_delete(self)


class NotesApp(ft.Column):
    def __init__(self, page: ft.Page, userId):
        super().__init__()
        self.userID = userId
        self.page = page
        self.new_note = ft.TextField(hint_text="Write your note here...", expand=True)
        self.notes = ft.Column()
        self.controls = [
            ft.Row(
                controls=[
                    self.new_note,
                    ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                ],
            ),
            self.notes,
        ]
        self.load_notes()

    def load_notes(self):
        """Load notes from Firestore on startup"""
        notes_data = FirebaseDB.get_notes(self.userID)
        for note in notes_data:
            self.notes.controls.append(Note(note["id"], note["text"], self.note_delete))
        self.page.update()

    def add_clicked(self, e):
        """Add a new note to Firestore and UI"""
        if self.new_note.value.strip():
            note_id = FirebaseDB.add_note(self.userID, self.new_note.value)
            
            if note_id:
                note = Note(note_id, self.new_note.value, self.note_delete)
                self.notes.controls.append(note)
                self.new_note.value = ""
                self.page.update()

    def note_delete(self, note):
        """Delete note from Firestore and UI"""
        FirebaseDB.delete_note(self.userID, note.note_id)
        self.notes.controls.remove(note)
        self.page.update()


# def main(page: ft.Page):
#     page.title = "Cloud Notes"
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#     page.update()

#     # Assign USER_ID after login
#     USER_ID = page.session.get("user_uid")  # This assumes the user ID is stored in session

#     app = NotesApp(page)
#     page.add(app)

# ft.app(target=main)

import flet as ft

class Note(ft.Column):
    def __init__(self, note_content, note_delete):
        super().__init__()
        self.note_content = note_content
        self.note_delete = note_delete
        self.edit_mode = False

        self.display_text = ft.Text(self.note_content, expand=True)
        self.edit_text = ft.TextField(value=self.note_content, multiline=True, expand=True)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_text,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(icon=ft.icons.EDIT, tooltip="Edit Note", on_click=self.edit_clicked),
                        ft.IconButton(icon=ft.icons.DELETE, tooltip="Delete Note", on_click=self.delete_clicked),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_text,
                ft.IconButton(icon=ft.icons.CHECK, icon_color=ft.colors.GREEN, tooltip="Save Note", on_click=self.save_clicked),
            ],
        )
        
        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_text.value = self.display_text.value
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_text.value = self.edit_text.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def delete_clicked(self, e):
        self.note_delete(self)


class NotesApp(ft.Column):
    def __init__(self):
        super().__init__()
        self.new_note = ft.TextField(hint_text="Write a new note...", multiline=True, expand=True)
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

    def add_clicked(self, e):
        if self.new_note.value.strip():
            note = Note(self.new_note.value.strip(), self.note_delete)
            self.notes.controls.append(note)
            self.new_note.value = ""
            self.update()

    def note_delete(self, note):
        self.notes.controls.remove(note)
        self.update()


def main(page: ft.Page):
    page.title = "Notes App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    app = NotesApp()
    page.add(app)

ft.app(target=main)

import flet as ft

def main(page: ft.Page):
    page.title = "Notes App"
    
    def add_note(e): # create new notes in the app
        if note_input.value.strip():
            notes_view.controls.append(
                ft.ListTile(
                    title=ft.Text(note_input.value),
                    trailing=ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, t=note_input.value: delete_note(e, t))
                )
            )
            note_input.value = ""
            page.update()
    
    def delete_note(e, note_text):
        notes_view.controls = [note for note in notes_view.controls if note.title.value != note_text]
        page.update()
    
    note_input = ft.TextField(hint_text="Write your note here...", expand=True)
    notes_view = ft.Column()
    
    view = ft.Column(
        width=600,
        controls=[
            ft.Row(
                controls=[
                    note_input,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_note),
                ],
            ),
            notes_view,
        ],
    )
    
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(view)

ft.app(target=main)

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from views.screens.edit_task_popup import EditTaskDialog
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from services.config import BASE_URL
import requests



class TaskItemView(BoxLayout):
    task_id = NumericProperty(0)
    title = StringProperty("")
    description = StringProperty("")
    due_date = StringProperty("")
    priority = StringProperty("")
    completed = BooleanProperty(False)
    controller = ObjectProperty(None)

    def on_checkbox_active(self, checkbox, value):
        if value:
            self.mark_task_complete_api()
            self.show_custom_dialog()
            Clock.schedule_once(lambda dt: self.remove_task_from_ui(), 0.2)

    def mark_task_complete_api(self):
        try:
            response = requests.patch(
                f"{BASE_URL}/tasks/completion/{self.task_id}",
                json={"completed": True}
            )
            response.raise_for_status()
            print("Task marked complete:", response.json())
        except requests.RequestException as e:
            print("Failed to update task completion:", e)

    def delete_self(self):
        if self.parent:
            self.parent.remove_widget(self)
        try:
            response = requests.delete(f"{BASE_URL}/tasks/{self.task_id}")
            response.raise_for_status()
            print("Task deleted successfully")
        except requests.RequestException as e:
            print("Failed to delete task:", e)

    def remove_task_from_ui(self):
        if self.parent:
            anim = Animation(opacity=0, duration=0.2)
            anim.bind(on_complete=lambda *a: self.parent.remove_widget(self))
            anim.start(self)

    def show_custom_dialog(self):
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                type="custom",
                title="",
                content_cls=MDBoxLayout(
                    MDLabel(text="Congrats!! Task completed!", halign="center"),
                    padding="12dp",
                    adaptive_height=True
                ),
                buttons=[
                    MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss())
                ]
            )
        self.dialog.open()

    def open_edit_popup(self):
        task_data = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority
        }
        dialog = EditTaskDialog(controller=self.controller, task_data=task_data)
        dialog.open()

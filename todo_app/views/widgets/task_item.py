# task_item.py
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from services.database import Database
from views.screens.edit_task_popup import EditTaskDialog
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel







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
            self.controller.toggle_task_completion(self.task_id, value)
            self.show_custom_dialog()
            Clock.schedule_once(lambda dt: self.remove_task_from_ui(), 0.2)  # Small delay for smoothness


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


    def delete_self(self):
        if self.parent:
            self.parent.remove_widget(self)
        Database.delete_task(self.task_id)

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
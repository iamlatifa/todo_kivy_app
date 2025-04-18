# edit_task_popup.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.clock import Clock

class EditTaskPopup(MDBoxLayout):
    task_id = NumericProperty()
    title = StringProperty("")
    description = StringProperty("")
    due_date = StringProperty("")
    priority = StringProperty("Low")
    controller = ObjectProperty()
    task_data = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # We'll populate fields after a short delay to ensure the widget is fully loaded
        Clock.schedule_once(self.populate_fields, 0.1)

    def populate_fields(self, *args):
        if not hasattr(self, 'ids') or not self.ids:
            print("Warning: IDs not available yet")
            return
            
        print(f"Populating fields with data: {self.task_data}")
        
        # Populate text fields
        self.ids.task_title_input.text = self.task_data.get("title", "")
        self.ids.task_description_input.text = self.task_data.get("description", "")
        self.ids.task_due_date_input.text = self.task_data.get("due_date", "")
        
        # Set priority
        self.priority = self.task_data.get("priority", "Low")
        
        # Highlight the correct priority button
        self.update_priority_buttons()
        
    def update_priority_buttons(self):
        # Dictionary mapping priority values to button IDs
        if not hasattr(self, 'ids') or not self.ids:
            return
            
        priority_buttons = {
            "Low": self.ids.btn_low,
            "Medium": self.ids.btn_medium,
            "High": self.ids.btn_high,
            "Urgent": self.ids.btn_urgent
        }
        
        # Reset all buttons
        for btn in priority_buttons.values():
            btn.md_bg_color = [0, 0, 0, 0]  # Transparent background
        
        # Highlight the selected priority button if it exists in our mapping
        if self.priority in priority_buttons:
            priority_buttons[self.priority].md_bg_color = [0.2, 0.6, 1, 0.2]  # Light blue highlight

    def set_priority(self, value):
        self.priority = value
        self.update_priority_buttons()


class EditTaskDialog:
    def __init__(self, controller, task_data):
        self.controller = controller
        self.task_data = task_data
        print(f"Creating dialog with task data: {task_data}")

        # Create the content widget with the task data
        self.content = EditTaskPopup(
            controller=controller,
            task_id=task_data.get("id", 0),
            task_data=task_data
        )

        # Create the dialog with our content
        self.dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=self.content,
            size_hint=(0.9, None),
            buttons=[
                MDRaisedButton(text="Save", on_release=self.save_task),
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
            ],
        )

    def open(self):
        self.dialog.open()

    def save_task(self, instance):
        updated_data = {
            "title": self.content.ids.task_title_input.text,
            "description": self.content.ids.task_description_input.text,
            "due_date": self.content.ids.task_due_date_input.text,
            "priority": self.content.priority,
        }
        
        print(f"Saving updated task data: {updated_data}")
        self.controller.update_task(self.task_data["id"], **updated_data)
        self.dialog.dismiss()
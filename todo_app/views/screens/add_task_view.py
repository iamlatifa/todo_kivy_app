from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import os
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from functools import partial

KV_PATH = os.path.join(os.path.dirname(__file__), '..', 'kv', 'add_task_view.kv')


class AddTaskView(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file(os.path.abspath(KV_PATH))
        self.due_date = None
        self.priority_menu = None
        self.create_priority_menu()

    def on_pre_enter(self):
        self.clear_fields()
        # self.ids.title_input.focus = True  #keyboard pop up


    def clear_fields(self):
        self.ids.title_input.text = ''
        self.ids.description_input.text = ''
        self.ids.priority_input.text = 'Priority'  # Reset to default text
        self.ids.due_date_input.text = ''
        self.due_date = None

    def create_priority_menu(self):
        priorities = ["Low", "Medium", "High", "Urgent"]
        priority_items = []

        for priority in priorities:
            priority_items.append({
                "text": priority,
                "on_release": partial(self.set_priority, priority)
            })

        self.priority_menu = MDDropdownMenu(
            caller=self.ids.priority_input,
            items=priority_items,
            width_mult=4
        )

    def open_priority_menu(self):
        if self.priority_menu:
            self.priority_menu.open()

    def set_priority(self, priority_text):
        print("Selected priority:", priority_text)
        self.ids.priority_input.text = priority_text
        self.priority_menu.dismiss()

    def save_task(self):
        title = self.ids.title_input.text
        description = self.ids.description_input.text
        priority = self.ids.priority_input.text
        due_date = self.due_date

        print("Saving task...")
        print("Title:", title)
        print("Description:", description)
        print("Priority:", priority)
        print("Due Date:", due_date)

    def set_due_date(self, date_obj):
        self.due_date = date_obj.strftime("%d-%m-%Y")
        self.ids.due_date_input.text = self.due_date

    def open_date_picker(self):
        date_picker = MDDatePicker(mode="picker")  # Clean compact dialog mode
        date_picker.bind(on_save=lambda instance, value, date_range: self.set_due_date(value))
        date_picker.open()


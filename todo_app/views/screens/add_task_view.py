from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from functools import partial
import os

KV_PATH = os.path.join(os.path.dirname(__file__), '..', 'kv', 'add_task_view.kv')

class AddTaskView(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file(os.path.abspath(KV_PATH))
        self.controller = None  # Set externally
        self.due_date = None
        self.priority_menu = self._create_priority_menu()

    def on_pre_enter(self):
        self._clear_fields()

    def _clear_fields(self):
        self.ids.title_input.text = ''
        self.ids.description_input.text = ''
        self.ids.priority_input.text = 'Priority'
        self.ids.due_date_input.text = ''
        self.due_date = None

    def _create_priority_menu(self):
        priorities = ["Low", "Medium", "High", "Urgent"]
        items = [{"text": p, "on_release": partial(self._set_priority, p)} for p in priorities]
        return MDDropdownMenu(caller=self.ids.priority_input, items=items, width_mult=4)

    def open_priority_menu(self):
        if self.priority_menu:
            self.priority_menu.open()

    def _set_priority(self, priority_text):
        self.ids.priority_input.text = priority_text
        self.priority_menu.dismiss()

    def open_date_picker(self):
        picker = MDDatePicker(mode="picker")
        picker.bind(on_save=lambda instance, value, date_range: self._set_due_date(value))
        picker.open()

    def _set_due_date(self, date_obj):
        self.due_date = date_obj.strftime("%d-%m-%Y")
        self.ids.due_date_input.text = self.due_date

    def save_task(self):
        if not self.controller:
            print("Controller not assigned.")
            return

        title = self.ids.title_input.text.strip()
        description = self.ids.description_input.text.strip()
        priority = self.ids.priority_input.text
        due_date = self.due_date

        if not title or priority == "Priority":
            print("Title and priority are required.")
            return

        self.controller.add_task(title, description, due_date, priority)
        self.manager.current = "home"

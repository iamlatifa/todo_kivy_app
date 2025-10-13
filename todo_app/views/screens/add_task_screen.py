from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
import os
from datetime import datetime



KV_PATH = os.path.join(os.path.dirname(__file__), '..', 'kv', 'add_task_screen.kv')

class AddTaskView(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = None  # Set externally
        self._due_date = None
        self.menu = None
        self.date_dialog = None
        Clock.schedule_once(self.setup_priority_menu)

    def on_pre_enter(self):
        self._clear_fields()


    def _clear_fields(self):
        self.ids.title_input.text = ''
        self.ids.description_input.text = ''
        self.ids.priority_input.text = 'select priority'
        self.ids.due_date_input.text = ''
        self._due_date = None

        # Reset line/text colors
        self.ids.description_input.line_color_normal = (0, 0, 0, 0)
        self.ids.description_input.text_color = (0, 0, 0, 1)
        self.ids.due_date_input.line_color_normal = (0, 0, 0, 0)
        self.ids.due_date_input.text_color = (0, 0, 0, 1)
        self.reset_priority_button()

    def open_date_picker(self):
        try:
            date_dialog = MDDatePicker(mode="picker", min_year=2023, max_year=2030)
            date_dialog.bind(on_save=self._on_date_selected)
            date_dialog.open()
        except Exception as e:
            # print(f"Date picker error: {e}")
            self.show_date_input_dialog()

    def _on_date_selected(self, instance, value, date_range):
        self._set_due_date(value)

    def show_date_input_dialog(self):
        self.date_field = MDTextField(
            hint_text="Enter date (DD-MM-YYYY)",
            helper_text="Example: 05-05-2025",
            helper_text_mode="on_focus"
        )

        self.date_dialog = MDDialog(
            title="Enter Due Date",
            type="custom",
            content_cls=self.date_field,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.date_dialog.dismiss()),
                MDFlatButton(text="OK", on_release=self.process_manual_date),
            ],
        )
        self.date_dialog.open()

    def process_manual_date(self, *args):
        try:
            date_obj = datetime.strptime(self.date_field.text, "%d-%m-%Y")
            self._set_due_date(date_obj)
            self.date_dialog.dismiss()
        except Exception as e:
            # print(f"Date parsing error: {e}")
            toast("Enter a valid date ")

    def _set_due_date(self, date_obj):
        self._due_date = date_obj.strftime("%Y-%m-%d")
        self.ids.due_date_input.text = date_obj.strftime("%d %b %Y")

    def setup_priority_menu(self, *args):
        menu_items = [
            {"text": "Urgent", "viewclass": "OneLineListItem", "height": dp(56),
            "on_release": lambda: self.set_priority("Urgent")},
            {"text": "High", "viewclass": "OneLineListItem", "height": dp(56),
            "on_release": lambda: self.set_priority("High")},
            {"text": "Medium", "viewclass": "OneLineListItem", "height": dp(56),
            "on_release": lambda: self.set_priority("Medium")},
            {"text": "Low", "viewclass": "OneLineListItem", "height": dp(56),
            "on_release": lambda: self.set_priority("Low")},
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.priority_input,
            items=menu_items,
            position="bottom",
            width_mult=4,
            max_height=dp(224),
            radius=[8, 8, 8, 8],
            elevation=2
        )

    def set_priority(self, priority):
        self.ids.priority_input.text = priority
        color_map = {
            "Urgent": [0.75, 0.13, 0.13, 1],   # dark red
            "High": [0.91, 0.3, 0.24, 1],      # red
            "Medium": [1, 0.55, 0, 1],         # orange
            "Low": [0.25, 0.64, 0.96, 1],      # blue
        }
        self.ids.priority_input.md_bg_color = color_map.get(priority, [0.5, 0.5, 0.5, 1])
        if self.menu:
            self.menu.dismiss()

    def show_priority_menu(self):
        if self.menu:
            self.menu.open()


    def save_task(self):
        if not self.controller:
            toast("connection is not set.")
            return


        title = self.ids.title_input.text.strip()
        description = self.ids.description_input.text.strip()
        priority = self.ids.priority_input.text

        if not title:
            toast("Title is required")
            return

        if not self._due_date:
            toast("Date is required")
            return

        if priority not in ("Urgent", "High", "Medium", "Low"):
            toast("Priority is required")
            return

        try:
            task = self.controller.create_task(
                title=title,
                description=description,
                due_date=self._due_date,
                priority=priority
            )
        except Exception as e:
            # print(f"create_task error: {e}")
            toast("Something went wrong. Try again.")
            return

        if task:
            toast("Task created successfully")
            App.get_running_app().sm.current = "home"
        else:
            toast("Failed to create task")

    def go_back(self):
        self.manager.current = 'home'




    def on_leave(self):
        self.reset_priority_button()

    def reset_priority_button(self):
        self.ids.priority_input.text = 'select priority'
        self.ids.priority_input.md_bg_color = (0.5, 0.5, 0.5, 1)
    

    


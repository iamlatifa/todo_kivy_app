from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivymd.uix.pickers import MDDatePicker
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from datetime import datetime
import os

# Load KV layout
KV_PATH = os.path.join(os.path.dirname(__file__), '..', 'kv', 'task_item_views.kv')


class TaskItemView(BoxLayout):
    task_id = NumericProperty(0)
    title = StringProperty("")
    description = StringProperty("")
    due_date = StringProperty("", allownone=True)
    priority = StringProperty("")
    completed = BooleanProperty(False)
    controller = ObjectProperty()
    background_color = ListProperty([1, 1, 1, 1])
    is_expanded = BooleanProperty(False)
    original_height = NumericProperty(100)
    expanded_height = NumericProperty(320)
    temp_due_date = StringProperty("", allownone=True)
    temp_title = StringProperty("")
    temp_description = StringProperty("")
    temp_priority = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._due_date = None
        Clock.schedule_once(self._after_init, 0.1)

    def _after_init(self, dt):
        if hasattr(self, 'ids') and 'title_field' in self.ids:
            self.ids.title_field.text = self.title
            self.ids.description_field.text = self.description
            self.temp_title = self.title
            self.temp_description = self.description
            self.temp_due_date = self.due_date
            self.temp_priority = self.priority

    def on_checkbox_active(self, checkbox, value):
        if not self.controller:
            toast("Controller not set.")
            return
        if value:
            self.controller.toggle_task_completion(self.task_id, True)
            self.show_custom_dialog()
            Clock.schedule_once(lambda dt: self.remove_task_from_ui(), 0.2)
        else:
            self.controller.toggle_task_completion(self.task_id, False)

    def confirm_and_delete_task(self):
        if not hasattr(self, 'delete_dialog') or not self.delete_dialog:
            self.delete_dialog = MDDialog(
                title="Confirm Deletion",
                text=f"Are you sure you want to delete the task '{self.title}'?",
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=lambda x: self.delete_dialog.dismiss()),
                    MDFlatButton(
                        text="DELETE",
                        text_color=get_color_from_hex("#F44336"),
                        on_release=lambda x: self.proceed_with_deletion(x)
                    ),
                ],
            )
        self.delete_dialog.open()

    def proceed_with_deletion(self, instance):
        self.delete_dialog.dismiss()
        self.delete_self()

    def delete_self(self):
        if self.parent:
            self.parent.remove_widget(self)
        if self.controller:
            self.controller.delete_task(self.task_id)

    def remove_task_from_ui(self):
        if self.parent:
            anim = Animation(opacity=0, duration=0.2)
            anim.bind(on_complete=lambda *a: self.parent.remove_widget(self) if self.parent else None)
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

    def open_edit_screen(self):
        if self.controller and self.task_id:
            self.controller.edit_task(self.task_id)

    def start_edit_mode(self):
        self.temp_title = self.title
        self.temp_description = self.description
        self.temp_due_date = self.due_date
        self.temp_priority = self.priority

        if self.due_date:
            try:
                date_obj = datetime.strptime(self.due_date, "%d %b %Y")
                self._due_date = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                try:
                    date_obj = datetime.strptime(self.due_date, "%Y-%m-%d")
                    self._due_date = self.due_date
                except ValueError:
                    self._due_date = None

        anim = Animation(height=self.expanded_height, duration=0.3)
        anim.bind(on_complete=lambda *x: setattr(self, 'is_expanded', True))
        anim.start(self)

    def collapse_edit_view(self):
        anim = Animation(height=self.original_height, duration=0.3)
        anim.bind(on_complete=lambda *x: setattr(self, 'is_expanded', False))
        anim.start(self)

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self._due_date = value.strftime("%Y-%m-%d")
        self.temp_due_date = value.strftime("%d %b %Y")

    def set_priority(self, priority):
        self.temp_priority = priority

    def save_task_changes(self):
        if not self.temp_title:
            toast("Title is required")
            return

        updated_data = {
            "title": self.temp_title,
            "description": self.temp_description,
            "due_date": self._due_date,
            "priority": self.temp_priority
        }

        success = self.controller.update_task(self.task_id, **updated_data)

        if success:
            self.title = self.temp_title
            self.description = self.temp_description
            self.due_date = self.temp_due_date
            self.priority = self.temp_priority
            toast("Task updated successfully")
        else:
            toast("Failed to update task")

        self.collapse_edit_view()

    def cancel_edit(self):
        self.collapse_edit_view()

    def on_priority(self, instance, value):
        color_map = {
            "Urgent": get_color_from_hex("#B71C1C"),
            "High": get_color_from_hex("#E53935"),
            "Medium": get_color_from_hex("#FB8C00"),
            "Low": get_color_from_hex("#42A5F5"),
        }

        modified_color_map = {}
        for color_key, color in color_map.items():
            rgba = list(color)
            if len(rgba) > 3:
                rgba[3] = 0.85
            modified_color_map[color_key] = rgba

        self.background_color = modified_color_map.get(value, [1, 1, 1, 1])

        if not self.is_expanded:
            self.temp_priority = value

    def get_priority_text_color(self):
        text_color_map = {
            "Urgent": get_color_from_hex("#FFFFFF"),
            "High": get_color_from_hex("#FFFFFF"),
            "Medium": get_color_from_hex("#263238"),
            "Low": get_color_from_hex("#0D47A1"),
        }
        return text_color_map.get(self.priority, get_color_from_hex("#212121"))

    def safe_parse_created_at(self, created_at_string):
        """Safely parse 'created_at' like 'Fri, 02 May 2025 17:26:59 GMT'."""
        try:
            clean = created_at_string.replace(" GMT", "")
            return datetime.strptime(clean, "%a, %d %b %Y %H:%M:%S")
        except Exception:
            print(f"[WARNING] [Date formatting failed] {created_at_string}")
            return None

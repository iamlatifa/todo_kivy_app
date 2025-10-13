from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProfileScreen(Screen):
    username = StringProperty("User")
    email = StringProperty("")
    join_date = StringProperty("")
    completed_tasks = StringProperty("0")
    pending_tasks = StringProperty("0")
    total_tasks = StringProperty("0")
    profile_image = StringProperty("assets/images/default_profile.png")
    task_completion_rate = StringProperty("0%")
    model = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('user_session.json')
        self.spinner = None

    def go_back(self):
        self.manager.current = 'home'

    def on_enter(self, *args):
        app = App.get_running_app()
        if app and app.current_user:
            self.load_user_stats()
            self.show_loading()
            try:
                user = app.current_user
                self.username = user.username
                self.email = user.email
                self.join_date = self._format_date(user.created_at)


                if 'completion_rate_label' in self.ids:
                    self.ids.completion_rate_label.text = f"Task Completion Rate: {self.task_completion_rate}"

                if 'completion_bar' in self.ids:
                    try:
                        rate = int(self.task_completion_rate.strip('%'))
                        self.ids.completion_bar.value = rate
                    except ValueError:
                        self.ids.completion_bar.value = 0

                
            except Exception as e:
                logger.error(f"Failed to load user data: {e}")
                # self.show_error_dialog("Could not load user profile.")
            finally:
                self.hide_loading()

    def _format_date(self, date_str):
        if not date_str:
            return "Not available"
        try:
            # Try parsing full date format like "Thu, 15 May 2025 15:59:47 GMT"
            date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
            return date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Date formatting failed: {e}")
            return date_str


    def load_user_stats(self):
        app = App.get_running_app()
        try:
            if not hasattr(app, 'task_controller'):
                raise AttributeError("App has no task_controller.")
            
            tasks = app.task_controller.get_all_tasks()
            print("screen, loading user stats...",tasks)

            total = len(tasks)
            completed = sum(1 for t in tasks if t.get("completed"))
            pending = total - completed
            completion_rate = f"{(completed / total) * 100:.0f}%" if total > 0 else "0%"

            self.total_tasks = str(total)
            self.completed_tasks = str(completed)
            self.pending_tasks = str(pending)
            self.task_completion_rate = completion_rate


            self.ids.total_tasks_label.text = self.total_tasks
            self.ids.completed_tasks_label.text = self.completed_tasks
            self.ids.pending_tasks_label.text = self.pending_tasks
            self.ids.completion_rate_label.text = f"Task Completion Rate: {self.task_completion_rate}"

            
        except Exception as e:
            logger.error(f"Failed to load task stats: {e}")
            self.total_tasks = self.completed_tasks = self.pending_tasks = "0"
            self.task_completion_rate = "0%"

    def show_loading(self):
        if not self.spinner:
            self.spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(46), dp(46)),
                pos_hint={'center_x': .5, 'center_y': .5}
            )
        if self.spinner.parent is None:
            self.add_widget(self.spinner)

    def hide_loading(self):
        if self.spinner and self.spinner.parent:
            self.remove_widget(self.spinner)

    def show_error_dialog(self, message):
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

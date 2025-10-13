from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.clock import Clock
from views.widgets.task_item import TaskItemView
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskController:
    def __init__(self, app, home_view, api_service):
        self.app = app
        self.home_view = home_view
        self.model = api_service  # ApiService instance
        self.home_view.controller = self
        self.current_filter = None
        self.completed_tasks_view = None  # Will be set later
        self.prevent_double_loading = False  # Flag to prevent double loading
        self.dialog = None  # Store reference to active dialog

        # Schedule cleanup every hour
        Clock.schedule_interval(self.check_and_prompt_task_cleanup, 3600)

    def set_completed_tasks_view(self, view):
        self.completed_tasks_view = view

    def create_task(self, title, description, due_date, priority):
        if not self.app.current_user:
            logger.error("User not logged in.")
            return False

        data = {
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'user_id': self.app.current_user.id,
            'completed': False
        }

        result = self.model.add_task(data)
        if "error" in result:
            logger.error(f"Failed to add task: {result['error']}")
            return False
        else:
            self.prevent_double_loading = True
            return True

    def save_task(self):
        title = self.screen.ids.title_input.text
        description = self.screen.ids.description_input.text
        due_date = self.screen.ids.due_date_input.text
        priority_text = self.screen.ids.priority_input.text

        if not title.strip():
            logger.warning("Title is required.")
            return False

        priority = priority_text
        return self.create_task(title, description, due_date, priority)

    def load_uncompleted_tasks(self):
        if not self.app.current_user:
            return

        user_id = self.app.current_user.id

        def load_in_thread():
            tasks = self.model.get_tasks(user_id=user_id, completed=False)
            Clock.schedule_once(lambda dt: self._display_tasks(tasks, self.home_view))

        import threading
        threading.Thread(target=load_in_thread).start()

    def load_completed_tasks(self):
        if not self.app.current_user or not self.completed_tasks_view:
            return

        user_id = self.app.current_user.id

        def load_in_thread():
            tasks = self.model.get_tasks(user_id=user_id, completed=True)
            Clock.schedule_once(lambda dt: self._display_tasks(tasks, self.completed_tasks_view))

        import threading
        threading.Thread(target=load_in_thread).start()

    def load_tasks(self, completed=None, target_view=None):
        if not self.app.current_user:
            return

        user_id = self.app.current_user.id

        def load_in_thread():
            tasks = self.model.get_tasks(user_id=user_id, completed=completed)
            Clock.schedule_once(lambda dt: self._display_tasks(tasks, target_view or self.home_view))

        import threading
        threading.Thread(target=load_in_thread).start()

    def reload_all_task_views(self):
        self.load_uncompleted_tasks()
        if self.completed_tasks_view:
            self.load_completed_tasks()

    def get_all_tasks(self):
        if not self.app.current_user:
            return []

        user_id = self.app.current_user.id
        tasks = self.model.get_tasks(user_id=user_id)
        logger.debug(f"All tasks: {len(tasks)} items")
        return tasks

    def _display_tasks(self, tasks, view):
        if not view:
            return

        if hasattr(view, 'on_tasks_data_loaded'):
            view.on_tasks_data_loaded(tasks)
            return

        view.clear_tasks()
        if not tasks:
            view.show_empty_message()
            return

        for task in tasks:
            task_widget = TaskItemView(
                task_id=task['id'],
                title=task['title'],
                description=task.get('description', ''),
                priority=task.get('priority', ''),
                completed=bool(task.get('completed', 0)),
                due_date=task.get('due_date', ''),
                controller=self
            )
            view.add_task_widget(task_widget)

    def toggle_task_completion(self, task_id, completed):
        result = self.model.update_task_completion(task_id, completed)
        if result:
            self.reload_all_task_views()
            return True
        else:
            logger.error(f"Error updating task completion for task ID: {task_id}")
            return False

    def delete_task(self, task_id):
        if self.model.delete_task(task_id):
            self.reload_all_task_views()
            return True
        else:
            logger.error(f"Error deleting task ID: {task_id}")
            return False

    def update_task(self, task_id, title, description, due_date, priority):
        data = {
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority
        }
        result = self.model.update_task(task_id, data)
        if result:
            return True
        else:
            logger.error(f"Failed to update task ID: {task_id}")
            return False

    def filter_tasks(self, filter_type):
        self.current_filter = None if filter_type == "all" else filter_type

        if filter_type == "completed":
            self.load_completed_tasks()
        else:
            self.load_uncompleted_tasks()

    def confirm_and_delete_task(self, task_id, task_title):
        if self.dialog:
            self.dialog.dismiss()

        def delete_callback(*args):
            self.delete_task(task_id)
            self.dialog.dismiss()
            self.dialog = None

        self.dialog = MDDialog(
            title="Delete Task",
            text=f"Are you sure you want to delete the task '{task_title}'?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="DELETE", text_color=(1, 0, 0, 1), on_release=delete_callback),
            ],
        )
        self.dialog.open()

    def edit_task(self, task_id):
        tasks = self.get_tasks_sync()
        task_data = next((t for t in tasks if t["id"] == task_id), None)
        if not task_data:
            logger.error(f"Task with ID {task_id} not found")
            return

        screen = self.app.root.get_screen("edit_task")
        screen.controller = self
        screen.task_data = task_data
        self.app.root.current = "edit_task"

    def get_tasks_sync(self, completed=None):
        if not self.app.current_user:
            return []

        user_id = self.app.current_user.id
        return self.model.get_tasks(user_id=user_id, completed=completed)

    def invalidate_cache(self):
        self.prevent_double_loading = False

    # ⏰ Scheduled method to check for old completed tasks
    def check_and_prompt_task_cleanup(self, dt):
        if not self.app.current_user:
            return

        tasks = self.get_tasks_sync(completed=True)
        old_tasks = []

        for task in tasks:
            completed_at = task.get('completed_at')
            if not completed_at:
                continue
            try:
                completed_time = datetime.fromisoformat(completed_at)
                if datetime.now() - completed_time > timedelta(hours=24):
                    old_tasks.append(task)
            except Exception as e:
                logger.error(f"Invalid date format for task {task['id']}: {e}")

        for task in old_tasks:
            self.prompt_task_deletion(task)

    # 📢 Show a dialog asking if the user wants to delete an old completed task
    def prompt_task_deletion(self, task):
        task_id = task['id']
        task_title = task['title']

        if self.dialog:
            self.dialog.dismiss()

        def delete_task_now(*args):
            self.delete_task(task_id)
            self.dialog.dismiss()
            self.dialog = None

        def keep_task(*args):
            self.dialog.dismiss()
            self.dialog = None

        self.dialog = MDDialog(
            title="Delete Old Task",
            text=f"The task '{task_title}' was completed over 24 hours ago.\nDelete it?",
            buttons=[
                MDFlatButton(text="KEEP", on_release=keep_task),
                MDRaisedButton(text="DELETE", on_release=delete_task_now),
            ],
        )
        self.dialog.open()

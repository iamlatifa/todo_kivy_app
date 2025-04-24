from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from views.widgets.task_item import TaskItemView

class TaskController:
    def __init__(self, app, home_view, api_service):
        self.app = app
        self.home_view = home_view
        self.model = api_service  # ApiService instance
        self.home_view.controller = self
        self.current_filter = None

    def add_task(self, title, description, due_date, priority):
        """Add a new task using ApiService"""
        if not self.app.current_user:
            print("User not logged in.")
            return

        data = {
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'user_id': self.app.current_user.id,
            'completed': False
        }

        result = self.model.add_task(data)
        if result:
            self.load_tasks()
        else:
            print("Failed to add task.")

    def save_task(self):
        """Collect task data from UI and send it to API"""
        title = self.screen.ids.title_input.text
        description = self.screen.ids.description_input.text
        due_date = self.screen.ids.due_date_input.text
        priority_text = self.screen.ids.priority_input.text

        if not title.strip():
            print("Title is required.")
            return

        priority_map = {
            "Low": 0, "Medium": 1, "High": 2, "Urgent": 3
        }

        priority = priority_map.get(priority_text, 0)

        self.add_task(title, description, due_date, priority)

    def load_tasks(self):
        """Load tasks for the current user via ApiService"""
        if not self.app.current_user:
            return

        user_id = self.app.current_user.id
        completed = (
            True if self.current_filter == "completed" else
            False if self.current_filter == "active" else
            None
        )

        tasks = self.model.get_tasks(user_id=user_id, completed=completed)

        self.home_view.clear_tasks()

        if not tasks:
            self.home_view.show_empty_message()
            return

        for task in tasks:
            task_widget = TaskItemView(
                task_id=task['id'],
                title=task['title'],
                description=task.get('description', ''),
                priority=task.get('priority', 0),
                completed=bool(task.get('completed', 0)),
                due_date=task.get('due_date', ''),
                controller=self
            )
            self.home_view.add_task_widget(task_widget)

    def toggle_task_completion(self, task_id, completed):
        """Toggle completion status via ApiService"""
        result = self.model.update_task_completion(task_id, completed)
        if result:
            self.load_tasks()
        else:
            print("Error updating task completion.")

    def delete_task(self, task_id):
        """Delete a task via ApiService"""
        if self.model.delete_task(task_id):
            self.load_tasks()
        else:
            print("Error deleting task.")

    def update_task(self, task_id, title, description, due_date, priority):
        """Update a task using ApiService"""
        data = {
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority
        }
        result = self.model.update_task(task_id, data)
        if result:
            self.load_tasks()
        else:
            print("Failed to update task.")

    def filter_tasks(self, filter_type):
        """Filter tasks: all, active, or completed"""
        self.current_filter = None if filter_type == "all" else filter_type
        self.load_tasks()

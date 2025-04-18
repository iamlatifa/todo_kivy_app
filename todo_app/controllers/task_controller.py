from services.task_service import TaskService
from services.database import Database
from views.widgets.task_item import TaskItemView
from kivy.app import App

class TaskController:
    """Controller for handling task-related operations"""

    def __init__(self, app, home_view, model=None, current_filter='active'):
        self.app = app
        self.home_view = home_view
        self.model = model if model else Database()
        self.home_view.controller = self
        self.task_service = TaskService()
        self.current_filter = current_filter
        self.task_widgets = []  # Stores currently loaded task widgets

    def load_tasks(self):
        """Load tasks from database and update view"""
        if not self.app.current_user:
            return

        self.home_view.clear_tasks()
        self.task_widgets = []

        user_id = self.app.current_user.id
        tasks = self.task_service.get_tasks_by_user_and_filter(self.model, user_id, self.current_filter)

        if not tasks:
            self.home_view.show_empty_message()
        else:
            for task in tasks:
                task_widget = TaskItemView(
                    task_id=task.id,
                    title=task.title,
                    description=task.description,
                    due_date=task.due_date,
                    priority=str(task.priority),
                    completed=task.completed,
                    controller=self
                )
                self.home_view.add_task_widget(task_widget)
                self.task_widgets.append(task_widget)

    def add_new_task(self):
        self.app.screen_manager.current = "add_task"

    def toggle_task_completion(self, task_id, value):
        self.model.update_task_completion(task_id, value)
        print(f"Task {task_id} marked as {'completed' if value else 'incomplete'}")

    def on_task_reordered(self):
        task_order = [child.task_id for child in self.home_view.ids.tasks_container.children[::-1]]
        self.model.save_task_order(task_order)

    def update_task(self, task_id, **task_data):
        """Update a task in the database and reflect changes in the UI"""
        # Update task in database
        self.model.update_task(
            task_id=task_id,
            title=task_data.get("title"),
            description=task_data.get("description"),
            due_date=task_data.get("due_date"),
            priority=task_data.get("priority", "Low")
        )

        # Find and update the widget in-place
        for widget in self.task_widgets:
            if widget.task_id == task_id:
                widget.title = task_data.get("title", "")
                widget.description = task_data.get("description", "")
                widget.due_date = task_data.get("due_date", "")
                widget.priority = task_data.get("priority", "Low")

                # Update the UI labels if they exist
                if 'title_label' in widget.ids:
                    widget.ids.title_label.text = widget.title
                if 'description_label' in widget.ids:
                    widget.ids.description_label.text = widget.description
                if 'due_date_label' in widget.ids:
                    widget.ids.due_date_label.text = f"Due: {widget.due_date}"
                if 'priority_label' in widget.ids:
                    widget.ids.priority_label.text = widget.priority

                print(f"Updated task {task_id} in UI")
                break
        else:
            print(f"Warning: Task widget for ID {task_id} not found in task_widgets.")

        print(f"Task {task_id} updated")


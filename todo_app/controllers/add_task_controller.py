from models.task import Task
from datetime import datetime

class AddTaskController:
    def __init__(self, app, screen):
        self.app = app
        self.screen = screen
        self.screen.controller = self
    
    def save_task(self):
        title = self.screen.ids.title_input.text
        description = self.screen.ids.description_input.text
        priority_text = self.screen.ids.priority_input.text
        due_date = self.screen.ids.due_date_input.text
        # try:
        #     due_date = datetime.strptime(due_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        # except ValueError:
        #     print("Invalid date format. Use YYYY-MM-DD.")
        #     return

        if not title.strip():
            print("Title required")
            return

        priority_map = {
            "Low": 0, "Medium": 1, "High": 2, "Urgent": 3
        }

        task = Task(
            user_id=self.app.current_user.id,
            title=title,
            description=description,
            due_date=due_date,
            priority= priority_text,
            completed=False
        )

        self.app.db.add_task(task.to_dict())
        self.app.root.get_screen("home").controller.load_tasks()
        self.app.root.current = "home"

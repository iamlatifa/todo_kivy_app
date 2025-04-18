from datetime import datetime

class Task:
    def __init__(self, id=None, user_id=None, title="", description="", 
                 due_date=None, priority=0, completed=False):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = completed

    @classmethod
    def from_dict(cls, data):
        """Create a Task object from a dictionary."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            priority=data.get('priority', 0),
            completed=bool(data.get('completed', False))
        )

    def to_dict(self):
        """Convert the Task object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'priority': self.priority,
            'completed': self.completed
        }

    @property
    def priority_text(self):
        """Return a text label for the priority level."""
        return {
            0: "Low",
            1: "Medium",
            2: "High",
            3: "Urgent"
        }.get(self.priority, "Low")

    @property
    def is_overdue(self):
        """Return True if the task is overdue and not completed."""
        if not self.due_date or self.completed:
            return False
        try:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
            return due_date.date() < datetime.now().date()
        except (ValueError, TypeError):
            return False

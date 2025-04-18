# services/task_service.py
from models.task import Task

class TaskService:
    @staticmethod
    def get_tasks_by_user_and_filter(db, user_id, filter_type):
        """Fetch tasks based on user and filter"""
        completed = None
        if filter_type == 'active':
            completed = False
        elif filter_type == 'completed':
            completed = True
        
        task_dicts = db.get_tasks_by_user(user_id, completed)
        return [Task.from_dict(task_dict) for task_dict in task_dicts]

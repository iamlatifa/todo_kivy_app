# services/task_service.py
from models.task import Task
import logging

logger = logging.getLogger(__name__)

class TaskService:
    @staticmethod
    def get_tasks_by_user_and_filter(api_service, user_id, filter_type):
        try:
            completed = None
            if filter_type == 'active':
                completed = 0
            elif filter_type == 'completed':
                completed = 1

            task_dicts = api_service.get_tasks(user_id, completed)
            return [Task.from_dict(task_dict) for task_dict in task_dicts]
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []

    
    @staticmethod
    def add_task(api_service, task_data):
        if 'user_id' not in task_data or 'title' not in task_data:
            logger.warning("Missing required fields in task_data")
            return None
        try:
            result = api_service.add_task(task_data)
            return Task.from_dict(result) if result else None
        except Exception as e:
            logger.error(f"Add task failed: {e}")
            return None

    
    @staticmethod
    def update_task(api_service, task_id, task_data):
        """Update a task using the API service"""
        result = api_service.update_task(task_id, task_data)
        if result:
            return Task.from_dict(result)
        return None
    
    @staticmethod
    def delete_task(api_service, task_id):
        """Delete a task using the API service"""
        return api_service.delete_task(task_id)
    
    @staticmethod
    def toggle_task_completion(api_service, task_id, completed):
        """Toggle task completion status using the API service"""
        result = api_service.update_task_completion(task_id, completed)
        if result:
            return Task.from_dict(result)
        return None
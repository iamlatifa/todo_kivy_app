from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from models.task import Task
import logging

logger = logging.getLogger(__name__)

class TaskService:
    PRIORITY_MAP = {
        'Low': 0,
        'Medium': 1,
        'High': 2
    }

    REVERSE_PRIORITY_MAP = {v: k for k, v in PRIORITY_MAP.items()}

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.tasks_file = self.data_dir / "tasks.json"
        self.statistics_file = self.data_dir / "statistics.json"
        
        self._ensure_files_exist()
        self._load_data()

    def _ensure_files_exist(self):
        if not self.tasks_file.exists():
            self._save_tasks([])
        if not self.statistics_file.exists():
            self._save_statistics({})

    def _load_data(self):
        with open(self.tasks_file, 'r') as f:
            self.tasks = json.load(f)
        with open(self.statistics_file, 'r') as f:
            self.statistics = json.load(f)

    def _save_tasks(self, tasks: List[Dict]):
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        self.tasks = tasks
        self._update_statistics()

    

    @staticmethod
    def add_task(api_service, task_data):
        if 'user_id' not in task_data or 'title' not in task_data:
            # logger.warning("Missing required fields in task_data")
            return None
        try:
            result = api_service.add_task(task_data)
            return Task.from_dict(result) if result else None
        except Exception as e:
            # logger.error(f"Add task failed: {e}")
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
        
        

    def get_task(self, task_id: int) -> Optional[dict]:
        return next((task for task in self.tasks if task['id'] == task_id), None)

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
    def toggle_task_completion(api_service, task_id, completed):
        """Toggle task completion status using the API service"""
        result = api_service.update_task_completion(task_id, completed)
        if result:
            return Task.from_dict(result)
        return None

    
#############################################################################################################""""

    def get_statistics(self) -> dict:
        return self.statistics

    def export_tasks(self, format: str = 'json') -> Union[str, List[Dict]]:
        if format == 'json':
            return json.dumps(self.tasks, indent=2)
        elif format == 'csv':
            output = []
            for task in self.tasks:
                output.append({
                    'id': task['id'],
                    'title': task['title'],
                    'description': task['description'],
                    'due_date': task.get('due_date', ''),
                    'priority': task['priority'],
                    'completed': task['completed'],
                    'created_at': task['created_at']
                })
            return output
        raise ValueError("Format must be 'json' or 'csv'")

    def import_tasks(self, data: Union[str, List[Dict]], format: str = 'json') -> bool:
        try:
            if format == 'json':
                tasks = json.loads(data)
            elif format == 'csv':
                tasks = data
            else:
                raise ValueError("Format must be 'json' or 'csv'")
            
            for task in tasks:
                if isinstance(task.get('priority'), str):
                    task['priority'] = self.PRIORITY_MAP.get(task['priority'].capitalize(), 1)

            self.tasks.extend(tasks)
            self._save_tasks(self.tasks)
            return True
        except Exception as e:
            print(f"Error importing tasks: {str(e)}")
            return False





    def _save_statistics(self, statistics: Dict):
        with open(self.statistics_file, 'w') as f:
            json.dump(statistics, f, indent=2)
        self.statistics = statistics

    def _update_statistics(self):
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task.get('completed', False))
        
        stats = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
        self._save_statistics(stats)
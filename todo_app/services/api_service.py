import requests

class ApiService:
    def __init__(self, base_url="http://50.6.153.0:5000/api"):  
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, username, password):
        """Login and get user details"""
        url = f"{self.base_url}/login"
        data = {
            "username": username,
            "password": password
        }
        try:
            response = self.session.post(url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}

    def register_user(self, username, email, password, confirm_password):
        """Register a new user"""
        url = f"{self.base_url}/signup"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }
        try:
            response = self.session.post(url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}

    def get_user(self, user_id):
        """Get user by ID"""
        url = f"{self.base_url}/users/{user_id}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return {"error": "User not found"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}

    def get_tasks(self, user_id, completed=None):
        """Get tasks for a user"""
        url = f"{self.base_url}/tasks"
        params = {"user_id": user_id}
        if completed is not None:
            params["completed"] = completed
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            print(f"API Error: {response.status_code}, {response.text}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return []

    def add_task(self, task_data):
        """Add a new task"""
        url = f"{self.base_url}/tasks"
        try:
            response = self.session.post(url, json=task_data)
            if response.status_code == 201:
                return response.json()
            return {"error": "Failed to add task"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}

    def get_task(self, task_id):
        """Get a specific task"""
        url = f"{self.base_url}/tasks/{task_id}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return {"error": "Task not found"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}

    def update_task(self, task_id, task_data):
        """Update a task"""
        url = f"{self.base_url}/tasks/{task_id}"
        try:
            response = self.session.put(url, json=task_data)
            if response.status_code == 200:
                return response.json()
            return {"error": "Failed to update task"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}

    def delete_task(self, task_id):
        """Delete a task"""
        url = f"{self.base_url}/tasks/{task_id}"
        try:
            response = self.session.delete(url)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Network error while deleting task: {e}")
            return False

    def update_task_completion(self, task_id, completed):
        """Update task completion status"""
        url = f"{self.base_url}/tasks/completion/{task_id}"
        data = {"completed": completed}
        try:
            response = self.session.patch(url, json=data)
            if response.status_code == 200:
                return response.json()
            return {"error": "Failed to update completion"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}
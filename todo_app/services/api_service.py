import requests
import os
import json
import logging
from config import Config
from utils.exceptions import AuthenticationError, NetworkError, APIError
# Setup logger

logger = logging.getLogger(__name__)

class ApiService:
    def __init__(self, config=Config.API_CONFIG, timeout=30):  
        self.base_url = config['base_url']
        self.session = requests.Session()
        self.users_file = "users.json"
        self.tasks_file = "tasks.json"
        self.timeout = timeout
        self._ensure_data_files()
        # Log initialization
        logger.info(f"ApiService initialized with base URL: {self.base_url}")

    def _ensure_data_files(self):
        """Ensure necessary data files exist for offline fallback"""
        try:
            # Implement the missing method
            for file_path in [self.users_file, self.tasks_file]:
                file_path = self._get_absolute_path(file_path)
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        json.dump([], f)
                    logger.info(f"Created file: {file_path}")
        except Exception as e:
            logger.error(f"Error ensuring data files: {str(e)}")

    def _get_absolute_path(self, file_name):
        """Get the absolute path for a file considering the platform"""
        try:
            import sys
            if hasattr(sys, 'getandroidapilevel'):
                from android.storage import app_storage_path
                app_dir = app_storage_path()
                abs_path = os.path.join(app_dir, file_name)
                logger.debug(f"Using Android app path for {file_name}: {abs_path}")
                return abs_path
        except Exception as e:
            logger.warning(f"Android storage path not available: {e}")

        # Default to a local folder for desktop or dev
        abs_path = os.path.join(os.getcwd(), file_name)
        logger.debug(f"Using desktop path for {file_name}: {abs_path}")
        return abs_path


    def _handle_connection_error(self, e, fallback=None):
        """Handle connection errors with proper logging"""
        logger.error(f"API connection error: {str(e)}")
        if fallback is not None:
            return fallback
        return {"error": f"Network error: {str(e)}"}

    def authenticate_user(self, username, password):
        """Authenticate user with the API"""
        try:
            result = self.login(username, password)
            if "error" not in result:
                logger.info(f"User {username} authenticated successfully")
                return result
            logger.warning(f"Authentication failed for user {username}: {result.get('error')}")
            return None
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    def check_user_exists(self, username, email):
        """Check if username or email already exists"""
        # This would typically call an API endpoint
        # For now, we'll return False to allow registration attempts
        return False

    def create_user(self, username, email, password):
        """Create a new user through the API"""
        try:
            result = self.register_user(username, email, password, password)
            if "error" not in result:
                logger.info(f"Created new user: {username}")
                return result
            logger.warning(f"Failed to create user {username}: {result.get('error')}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    def login(self, username, password):
        """Login and get user details"""
        try:
            url = f"{self.base_url}/api/login"
            payload = {"username": username, "password": password}
            logger.debug(f"Sending POST request to {url} with data {payload}")

            response = requests.post(url, json=payload, timeout=self.timeout)
            logger.debug(f"Received response: {response.status_code} - {response.text}")

            if response.status_code == 401:
                raise AuthenticationError("Invalid username or password")

            if not response.ok:
                raise APIError(f"Unexpected error: {response.status_code} - {response.text}")

            return response.json()

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

    def register_user(self, username, email, password, confirm_password):
        """Register a new user"""
        url = f"{self.base_url}/api/signup"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }
        try:
            logger.info(f"Attempting to register user: {username}")
            response = self.session.post(url, json=data, timeout=10)
            
            if response.status_code == 201:
                logger.info("Registration successful")
                return response.json()
                
            logger.warning(f"Registration failed with status code: {response.status_code}")
            return {"error": f"Registration failed: {response.text}"}
        except requests.exceptions.RequestException as e:
            return self._handle_connection_error(e)

    def get_user(self, user_id):
        """Get user by ID"""
        url = f"{self.base_url}/api/users/{user_id}"
        try:
            logger.info(f"Getting user with ID: {user_id}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
                
            logger.warning(f"Get user failed with status code: {response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    def get_tasks(self, user_id, completed=None):
        """Get tasks for a user"""
        url = f"{self.base_url}/api/tasks/{user_id}"
        params = {"user_id": user_id}
        if completed is not None:
            params["completed"] = completed
        try:
            logger.info(f"Getting tasks for user ID: {user_id}, completed={completed}")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
                
            logger.warning(f"Get tasks failed: {response.status_code}, {response.text}")
            return []
        except requests.exceptions.RequestException as e:
            return self._handle_connection_error(e, [])

    def add_task(self, task_data):
        """Add a new task"""
        url = f"{self.base_url}/api/tasks"
        try:
            logger.info(f"Adding task: {task_data.get('title', 'Unknown')}")
            response = self.session.post(url, json=task_data, timeout=10)
            
            if response.status_code == 201:
                logger.info("Task added successfully")
                return response.json()
                
            logger.warning(f"Add task failed: {response.status_code}, {response.text}")
            return {"error": "Failed to add task"}
        except requests.exceptions.RequestException as e:
            return self._handle_connection_error(e)

    def update_task(self, task_id, task_data):
        """Update a task"""
        url = f"{self.base_url}/api/tasks/{task_id}"
        try:
            logger.info(f"Updating task ID: {task_id}")
            response = self.session.put(url, json=task_data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Task updated successfully")
                return response.json()
                
            logger.warning(f"Update task failed: {response.status_code}, {response.text}")
            return {"error": "Failed to update task"}
        except requests.exceptions.RequestException as e:
            return self._handle_connection_error(e)

    def delete_task(self, task_id):
        """Delete a task"""
        url = f"{self.base_url}/api/tasks/{task_id}"
        try:
            logger.info(f"Deleting task ID: {task_id}")
            response = self.session.delete(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Task deleted successfully")
                return True
                
            logger.warning(f"Delete task failed: {response.status_code}, {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while deleting task: {str(e)}")
            return False

    def update_task_completion(self, task_id, completed):
        """Update task completion status"""
        url = f"{self.base_url}/api/tasks/completion/{task_id}"
        data = {"completed": completed}
        try:
            logger.info(f"Updating task completion for ID: {task_id} to {completed}")
            response = self.session.patch(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Task completion updated successfully")
                return response.json()
                
            logger.warning(f"Update completion failed: {response.status_code}, {response.text}")
            return {"error": "Failed to update completion"}
        except requests.exceptions.RequestException as e:
            return self._handle_connection_error(e)
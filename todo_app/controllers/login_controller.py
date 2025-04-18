import json
import re

SESSION_FILE = "user_session.json"

class LoginController:
    """Controller for handling login logic"""
    
    def __init__(self, app, view):
        self.app = app
        self.view = view
        self.view.controller = self
    
    def login(self, username, password):
        """Process login attempt"""
        if not username or not password:
            self.view.set_error("Username and password are required")
            return
        
        # Check credentials against database
        user = self.app.db.get_user_by_credentials(username, password)
        
        if user:
            self.view.set_error("")
            self.save_session(user[0])
            self.app.login_user(user)
        else:
            self.view.set_error("Invalid username or password")
    
    def save_session(self, user_id):
        with open(SESSION_FILE, "w") as f:
            json.dump({"user_id": user_id}, f)


    def navigate_to_signup(self):
        """Navigate to signup screen"""
        self.app.navigate_to('signup')
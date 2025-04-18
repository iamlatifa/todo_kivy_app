import re

class SignupController:
    """Controller for handling signup logic"""
    
    def __init__(self, app, view):
        self.app = app
        self.view = view
        self.db = app.db
        self.view.controller = self
    
    def register(self, username, email, password, confirm_password):
        """Process signup attempt"""
        if not username or not password or not confirm_password:
            self.view.set_error("All feilds are required")
            return
        
        # Check credentials against database        
        if password != confirm_password:
            self.view.set_error("Passwords do not match")
            return

        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            self.view.set_error("Username already exists.")
            return


        user_data={
           "username": username,
           "email": email,
           "password": password

       }

        self.app.db.create_user(username, password)
        self.app.navigate_to("login")

    def navigate_to_login(self):
        self.app.navigate_to('login')
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
import re
from kivy.app import App
import logging

# Setup logger
logger = logging.getLogger(__name__)

class SignupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        logger.info("SignupScreen initialized")
        
    def on_enter(self):
        """Reset input fields when screen is entered"""
        logger.debug("Resetting signup form fields")
        self.ids.username.text = ""
        self.ids.email.text = ""
        self.ids.password.text = ""
        self.ids.confirm_password.text = ""
        
    def validate_input(self):
        """Validate user input"""
        username = self.ids.username.text.strip()
        email = self.ids.email.text.strip()
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text
        
        # Reset error states
        self.ids.username.error = False
        self.ids.email.error = False
        self.ids.password.error = False
        self.ids.confirm_password.error = False
        
        # Validate username
        if not username:
            self.ids.username.error = True
            self.ids.username.helper_text = "Username is required"
            logger.warning("Signup validation failed: username missing")
            return False
            
        # Validate email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.ids.email.error = True
            self.ids.email.helper_text = "Invalid email format"
            logger.warning("Signup validation failed: invalid email format")
            return False
            
        # Validate password
        if len(password) < 8:
            self.ids.password.error = True
            self.ids.password.helper_text = "Password must be at least 8 characters"
            logger.warning("Signup validation failed: password too short")
            return False
            
        # Validate password confirmation
        if password != confirm_password:
            self.ids.confirm_password.error = True
            self.ids.confirm_password.helper_text = "Passwords do not match"
            logger.warning("Signup validation failed: passwords don't match")
            return False
            
        logger.info("Signup validation successful")
        return True
    
    # Add this method that's expected by the controller
    def set_error(self, message):
        """Update error message (called by controller)"""
        logger.warning(f"Signup error: {message}")
        self.show_error_dialog(message)
        
    def signup(self):
        """Handle signup button press"""
        logger.info("Signup button pressed")
        if not self.validate_input():
            return
            
        # Get the app instance
        app = App.get_running_app()
        
        try:
            # Extract form values
            username = self.ids.username.text.strip()
            email = self.ids.email.text.strip()
            password = self.ids.password.text
            confirm_password = self.ids.confirm_password.text
            
            logger.info(f"Attempting to register user: {username}")
            
            # Attempt to sign up the user
            result = app.signup_controller.signup(
                username=username,
                email=email,
                password=password,
                confirm_password=confirm_password
            )
            
            if result:
                logger.info("Signup successful, redirecting to login")
                # Navigate to login screen on success
                self.go_to_login()
            else:
                logger.warning("Signup failed")
                # The controller should have called set_error already
        except Exception as e:
            error_msg = f"Unexpected error during signup: {str(e)}"
            logger.error(error_msg)
            self.show_error_dialog(error_msg)
            
    def show_error_dialog(self, message):
        """Show error dialog with the given message"""
        logger.debug(f"Showing error dialog: {message}")
        if not self.dialog:
            self.dialog = MDDialog(
                title="Error",
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog.text = message
            
        self.dialog.open()
        
    def go_to_login(self):
        """Navigate to login screen"""
        logger.info("Navigating to login screen")
        self.manager.current = 'login'
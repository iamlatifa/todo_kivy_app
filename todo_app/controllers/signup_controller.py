import logging

# Setup logger
logger = logging.getLogger(__name__)

class SignupController:
    def __init__(self, app, view, api):
        self.app = app
        self.view = view
        self.api = api
        # Connect the view to this controller
        # self.view.controller = self  # This would be set in main.py
        logger.info("SignupController initialized")
        
    def signup(self, username, email, password, confirm_password):
        """Register a new user"""
        logger.info(f"SignupController: Processing signup for {username}")
        try:
            # Validate inputs (additional validation beyond view validation)
            if not all([username, email, password, confirm_password]):
                error_msg = "All fields are required"
                logger.warning(f"Signup validation failed: {error_msg}")
                self.view.set_error(error_msg)
                return False
                
            if password != confirm_password:
                error_msg = "Passwords do not match"
                logger.warning(f"Signup validation failed: {error_msg}")
                self.view.set_error(error_msg)
                return False
            
            # Attempt registration with API
            logger.info(f"Sending registration request for {username}")
            result = self.api.register_user(username, email, password, confirm_password)
            
            # Check for API errors
            if "error" in result:
                error_msg = result.get("error", "Registration failed")
                logger.warning(f"API registration error: {error_msg}")
                self.view.set_error(error_msg)
                return False
                
            # Success!
            logger.info(f"User {username} successfully registered")
            return True
                
        except Exception as e:
            error_msg = f"Registration error: {str(e)}"
            logger.error(error_msg)
            self.view.set_error(error_msg)
            return False
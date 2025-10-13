import logging
from utils.exceptions import AuthenticationError, NetworkError, APIError

# Setup logger
logger = logging.getLogger(__name__)

class LoginController:
    def __init__(self, app, view, api):
        self.app = app
        self.view = view
        self.api = api
        self.view.controller = self
        logger.info("LoginController initialized")
        
    def is_logged_in(self):
        """Check if user is authenticated"""
        return self.app.is_authenticated
        
    def login(self, username, password):
        logger.info(f"LoginController: Processing login for {username}")
        if not username or not password:
            self.view.set_error("Please fill in all fields")
            return False

        try:
            result = self.api.login(username, password)
            self.app.login_user(result)
            return True

        except AuthenticationError as e:
            logger.warning(f"Auth failed: {e}")
            self.view.set_error("Invalid username or password")
        except NetworkError as e:
            logger.warning(f"Network error: {e}")
            self.view.set_error("Could not reach server. Check your connection.")
        except APIError as e:
            logger.error(f"API error: {e}")
            self.view.set_error("Something went wrong on the server.")
        except Exception as e:
            logger.exception("Unexpected error in login")
            self.view.set_error("Unexpected error occurred. Try again.")

        return False
            
    def navigate_to_signup(self):
        """Navigate to the signup screen"""
        logger.info("Navigating to signup screen")
        self.app.navigate_to('signup')
        
    def logout(self):
        """Log out the current user"""
        logger.info("Logging out user")
        self.app.logout_user()
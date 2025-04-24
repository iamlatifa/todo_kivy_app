class SignupController:
    """Controller for handling signup logic."""

    def __init__(self, app, view):
        self.app = app
        self.view = view
        self.api = app.api  # Uses ApiService instance
        self.view.controller = self

    def register(self, username, email, password, confirm_password):
        """Validate and register a new user via API."""
        error = self._validate_input(username, email, password, confirm_password)
        if error:
            self.view.set_error(error)
            return

        response = self.api.register_user(username, email, password, confirm_password)

        if response.get("error"):
            self.view.set_error(response["error"])
        else:
            self.app.navigate_to("login")

    def _validate_input(self, username, email, password, confirm_password):
        """Return error message if input is invalid, else None."""
        if not all([username, email, password, confirm_password]):
            return "All fields are required"

        if password != confirm_password:
            return "Passwords do not match"

        return None

    def navigate_to_login(self):
        """Navigate to login screen."""
        self.app.navigate_to("login")

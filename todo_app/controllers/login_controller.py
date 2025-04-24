class LoginController:
    """Controller for handling login logic."""

    def __init__(self, app, view):
        self.app = app
        self.view = view
        self.api = app.api  # Instance of ApiService
        self.view.controller = self

    def login(self, username, password):
        """Attempt login through ApiService"""
        if not username.strip() or not password.strip():
            self.view.set_error("Please fill in all fields.")
            return

        response = self.api.login(username, password)

        if not response:
            self.view.set_error("No response from server.")
            return

        if "error" in response:
            self.view.set_error(response["error"])
            return

        # Login successful
        self.view.clear_fields()
        self.app.login_user(response)

    def navigate_to_signup(self):
        """Navigate to the signup screen"""
        self.app.navigate_to('signup')

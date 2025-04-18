from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App


class SignupView(Screen):
    controller = ObjectProperty(None)
    error_message = StringProperty('')

    # Handle Signup button press by delegating to controller
    def on_signup_press(self):
        if self.controller:
            username = self.ids.username_input.text.strip()
            email = self.ids.email_input.text.strip()
            password = self.ids.password_input.text.strip()
            confirm_password = self.ids.password_input.text.strip()
            self.controller.register(username, email, password, confirm_password)

    #Navigate to login screen
    def on_login_press(self):
        if self.controller:
            self.controller.navigate_to_login()


    def set_error(self, message):
        """Update error message (called by controller)"""
        self.error_message = message
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App


class LoginView(Screen):
    controller = ObjectProperty(None)
    error_message = StringProperty('')

    # Handle login button press by delegating to controller
    def on_login_press(self):
        if self.controller:
            username = self.ids.username_input.text.strip()
            password = self.ids.password_input.text.strip()
            self.controller.login(username, password)

            
        if not username or not password:
            if not username:
                self.ids.username_input.error = True
            if not password:
                self.ids.password_input.error = True
            self.error_message = "Please fill in all fields"
            return
            
    #Navigate to signup screen
    def on_signup_press(self):
        if self.controller:
            self.controller.navigate_to_signup()


    def set_error(self, message):
        """Update error message (called by controller)"""
        self.error_message = message

    def clear_fields(self):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
        self.error_message = ""
import logging
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty, ObjectProperty

# Setup logger for this module
logger = logging.getLogger(__name__)

class LoginScreen(MDScreen):
    controller = ObjectProperty(None)
    error_message = StringProperty('')
    dialog = None  # initialize dialog

    def on_login_press(self):
        if not self.controller:
            logger.warning("LoginScreen: No controller attached")
            return

        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        if not username or not password:
            if not username:
                self.ids.username.error = True
            if not password:
                self.ids.password.error = True
            self.set_error("Please fill in all fields")
            return

        self.controller.login(username, password)

    def on_signup_press(self):
        if self.controller:
            self.controller.navigate_to_signup()

    def set_error(self, message):
        """Update error message and show dialog"""
        self.error_message = message
        self.show_error_dialog(message)

    def clear_fields(self):
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.error_message = ""

    def show_error_dialog(self, message):
        """Show error dialog with the given message"""
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

        logger.debug(f"Showing error dialog: {message}")
        self.dialog.open()

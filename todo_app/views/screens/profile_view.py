from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

class ProfileScreen(Screen):
    username = StringProperty("User")

    def on_enter(self, *args):
        # Access the app instance
        app = self.manager.app
        if app and app.current_user:
            self.username = app.current_user.username

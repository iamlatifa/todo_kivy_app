from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock





class SidebarView(BoxLayout):
    """Sidebar navigation widget"""
    username = StringProperty("User")
    controller = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.setup_pos_binding)

    
    def on_nav_press(self, screen_name):
        """Handle navigation button press"""
        app = App.get_running_app()
        app.navigate_to(screen_name)
    
    def on_logout_press(self):
        """Handle logout button press"""
        app = App.get_running_app()
        app.logout_user()
        print("Logout pressed")

    
    def update_username(self, username):
        """Update displayed username"""
        self.username = username


    def setup_pos_binding(self, *args):
        self.bind(x=self.update_pos)
    def update_pos(self, *args):
        self.pos = (self.x, self.y)  # This forces it to move visually


    def close_sidebar(self):
        if self.controller:
            self.controller.toggle_sidebar()  # assuming controller handles open/close

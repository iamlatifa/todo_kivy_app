from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
import logging

logger = logging.getLogger(__name__)

class SidebarView(BoxLayout):
    username = StringProperty("")
    controller = ObjectProperty(None)
    is_open = BooleanProperty(False)
    _animation = None  # Store current animation

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_sidebar)
        self.model = ObjectProperty(None)

    def init_sidebar(self, *args):
        """Initialize sidebar in closed state"""
        self.width = dp(280)
        self.x = -self.width
        self.opacity = 1
        self.disabled = True
        self.is_open = False

    def toggle(self, *args):
        """Toggle sidebar with animation"""
        if self._animation:  # prevent overlapping animations
            return

        target_x = 0 if not self.is_open else -self.width
        #target_opacity = 1 if not self.is_open else 0

        self.disabled = False 
        if not self.is_open:
            self.opacity = 1 # enable before animating
        self._animation = Animation(x=target_x, duration=0.3, t='out_quad')
        self._animation.bind(on_complete=self._on_animation_complete)
        self._animation.start(self)

    def _on_animation_complete(self, animation, widget):
        """Handle animation completion"""
        self.is_open = self.x == 0
        if not self.is_open:
            self.disabled = True 
            self.opacity = 1 # only disable after closing
        self._animation = None
        # logger.debug(f"Sidebar animation completed, is_open: {self.is_open}")

    def close_sidebar(self, *args):
        """Force close the sidebar"""
        if self.is_open:
            self.toggle()

    def on_nav_press(self, screen_name):
        """Handle navigation item press"""
        app = App.get_running_app()
        if app and hasattr(app.root, 'current'):
            app.root.current = screen_name
            Clock.schedule_once(self.close_sidebar, 0.1)

    def on_logout_press(self):
        """Handle logout button press"""
        app = App.get_running_app()
        app.logout_user()
        print("Logout pressed")
        Clock.schedule_once(self.close_sidebar, 0.1)

    def update_username(self, *args):
        """Update displayed username"""
        app = App.get_running_app()
        try:
            user = app.current_user
            self.username = user.username
        except Exception as e:
            logger.error(f"Failed to load user data: {e}")

    def open_sidebar(self):
        """Open the sidebar explicitly"""
        self.disabled = False
        self.opacity = 1
        Animation.cancel_all(self)
        anim = Animation(x=0, duration=0.3)
        anim.bind(on_complete=self._on_animation_complete)
        anim.start(self)

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty
import os
import json
import logging
from kivy.logger import Logger as KivyLogger
import sys
# Models
from models.user import User
from models.task import Task

# Views (Screens)
from views.screens.login_screen import LoginScreen
from views.screens.signup_screen import SignupScreen
from views.screens.home_screen import HomeView
from views.screens.add_task_screen import AddTaskView
from views.screens.profile_screen import ProfileScreen
from views.screens.completed_tasks_screen import CompletedTasksView
from views.screens.loading_screen import LoadingScreen  
from views.screens.edit_task_screen import EditTaskScreen
# Controllers and Services
from controllers.login_controller import LoginController
from controllers.signup_controller import SignupController
from controllers.task_controller import TaskController
from services.api_service import ApiService
from kivy.utils import platform

if platform == "android":
    # Only set KIVY_HOME if on Android
    from android.storage import app_storage_path
    os.environ["KIVY_HOME"] = os.path.join(app_storage_path(), ".kivy_user")


from kivy.core.text import LabelBase


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Make Kivy's logger work with Python's logging
logging.getLogger('kivy').setLevel(logging.INFO)

class TodoApp(MDApp):
    current_user = ObjectProperty(None, allownone=True)
    is_authenticated = BooleanProperty(False)
    api = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.api_service = ApiService()

        # Load KV files
        kv_files = [
            'task_item_view.kv',
            'side_bar_view.kv',
            'edit_task_screen.kv',
            'home_screen.kv',
            'login_screen.kv',
            'signup_screen.kv',
            'add_task_screen.kv',
            'profile_screen.kv',
            'completed_tasks_screen.kv',
            'loading_screen.kv'
        ]
        kv_directory = os.path.join(os.path.dirname(__file__), 'views', 'kv')
        for kv_file in kv_files:
            try:
                kv_path = os.path.join(kv_directory, kv_file)
                if kv_path not in Builder.files:
                    Builder.load_file(kv_path)
            except Exception as e:
                print(f"Error loading {kv_file}: {str(e)}")
                raise

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "BlueGray"
        self.theme_cls.theme_style = "Light"
        logger = logging.getLogger(__name__)
        logger.info("Building TodoApp")

        from kivy.utils import platform
        logger.info(f"Running on platform: {platform}")
    

        self.sm = ScreenManager()

        # Create screen instances
        self.login_screen = LoginScreen(name='login')
        self.signup_screen = SignupScreen(name='signup')
        self.home_screen = HomeView(name='home')
        self.add_task_screen = AddTaskView(name='add_task')
        self.edit_task_screen = EditTaskScreen(name='edit_task')
        self.profile_screen = ProfileScreen(name='profile')
        self.completed_tasks_screen = CompletedTasksView(name='completed_tasks')
        self.loading_screen = LoadingScreen(name='loading')

        # Add screens
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.signup_screen)
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.add_task_screen)
        self.sm.add_widget(self.edit_task_screen)
        self.sm.add_widget(self.profile_screen)
        self.sm.add_widget(self.completed_tasks_screen)
        self.sm.add_widget(self.loading_screen)


        self.task = Task()

        logger.info("Initializing controllers")

        # Initialize controllers
        self.login_controller = LoginController(app=self, view=self.login_screen,api=self.api_service)
        self.signup_controller = SignupController(app=self, view=self.signup_screen,api=self.api_service)
        self.task_controller = TaskController(app=self, home_view=self.home_screen, api_service=self.api_service)
        self.completed_tasks_screen.controller = self.task_controller
        self.add_task_screen.controller = self.task_controller
        self.task_controller.set_completed_tasks_view(self.completed_tasks_screen)
        self.task_controller.view = self.add_task_screen  
        self.profile_screen.controller = self.task_controller

        self.signup_screen.controller = self.signup_controller

        logger.info("Checking for existing session")

        # Auto-login if session exists
        logger.info("Checking for existing session")
        user_id = self.load_session()
        if user_id:
            logger.info(f"Found session for user ID: {user_id}")
            user_data = self.api_service.get_user(user_id)
            if user_data:
                logger.info("User data retrieved, logging in")
                Clock.schedule_once(lambda dt: self.task_controller.load_completed_tasks(), 1)
                self.login_user(user_data)
                self.sm.current = "home"
            else:
                logger.warning("User data not found, going to loading screen")
                self.sm.current = "loading"
        else:
            logger.info("No session found, going to login screen")
            self.sm.current = "login"

        return self.sm

    def check_session(self, dt):
        from threading import Thread
        Thread(target=self._do_session_check).start()

    def _do_session_check(self):
        import time
        time.sleep(1.5)
        is_logged_in = self.login_controller.is_logged_in()
        Clock.schedule_once(lambda dt: self.navigate_to('home' if is_logged_in else 'login'), 0)

    def navigate_to(self, screen_name):
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            print(f"Screen '{screen_name}' does not exist!")

    def load_session(self):
        if os.path.exists("user_session.json"):
            with open("user_session.json", "r") as f:
                session = json.load(f)
                return session.get("user_id")
        return None

    def login_user(self, user_data):
        logger = logging.getLogger(__name__)
        logger.info(f"Setting up user session")
        
        # Check if user_data contains error
        if isinstance(user_data, dict) and "error" in user_data:
            logger.error(f"Login error: {user_data['error']}")
            return False
        
        self.current_user = User.from_dict(user_data)
        self.is_authenticated = True
        
        # Save session
        try:
            with open("user_session.json", "w") as f:
                import json
                session_data = {"user_id": self.current_user.id}
                json.dump(session_data, f)
                logger.info(f"Saved session for user ID: {self.current_user.id}")
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")
        
        self.sm.current = 'home'
        return True

    def logout_user(self):
        self.current_user = None
        self.is_authenticated = False
        if os.path.exists("user_session.json"):
            os.remove("user_session.json")

        
        self.sm.current = 'login'


if __name__ == '__main__':
    TodoApp().run()

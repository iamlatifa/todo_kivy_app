from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.lang import Builder
import os
import json

# Controllers
from controllers.task_controller import TaskController
from controllers.add_task_controller import AddTaskController
from controllers.login_controller import LoginController
from controllers.signup_controller import SignupController

# Services
from services.database import Database

# Views
from views.screens.login_view import LoginView
from views.screens.signup_view import SignupView
from views.screens.home_view import HomeView
from views.screens.add_task_view import AddTaskView
from views.widgets.side_bar import SidebarView


from views.widgets.drop_container import DropContainer


# Models
from models.user import User
from models.task import Task  # ✅ Added





class ToDoApp(MDApp):
    current_user = ObjectProperty(None, allownone=True)
    is_authenticated = BooleanProperty(False)
    db = ObjectProperty(None)

    from kivy.factory import Factory
    Factory.register('SidebarView', cls=SidebarView)

    from kivy.factory import Factory
    Factory.register('DropContainer', cls=DropContainer)


    def build(self):
        Window.size = (400, 700)
        self.db = Database()
    
        


        # Load KV files
        Builder.load_file('views/kv/login.kv')
        Builder.load_file('views/kv/signup.kv')
        Builder.load_file('views/kv/home.kv')
        Builder.load_file('views/kv/sidebar.kv')
        Builder.load_file('views/kv/add_task_view.kv')
        Builder.load_file('views/kv/task_item_view.kv')
        Builder.load_file('views/kv/edit_task_popup.kv')



        # Initialize ScreenManager
        self.screen_manager = ScreenManager(transition=NoTransition())

        # Create views
        login_view = LoginView(name="login")
        signup_view = SignupView(name="signup")
        self.home_view = HomeView(name="home")
        self.add_task_view = AddTaskView(name="add_task")

        # Add views to manager
        self.screen_manager.add_widget(login_view)
        self.screen_manager.add_widget(signup_view)
        self.screen_manager.add_widget(self.home_view)
        self.screen_manager.add_widget(self.add_task_view)

        # ✅ Initialize model
        self.task = Task()

        # Initialize controllers
        LoginController(app=self, view=login_view)
        SignupController(app=self, view=signup_view)
        self.task_controller = TaskController(app=self, home_view=self.home_view, model=self.db)
        self.add_task_controller = AddTaskController(app=self, screen=self.add_task_view)

        # Try auto-login if session exists
        user_id = self.load_session()
        if user_id:
            user_data = self.db.get_user_by_id(user_id)
            if user_data:
                self.login_user(user_data)
                self.screen_manager.current = "home"
            else:
                self.screen_manager.current = "login"
        else:
            self.screen_manager.current = "login"

        return self.screen_manager

    def login_user(self, user_data):
        self.current_user = User.from_dict(user_data)
        self.is_authenticated = True
        self.screen_manager.current = 'home'

    def logout_user(self):
        self.current_user = None
        self.is_authenticated = False
        self.screen_manager.current = 'login'

    def navigate_to(self, screen_name):
        if screen_name == 'login' and self.is_authenticated:
            self.logout_user()
        else:
            self.screen_manager.current = screen_name

    def load_session(self):
        if os.path.exists("user_session.json"):
            with open("user_session.json", "r") as f:
                session = json.load(f)
                return session.get("user_id")
        return None

    

    
if __name__ == '__main__':
    ToDoApp().run()

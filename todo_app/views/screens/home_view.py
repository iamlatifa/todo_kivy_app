from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from views.widgets.side_bar import SidebarView
from views.widgets.task_item import TaskItemView

class HomeView(Screen):
    # Home screen view implementation showing tasks list
    controller = ObjectProperty(None)

    def on_enter(self):
        if self.controller:
            # Load tasks from the controller when entering the screen
            self.controller.load_tasks()
        self.ids.sidebar.x = -250

    def on_kv_post(self, base_widget):
        # Attach the controller to the sidebar after kv is loaded
        self.ids.sidebar.controller = self
        # Initialize sidebar to be off-screen
        self.ids.sidebar.x = -250

    def toggle_sidebar(self):
        sidebar = self.ids.sidebar
        if sidebar.x < 0:
            Animation(x=0, d=0.3).start(sidebar)
        else:
            Animation(x=-250, d=0.3).start(sidebar)

    def on_add_task_press(self):
        # Transition to the add task screen
        self.manager.current = 'add_task'

    def on_filter_press(self, filter_type):
        # Handle filter button press with validation
        if self.controller:
            if filter_type in ["all", "completed", "pending"]:  # Example filter types
                self.controller.filter_tasks(filter_type)

    def clear_tasks(self):
        # Use Clock to ensure the widget list is cleared after layout is stable
        Clock.schedule_once(lambda dt: self.ids.tasks_container.clear_widgets(), 0)

    def add_task_widget(self, task_widget):
        # Add task widget to container after layout is stable
        Clock.schedule_once(lambda dt: self.ids.tasks_container.add_widget(task_widget), 0)
        print("Adding task widget:", task_widget)

    def show_empty_message(self):
        # Show a message when no tasks are available
        label = Label(
            text="No tasks found",
            size_hint_y=None,
            height="50dp"
        )
        self.ids.tasks_container.add_widget(label)

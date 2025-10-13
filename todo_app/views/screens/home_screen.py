# Updated home_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.app import App
from threading import Thread
import logging
from kivymd.uix.label import MDLabel
from views.widgets.task_item import TaskItemView
from views.widgets.loading_widget import LoadingWidget, PulsingDotIndicator

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class HomeView(Screen):
    controller = ObjectProperty(None)
    sidebar_open = BooleanProperty(False)
    tasks_per_page = NumericProperty(10)
    current_page = NumericProperty(0)
    loading_more = BooleanProperty(False)
    tasks = ListProperty([])
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Initializing HomeView")
        
        # Create loading indicators
        self.main_loading = LoadingWidget()
        self.more_loading = PulsingDotIndicator()
        
        Clock.schedule_once(self._late_init)

    def _late_init(self, *args):
        logger.info("Late init called")
        self._setup_sidebar()
        self._setup_loading_indicators()

    def _setup_loading_indicators(self):
        """Add loading indicators to the screen"""
        try:
            # Add main loading indicator (overlay)
            self.add_widget(self.main_loading)
            
            # Add minimal loading indicator to task list if it exists
            if hasattr(self.ids, 'task_list_container'):
                self.ids.task_list_container.add_widget(self.more_loading)
        except Exception as e:
            logger.error(f"Error setting up loading indicators: {e}")

    def _setup_sidebar(self):
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'current_user') and app.current_user:
                username = app.current_user.username
                logger.info(f"Got username from current_user: {username}")
                if username and 'sidebar' in self.ids:
                    self.ids.sidebar.username = username
        except Exception as e:
            logger.error(f"Error setting up sidebar: {e}")

    def on_pre_enter(self):
        super().on_pre_enter()
        if self.controller:
            try:
                if not hasattr(self.controller, 'prevent_double_loading') or not self.controller.prevent_double_loading:
                    self.controller.invalidate_cache()
                    Clock.schedule_once(lambda dt: self.reset_and_load_tasks(), 0.2)
                else:
                    self.controller.prevent_double_loading = False
                    Clock.schedule_once(lambda dt: self.reset_and_load_tasks(), 0.2)
            except Exception as e:
                logger.error(f"Error in on_pre_enter: {e}")

    def on_enter(self):
        super().on_enter()
        self._ensure_sidebar_closed()

    def _ensure_sidebar_closed(self):
        try:
            if not hasattr(self.ids, 'sidebar'):
                logger.warning("Sidebar widget not found")
                return

            self.sidebar_open = False
            self.ids.sidebar.x = -self.ids.sidebar.width
            self.ids.sidebar.opacity = 0
            self.ids.sidebar.disabled = True
            self.ids.sidebar.is_open = False
        except Exception as e:
            logger.error(f"Error closing sidebar: {e}")

    def reset_and_load_tasks(self):
        """Reset and load only uncompleted tasks"""
        logger.info("Resetting and loading uncompleted tasks...")
        if not self.controller:
            logger.warning("reset_and_load_tasks: Controller is not set.")
            return
            
        self.current_page = 0
        self.tasks = []
        self.clear_tasks()
        self.is_loading = True
        
        # Show main loading indicator
        self.main_loading.show()
        
        Thread(target=self._load_tasks_thread).start()

    def _load_tasks_thread(self):
        """Load only uncompleted tasks in a separate thread"""
        if not self.controller:
            Clock.schedule_once(lambda dt: self._set_loading_complete(), 0)
            return

        try:
            all_tasks = self.controller.get_tasks_sync(completed=False)
            start = self.current_page * self.tasks_per_page
            end = start + self.tasks_per_page
            paginated_tasks = all_tasks[start:end]

            if not paginated_tasks:
                Clock.schedule_once(lambda dt: self._set_loading_complete(), 0)
                Clock.schedule_once(lambda dt: self.show_empty_message(), 0.5)
                return

            Clock.schedule_once(lambda dt: self.on_tasks_data_loaded(paginated_tasks), 0)

        except Exception as e:
            logger.error(f"[THREAD] Error during task loading: {e}", exc_info=True)
            Clock.schedule_once(lambda dt: self._set_loading_complete(), 0)

    def on_tasks_data_loaded(self, task_list):
        self.clear_tasks()
        for task in task_list:
            widget = self.create_task_widget(task)
            self.add_task_widget(widget)
        self._set_loading_complete()

    def _set_loading_complete(self, *args):
        self.loading_more = False
        self.is_loading = False
        
        # Hide loading indicators
        self.main_loading.hide()
        self.more_loading.hide()

    def create_task_widget(self, task):
        widget = TaskItemView(
            task_id=task['id'],
            title=task['title'],
            description=task.get('description', ''),
            due_date=task.get('due_date', 'No due date'),
            priority=task.get('priority', 'low'),
            completed=False,
            controller=self.controller
        )
        widget.bind(completed=self.on_task_completion_changed)
        return widget

    def on_task_completion_changed(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.reset_and_load_tasks(), 0.3)
            
            app = App.get_running_app()
            if hasattr(app, 'task_controller') and app.task_controller.completed_tasks_screen:
                Clock.schedule_once(lambda dt: app.task_controller.load_completed_tasks(), 0.5)

    def clear_tasks(self):
        if hasattr(self.ids, 'task_list'):
            logger.debug("Clearing tasks container")
            self.ids.task_list.clear_widgets()
        else:
            logger.warning("task_list not found in ids")

    def add_task_widget(self, task_widget):
        if hasattr(self.ids, 'task_list'):
            self.ids.task_list.add_widget(task_widget)
        else:
            logger.warning("task_list not found in ids")

    def load_more_tasks(self, *args):
        if not self.loading_more:
            self.loading_more = True
            self.is_loading = True
            
            # Show minimal loading indicator for "load more"
            self.more_loading.show()
            
            Thread(target=self._load_tasks_thread).start()

    def on_scroll_move(self, scroll_y):
        if scroll_y <= 0.1 and not self.loading_more:
            logger.debug("Near bottom of scroll, loading more tasks")
            Clock.schedule_once(lambda dt: self.load_more_tasks(), 0.1)

    def show_empty_message(self):
        if hasattr(self.ids, 'task_list'):
            self.ids.task_list.add_widget(MDLabel(
                text="No tasks to do! Create a new task to get started.",
                halign="center",
                theme_text_color="Hint",
                padding="12dp",
                adaptive_height=True
            ))

    # ... rest of your existing methods remain the same ...
    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open
        if hasattr(self.ids, 'sidebar'):
            self.ids.sidebar.toggle()

    def show_add_task_dialog(self):
        print("Switching to add_task screen")
        self.manager.current = 'add_task'

    def show_completed_tasks(self):
        print("Switching to completed_tasks screen")
        self.manager.current = 'completed_tasks'

    def on_overlay_touch(self, instance, touch):
        if self.sidebar_open and hasattr(self.ids, 'sidebar_overlay'):
            if self.ids.sidebar_overlay.collide_point(*touch.pos):
                Clock.schedule_once(lambda dt: self.toggle_sidebar(), 0)
                logger.debug("Sidebar overlay touch detected")

    def on_filter_press(self, filter_type):
        if self.controller:
            if filter_type == "completed":
                self.show_completed_tasks()
            else:
                self.controller.filter_tasks(filter_type)

    def on_touch_down_outside_sidebar(self, window, touch):
        if not self.sidebar_open:
            return
        if hasattr(self.ids, 'sidebar'):
            sidebar_widget = self.ids.sidebar
            if not sidebar_widget.collide_point(*touch.pos):
                Clock.schedule_once(lambda dt: self.close_sidebar(), 0)
                logger.debug("Touch outside sidebar detected")

    def close_sidebar(self):
        if self.sidebar_open and hasattr(self.ids, 'sidebar'):
            self.toggle_sidebar()
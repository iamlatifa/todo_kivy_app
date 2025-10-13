from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.app import App
from threading import Thread
from kivymd.uix.label import MDLabel
from views.widgets.task_item import TaskItemView
from views.widgets.loading_widget import LoadingWidget  # <-- ADDED

import logging
logger = logging.getLogger(__name__)

class CompletedTasksView(Screen):
    controller = ObjectProperty(None)
    tasks_per_page = NumericProperty(10)
    current_page = NumericProperty(0)
    loading_more = BooleanProperty(False)
    tasks = ListProperty([])
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_loading = LoadingWidget()  # <-- ADDED
        Clock.schedule_once(self._add_loading_indicator)  # <-- ADDED

    def _add_loading_indicator(self, *args):
        self.add_widget(self.main_loading)  # <-- ADDED

    def on_pre_enter(self):
        if self.controller:
            self.reset_and_load_tasks()

    def reset_and_load_tasks(self):
        logger.info("Resetting and loading completed tasks...")
        self.current_page = 0
        self.tasks = []
        self.clear_tasks()
        self.is_loading = True
        self.main_loading.show()  # <-- ADDED
        Thread(target=self._load_tasks_thread).start()

    def _load_tasks_thread(self):
        if not self.controller:
            Clock.schedule_once(lambda dt: self._set_loading_complete(), 0)
            return

        try:
            all_tasks = self.controller.get_tasks_sync(completed=True)
            start = self.current_page * self.tasks_per_page
            end = start + self.tasks_per_page
            paginated_tasks = all_tasks[start:end]

            if not paginated_tasks:
                Clock.schedule_once(lambda dt: self._set_loading_complete(), 0)
                Clock.schedule_once(lambda dt: self.show_empty_message(), 0.5)
                return

            Clock.schedule_once(lambda dt: self._on_tasks_loaded(paginated_tasks), 0)

        except Exception as e:
            logger.error(f"[Completed] Error loading tasks: {e}", exc_info=True)
            Clock.schedule_once(lambda dt: self._set_loading_complete(), 0)

    def _on_tasks_loaded(self, paginated_tasks):
        for task in paginated_tasks:
            widget = self.create_task_widget(task)
            self.add_task_widget(widget)
        self.current_page += 1
        self._set_loading_complete()

    def _set_loading_complete(self, *args):
        self.loading_more = False
        self.is_loading = False
        self.main_loading.hide()  # <-- ADDED

    def create_task_widget(self, task):
        widget = TaskItemView(
            task_id=task['id'],
            title=task['title'],
            description=task.get('description', ''),
            due_date=task.get('due_date', 'No due date'),
            priority=task.get('priority', 'low'),
            completed=True,  # These are completed tasks
            controller=self.controller
        )
        return widget

    def clear_tasks(self):
        if hasattr(self.ids, 'task_list'):
            self.ids.task_list.clear_widgets()

    def add_task_widget(self, widget):
        if hasattr(self.ids, 'task_list'):
            self.ids.task_list.add_widget(widget)

    def on_scroll_move(self, scroll_y):
        if scroll_y <= 0.1 and not self.loading_more:
            Clock.schedule_once(lambda dt: self.load_more_tasks(), 0.1)

    def load_more_tasks(self, *args):
        if not self.loading_more:
            self.loading_more = True
            self.is_loading = True
            Thread(target=self._load_tasks_thread).start()

    def on_tasks_data_loaded(self, task_list):
        self.clear_tasks()
        self.tasks = task_list
        widgets = [self.create_task_widget(task) for task in task_list]
        for widget in widgets:
            self.add_task_widget(widget)

    def show_empty_message(self):
        if hasattr(self.ids, 'task_list'):
            self.ids.task_list.add_widget(MDLabel(
                text="No completed tasks yet.",
                halign="center",
                theme_text_color="Hint",
                padding="12dp",
                adaptive_height=True
            ))

    def on_back_press(self):
        self.manager.current = 'home'

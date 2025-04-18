from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from views.widgets.side_bar import SidebarView
from views.widgets.task_item import TaskItemView



class HomeView(Screen):
#Home screen view implementation showing tasks list
    controller = ObjectProperty(None)


    
    # Called when screen is entered
    def on_enter(self):
        if self.controller:
            self.controller.load_tasks()

    def on_kv_post(self, base_widget):
        # Attach the controller to the sidebar after kv is loaded
        self.ids.sidebar.controller = self    

    def toggle_sidebar(self):
        # print("Toggling sidebar!")  
        sidebar = self.ids.sidebar
        if sidebar.x < 0:
            # print("Opening sidebar")
            Animation(x=0, d=0.3).start(sidebar)
        else:
            # print("Closing sidebar")
            Animation(x=-250, d=0.3).start(sidebar)
    
    def on_add_task_press(self):
        self.manager.current = 'add_task'  

    
    def on_filter_press(self, filter_type):
        #Handle filter button press
        if self.controller:
            self.controller.filter_tasks(filter_type)
    
    def clear_tasks(self):
        Clock.schedule_once(lambda dt: self.ids.tasks_container.clear_widgets(), 0)


    def add_task_widget(self, task_widget):
        # Schedule widget addition after layout is stable
        Clock.schedule_once(lambda dt: self.ids.tasks_container.add_widget(task_widget), 0)
        print("Adding task widget:", task_widget)

    
    def show_empty_message(self):
        #Show a message when no tasks are available
        label = Label(
            text="No tasks found",
            size_hint_y=None,
            height="50dp"
        )
        self.ids.tasks_container.add_widget(label)




   
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.properties import ObjectProperty
from kivymd.uix.menu import MDDropdownMenu

class EditTaskScreen(MDScreen):
    controller = ObjectProperty()
    task_data = ObjectProperty()
    priority_menu = None

    def on_pre_enter(self):
        self.ids.title_input.text = self.task_data.get("title") or ""
        self.ids.description_input.text = self.task_data.get("description") or ""
        self.ids.due_date_input.text = self.task_data.get("due_date") or ""

        priority = self.task_data.get("priority") or "Medium"
        self.set_priority(priority)  # sets both color and text
        self.update_field_colors()

    def save_task(self):
        title = self.ids.title_input.text
        description = self.ids.description_input.text
        due_date = self.ids.due_date_input.text
        priority = self.ids.priority_button.text

        if not title.strip():
            toast("Title is required")
            return

        success = self.controller.update_task(
            self.task_data["id"], title, description, due_date, priority
        )

        if success:
            toast("Task updated successfully")
            self.manager.current = "home"  # Go back to main/home screen
        else:
            toast("Failed to update task")



    def show_priority_menu(self):
        priorities = ["Low", "Medium", "High", "Urgent"]
        menu_items = [
            {
                "text": p,
                "viewclass": "OneLineListItem",  # Ensure the items are visible
                "on_release": lambda x=p: self.set_priority(x),
                "text_color": (0, 0, 0, 1),  # Optional: ensure black text
            }
            for p in priorities
        ]

        self.priority_menu = MDDropdownMenu(
            caller=self.ids.priority_button,
            items=menu_items,
            width_mult=4
        )
        self.priority_menu.open()


    def set_priority(self, priority):
        self.ids.priority_button.text = priority
        self.ids.priority_button.md_bg_color = self.get_priority_color(priority)
        if self.priority_menu:
            self.priority_menu.dismiss()

    def get_priority_color(self, priority):
        return {
            "Low": (0.25, 0.64, 0.96, 1),
            "Medium": (1, 0.55, 0, 1),
            "High": (0.9, 0.2, 0.2, 1),
            "Urgent": (0.6, 0, 0, 1),
        }.get(priority, (0.5, 0.5, 0.5, 1))  # Default gray

    def open_date_picker(self):
        from kivymd.uix.pickers import MDDatePicker
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.on_date_chosen)
        date_picker.open()

    def on_date_chosen(self, instance, value, date_range):
        self.ids.due_date_input.text = value.strftime("%Y-%m-%d")

    def cancel_edit(self):
        self.manager.current = "home"

    def update_field_colors(self):
        blue = (0.25, 0.64, 0.96, 1)  # Material Blue

        if self.ids.description_input.text.strip():
            self.ids.description_input.line_color_normal = blue
            self.ids.description_input.line_color_focus = blue
            self.ids.description_input.text_color = blue

        if self.ids.due_date_input.text.strip():
            self.ids.due_date_input.line_color_normal = blue
            self.ids.due_date_input.line_color_focus = blue
            self.ids.due_date_input.text_color = blue

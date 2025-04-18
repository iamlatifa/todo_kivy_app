from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.clock import Clock


class DropContainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10

    def reorder_widget(self, widget):
        if widget not in self.children:
            return

        old_children = list(self.children)
        old_index = old_children.index(widget)

        self.remove_widget(widget)
        inserted = False
        for index, child in enumerate(reversed(old_children)):
            if widget.top > child.top:
                self.add_widget(widget, index=len(old_children) - index)
                inserted = True
                break


        if not inserted:
            self.add_widget(widget)

        new_children = list(self.children)
        new_index = new_children.index(widget)

        # Animate only affected widgets
        moved_widgets = []

        if new_index < old_index:
            moved_widgets = new_children[new_index + 1: old_index + 1]
        elif new_index > old_index:
            moved_widgets = new_children[old_index:new_index]

        # # Disable layout briefly to avoid jitter
        # for child in self.children:
        #     child.disabled = True

        Clock.schedule_once(lambda dt: self.animate_widgets(moved_widgets), 0.01)


    def animate_widgets(self, widgets):
        for widget in widgets:
            anim = Animation(y=widget.y, duration=0.2, t='out_quad')
            anim.start(widget)
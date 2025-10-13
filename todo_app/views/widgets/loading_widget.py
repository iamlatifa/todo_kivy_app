from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Line
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

class LoadingWidget(Widget):
    """Modern top progress bar indicator"""
    
    progress = NumericProperty(0)
    is_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = 6  # Thin progress bar
        self.pos_hint = {"top": 1}  # Stick to top
        self.opacity = 0
        
        # Create graphics
        with self.canvas:
            # Background line (light gray)
            Color(0.9, 0.9, 0.9, 1)
            self.bg_line = Rectangle(pos=self.pos, size=(self.width, self.height))
            
            # Progress line (modern blue)
            Color(1, 1, 1, 1)  # Modern blue color
            self.progress_line = Rectangle(pos=self.pos, size=(0, self.height))
        
        # Bind to update graphics when widget changes
        self.bind(pos=self._update_graphics, size=self._update_graphics, progress=self._update_progress)
        
        # Animation properties
        self.animation_event = None
        self.current_progress = 0
        
    def _update_graphics(self, *args):
        """Update graphics when widget position/size changes"""
        self.bg_line.pos = self.pos
        self.bg_line.size = (self.width, self.height)
        self.progress_line.pos = self.pos
        self._update_progress()
        
    def _update_progress(self, *args):
        """Update progress line width"""
        progress_width = self.width * (self.progress / 100.0)
        self.progress_line.size = (progress_width, self.height)
        
    def show(self):
        """Show and animate the progress bar"""
        self.is_visible = True
        self.progress = 0
        self.current_progress = 0

        # Immediately show the widget container (but progress is 0)
        self.opacity = 1

        # Start growing the progress line
        self._start_progress_animation()


        
    def hide(self):
        """Hide the progress bar"""
        self.is_visible = False
        self._stop_progress_animation()
        
        # Quick finish animation then fade out
        finish_anim = Animation(progress=100, duration=0.1)
        finish_anim.bind(on_complete=self._fade_out)
        finish_anim.start(self)
        
    def _fade_out(self, *args):
        """Fade out after completion"""
        Animation(opacity=0, duration=0.3).start(self)
        
    def _start_progress_animation(self):
        """Start the indeterminate progress animation"""
        self.animation_event = Clock.schedule_interval(self._update_animation, 0.05)
        
    def _stop_progress_animation(self):
        """Stop the progress animation"""
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
            
    def _update_animation(self, dt):
        """Update the progress animation"""
        # Simulate realistic loading progress
        if self.current_progress < 30:
            self.current_progress += 2
        elif self.current_progress < 60:
            self.current_progress += 1
        elif self.current_progress < 90:
            self.current_progress += 0.5
        else:
            self.current_progress += 0.1
            
        # Cap at 95% until we actually finish
        self.progress = min(self.current_progress, 95)


class PulsingDotIndicator(Widget):
    """Modern pulsing dot indicator for inline loading"""
    
    is_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 20)
        self.opacity = 0
        
        # Create three dots
        with self.canvas:
            self.dots = []
            for i in range(3):
                Color(0.4, 0.4, 0.4, 1)  # Gray dots
                x_pos = self.x + 10 + (i * 20)
                y_pos = self.center_y
                dot = Line(circle=(x_pos, y_pos, 3), width=2)
                self.dots.append(dot)
        
        self.bind(pos=self._update_dots, size=self._update_dots)
        self.animation_event = None
        self.dot_index = 0
        
    def _update_dots(self, *args):
        """Update dot positions"""
        for i, dot in enumerate(self.dots):
            x_pos = self.x + 10 + (i * 20)
            y_pos = self.center_y
            dot.circle = (x_pos, y_pos, 3)
            
    def show(self):
        """Show the pulsing dots"""
        self.is_visible = True
        Animation(opacity=1, duration=0.2).start(self)
        self._start_pulse_animation()
        
    def hide(self):
        """Hide the pulsing dots"""
        self.is_visible = False
        self._stop_pulse_animation()
        Animation(opacity=0, duration=0.2).start(self)
        
    def _start_pulse_animation(self):
        """Start the pulsing animation"""
        self.dot_index = 0
        self.animation_event = Clock.schedule_interval(self._pulse_next_dot, 0.4)
        
    def _stop_pulse_animation(self):
        """Stop the pulsing animation"""
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
            
    def _pulse_next_dot(self, dt):
        """Pulse the next dot"""
        # Reset all dots to normal
        with self.canvas:
            for i, dot in enumerate(self.dots):
                if i == self.dot_index:
                    Color(0.2, 0.6, 1, 1)  # Bright blue for active dot
                else:
                    Color(0.4, 0.4, 0.4, 1)  # Gray for inactive dots
                    
                x_pos = self.x + 10 + (i * 20)
                y_pos = self.center_y
                dot.circle = (x_pos, y_pos, 3)
                
        self.dot_index = (self.dot_index + 1) % 3


class ModernLoadingOverlay(MDBoxLayout):
    """Modern loading overlay with text and progress"""
    
    loading_text = StringProperty("Loading...")
    is_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "16dp"
        self.size_hint = (None, None)
        self.size = ("200dp", "80dp")
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.opacity = 0
        self.disabled = True
        
        # Add some padding and background
        with self.canvas.before:
            Color(0, 0, 0, 0.1)  # Semi-transparent dark background
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Loading text
        self.loading_label = MDLabel(
            text=self.loading_text,
            halign="center",
            theme_text_color="Primary",
            font_style="Caption",
            adaptive_height=True
        )
        
        # Pulsing dots
        self.dots_indicator = PulsingDotIndicator(
            pos_hint={"center_x": 0.5}
        )
        
        self.add_widget(self.loading_label)
        self.add_widget(self.dots_indicator)
        
    def _update_bg(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
    def show(self, text="Loading..."):
        """Show the loading overlay"""
        self.loading_text = text
        self.loading_label.text = text
        self.is_visible = True
        self.disabled = False
        
        # Fade in
        Animation(opacity=1, duration=0.3).start(self)
        self.dots_indicator.show()
        
    def hide(self):
        """Hide the loading overlay"""
        self.is_visible = False
        self.dots_indicator.hide()
        
        # Fade out
        fade_out = Animation(opacity=0, duration=0.3)
        fade_out.bind(on_complete=lambda anim, widget: setattr(self, 'disabled', True))
        fade_out.start(self)


# Main loading indicators to use
class ModernLoadingIndicator(LoadingWidget):
    """Main loading indicator - top progress bar"""
    pass

class MinimalLoadingIndicator(ModernLoadingOverlay):
    """Minimal loading indicator - small overlay with pulsing dots"""
    pass
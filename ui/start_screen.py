from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.widget import Widget
import json

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )
        
        # Title
        title = Label(
            text='Ataxx Game',
            font_size=dp(32),
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(title)

        # Content layout
        content = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )

        # Game mode selection
        content.add_widget(Label(text='Game Mode:'))
        self.mode_spinner = Spinner(
            text='Player vs Player',
            values=['Player vs Player'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(self.mode_spinner)

        # Time limit selection
        content.add_widget(Label(text='Time Limit:'))
        self.time_spinner = Spinner(
            text='Unlimited',
            values=['Unlimited', '5 minutes', '10 minutes', '15 minutes'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(self.time_spinner)

        # Level selection
        content.add_widget(Label(text='Select Level:'))
        self.level_spinner = Spinner(
            text='Select Level',
            values=self._load_level_names(),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(self.level_spinner)

        main_layout.add_widget(content)

        # Add some spacing
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # Start button
        start_button = Button(
            text='Start Game',
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={'center_x': 0.5}
        )
        start_button.bind(on_press=self.start_game)
        main_layout.add_widget(start_button)

        self.add_widget(main_layout)

    def _load_level_names(self):
        """Load level names from levels.txt"""
        try:
            with open('levels.txt', 'r') as f:
                levels = json.load(f)
                return [level['name'] for level in levels]
        except (FileNotFoundError, json.JSONDecodeError):
            return ['Default Level']

    def _load_selected_level(self):
        """Load the selected level data"""
        try:
            with open('levels.txt', 'r') as f:
                levels = json.load(f)
                return next(level for level in levels 
                          if level['name'] == self.level_spinner.text)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return a default level if file cannot be loaded
            return {
                'name': 'Default Level',
                'size': [7, 7],
                'board': [
                    [1, 0, 0, 0, 0, 0, 2],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [2, 0, 0, 0, 0, 0, 1]
                ]
            }

    def start_game(self, instance):
        """Initialize and start a new game"""
        # Get selected options
        time_limit = None
        if self.time_spinner.text != 'Unlimited':
            time_limit = int(self.time_spinner.text.split()[0])

        # Load selected level
        level_data = self._load_selected_level()
        
        # Initialize game state
        game_screen = self.manager.get_screen('game')
        game_screen.start_new_game(level_data, time_limit)
        
        # Switch to game screen
        self.manager.current = 'game'

    def on_enter(self):
        """Reset selections when entering screen"""
        self.mode_spinner.text = 'Player vs Player'
        self.time_spinner.text = 'Unlimited'
        if self.level_spinner.values:
            self.level_spinner.text = self.level_spinner.values[0]
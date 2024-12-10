from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
import json

class CustomSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown_cls = CustomDropDown

class CustomDropDown(DropDown):
    pass

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize spinner attributes first
        self.mode_spinner = Spinner(
            text='Player vs Player',
            values=['Player vs Player'],
            size_hint=(None, None),
            width=dp(180),
            height=dp(40),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1)
        )

        self.time_spinner = Spinner(
            text='Unlimited',
            values=['Unlimited', '5 minutes', '10 minutes', '15 minutes'],
            size_hint=(None, None),
            width=dp(180),
            height=dp(40),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1)
        )

        # Custom level spinner with delete functionality
        self.level_spinner = CustomSpinner(
            text='Select Level',
            values=self._load_level_names(),
            size_hint=(None, None),
            width=dp(180),
            height=dp(40),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1)
        )
        self.setup_level_spinner()
        
        # Main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(30),
            size_hint=(0.6, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Title
        title = Label(
            text='Ataxx Game',
            font_size=dp(48),
            size_hint_y=None,
            height=dp(80),
            bold=True,
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        main_layout.add_widget(title)

        # Content layout
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint=(None, None),
            width=dp(350),
            height=dp(180),
            pos_hint={'center_x': 0.5}
        )

        # Create rows for configuration options
        for label_text, spinner in [
            ('Game Mode:', self.mode_spinner),
            ('Time Limit:', self.time_spinner),
            ('Select Level:', self.level_spinner)
        ]:
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(20),
                size_hint_x=None,
                width=dp(350)
            )
            
            label = Label(
                text=label_text,
                size_hint=(None, None),
                width=dp(120),
                height=dp(40),
                font_size=dp(18),
                halign='right',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            
            row.add_widget(label)
            row.add_widget(Widget(size_hint_x=None, width=dp(10)))
            row.add_widget(spinner)
            content.add_widget(row)

        main_layout.add_widget(Widget(size_hint_y=0.1))
        main_layout.add_widget(content)
        main_layout.add_widget(Widget(size_hint_y=0.1))

        # Start button
        start_button = Button(
            text='Start Game',
            size_hint=(None, None),
            size=(dp(180), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            font_size=dp(20)
        )
        start_button.bind(on_press=self.start_game)
        main_layout.add_widget(start_button)

        # Add editor button
        editor_button = Button(
            text='Level Editor',
            size_hint=(None, None),
            size=(dp(180), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),
            font_size=dp(20)
        )
        editor_button.bind(on_press=self.open_editor)
        main_layout.add_widget(editor_button)

        # Wrapper layout
        wrapper_layout = BoxLayout(
            orientation='horizontal',
            padding=dp(20)
        )
        wrapper_layout.add_widget(Widget(size_hint_x=0.1))
        wrapper_layout.add_widget(main_layout)
        wrapper_layout.add_widget(Widget(size_hint_x=0.1))

        self.add_widget(wrapper_layout)

    def setup_level_spinner(self):
        dropdown = self.level_spinner.dropdown_cls(
            auto_width=False,
            width=dp(220)
        )
        
        levels = self._load_all_levels()
        for level in levels:
            btn = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(2)
            )
            
            level_btn = Button(
                text=level['name'],
                size_hint_x=0.85,
                background_normal='',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1)
            )
            
            btn.add_widget(level_btn)
            
            if level['name'].startswith('Custom Level'):
                delete_btn = Button(
                    text='×',
                    size_hint_x=0.15,
                    size_hint_y=1,
                    background_normal='',
                    background_color=(0.7, 0.2, 0.2, 1),
                    color=(1, 1, 1, 1)
                )
                delete_btn.level_name = level['name']
                delete_btn.bind(on_release=self.delete_level)
                btn.add_widget(delete_btn)
            
            level_btn.bind(on_release=lambda btn=level_btn: self.select_level(btn.text))
            dropdown.add_widget(btn)
        
        self.level_spinner.dropdown = dropdown

    def select_level(self, level_name):
        self.level_spinner.text = level_name
        self.level_spinner.is_open = False

    def delete_level(self, instance):
        level_name = instance.level_name
        try:
            with open('levels.txt', 'r') as f:
                levels = json.load(f)
            
            levels = [level for level in levels if level['name'] != level_name]
            
            with open('levels.txt', 'w') as f:
                json.dump(levels, f, indent=4)
            
            self.level_spinner.values = self._load_level_names()
            self.setup_level_spinner()
            if self.level_spinner.values:
                self.level_spinner.text = self.level_spinner.values[0]
            
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _load_all_levels(self):
        try:
            with open('levels.txt', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [self._get_default_level()]

    def _load_level_names(self):
        levels = self._load_all_levels()
        return [level['name'] for level in levels]

    def _get_default_level(self):
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

    def _load_selected_level(self):
        levels = self._load_all_levels()
        try:
            return next(level for level in levels 
                       if level['name'] == self.level_spinner.text)
        except StopIteration:
            return self._get_default_level()

    def start_game(self, instance):
        time_limit = None
        if self.time_spinner.text != 'Unlimited':
            time_limit = int(self.time_spinner.text.split()[0])

        level_data = self._load_selected_level()
        
        game_screen = self.manager.get_screen('game')
        game_screen.reset_game()
        game_screen.start_new_game(level_data, time_limit)
        
        self.manager.current = 'game'

    def on_enter(self):
        self.mode_spinner.text = 'Player vs Player'
        self.time_spinner.text = 'Unlimited'
        self.level_spinner.values = self._load_level_names()
        self.setup_level_spinner()
        if self.level_spinner.values:
            self.level_spinner.text = self.level_spinner.values[0]
            
    def open_editor(self, instance):
        self.manager.current = 'editor'
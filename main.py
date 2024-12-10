#!/usr/bin/env python
from utils.kivy_config_helper import config_kivy

# Initialize with fixed window size and ensure this comes before other Kivy imports
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
config_kivy(WINDOW_WIDTH, WINDOW_HEIGHT)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

# Import screens
from ui.start_screen import StartScreen
from ui.game_screen import GameScreen
from ui.end_screen import EndScreen

class AtaxxApp(App):
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(EndScreen(name='end'))
        return sm

if __name__ == '__main__':
    AtaxxApp().run()
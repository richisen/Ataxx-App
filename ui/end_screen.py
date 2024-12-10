from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.widget import Widget

class EndScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout with reduced width for more contained look
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(30),
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Add top spacing
        main_layout.add_widget(Widget(size_hint_y=0.2))
        
        # Content layout for centered text
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(200),
            pos_hint={'center_x': 0.5}
        )
        
        # Game over title with improved styling
        self.title_label = Label(
            text='Game Over!',
            font_size=dp(48),
            size_hint_y=None,
            height=dp(80),
            bold=True,
            halign='center',
            valign='middle'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        content_layout.add_widget(self.title_label)
        
        # Winner announcement with improved styling
        self.winner_label = Label(
            text='',
            font_size=dp(32),
            size_hint_y=None,
            height=dp(60),
            bold=True,
            halign='center',
            valign='middle'
        )
        self.winner_label.bind(size=self.winner_label.setter('text_size'))
        content_layout.add_widget(self.winner_label)
        
        # Final score with improved styling
        self.score_label = Label(
            text='',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        self.score_label.bind(size=self.score_label.setter('text_size'))
        content_layout.add_widget(self.score_label)
        
        main_layout.add_widget(content_layout)
        
        # Add flexible space
        main_layout.add_widget(Widget(size_hint_y=0.3))
        
        # Return message with improved styling
        self.return_label = Label(
            text='Returning to start screen...',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle',
            opacity=0.7  # Slightly transparent
        )
        self.return_label.bind(size=self.return_label.setter('text_size'))
        main_layout.add_widget(self.return_label)
        
        # Add bottom spacing
        main_layout.add_widget(Widget(size_hint_y=0.1))
        
        # Wrapper layout to center everything
        wrapper_layout = BoxLayout(
            orientation='horizontal',
            padding=dp(20)
        )
        wrapper_layout.add_widget(Widget(size_hint_x=0.1))
        wrapper_layout.add_widget(main_layout)
        wrapper_layout.add_widget(Widget(size_hint_x=0.1))
        
        self.add_widget(wrapper_layout)

    def on_pre_enter(self):
        """Called just before the screen is displayed"""
        # Get game state from previous screen
        game_screen = self.manager.get_screen('game')
        game_state = game_screen.game_state
        
        if not game_state:
            return
            
        # Get piece counts
        p1_count, p2_count = game_state.board.get_piece_counts()
        
        # Update winner text
        if game_state.winner == 1:
            self.winner_label.text = 'Player 1 Wins!'
        elif game_state.winner == 2:
            self.winner_label.text = 'Player 2 Wins!'
        else:
            self.winner_label.text = "It's a Draw!"
            
        # If game ended due to time
        if game_state.time_limit and (game_state.player1_time <= 0 or game_state.player2_time <= 0):
            self.winner_label.text = 'Player 2 Wins by Time!' if game_state.player1_time <= 0 else 'Player 1 Wins by Time!'
        
        # Update score
        self.score_label.text = f'Final Score - Player 1: {p1_count} | Player 2: {p2_count}'
        
        # Schedule return to start screen after 7 seconds
        Clock.schedule_once(self.return_to_start, 7)

    def return_to_start(self, dt):
        """Return to the start screen"""
        game_screen = self.manager.get_screen('game')
        game_screen.reset_game()
        self.manager.current = 'start'

    def on_leave(self):
        """Called when leaving the screen"""
        self.winner_label.text = ''
        self.score_label.text = ''
        Clock.unschedule(self.return_to_start)
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class EndScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )
        
        # Game over title
        self.title_label = Label(
            text='Game Over!',
            font_size=dp(36),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(self.title_label)
        
        # Winner announcement
        self.winner_label = Label(
            text='',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.winner_label)
        
        # Final score
        self.score_label = Label(
            text='',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.score_label)
        
        # Add some spacing
        layout.add_widget(Label(size_hint_y=0.4))  # Flexible space
        
        # Return to start message
        self.return_label = Label(
            text='Returning to start screen...',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.return_label)
        
        self.add_widget(layout)

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
        # Reset game state before switching screens
        game_screen = self.manager.get_screen('game')
        game_screen.reset_game()  # Use the new reset method
        self.manager.current = 'start'

    def on_leave(self):
        """Called when leaving the screen"""
        # Reset labels for next time
        self.winner_label.text = ''
        self.score_label.text = ''
        # Unschedule any pending callbacks
        Clock.unschedule(self.return_to_start)
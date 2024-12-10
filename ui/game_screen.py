from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.metrics import dp
from game.game_state import GameState

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical')
        
        # Info bar at top
        self.info_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=dp(10)
        )
        
        # Player 1 info
        self.p1_box = BoxLayout(orientation='vertical')
        self.p1_score = Label(text='Player 1: 2')
        self.p1_time = Label(text='--:--')
        self.p1_box.add_widget(self.p1_score)
        self.p1_box.add_widget(self.p1_time)
        self.info_bar.add_widget(self.p1_box)
        
        # Center spacer
        self.info_bar.add_widget(Widget())
        
        # Player 2 info
        self.p2_box = BoxLayout(orientation='vertical')
        self.p2_score = Label(text='Player 2: 2')
        self.p2_time = Label(text='--:--')
        self.p2_box.add_widget(self.p2_score)
        self.p2_box.add_widget(self.p2_time)
        self.info_bar.add_widget(self.p2_box)
        
        self.layout.add_widget(self.info_bar)
        
        # Game board
        self.board_widget = BoardWidget(game_screen=self)
        self.layout.add_widget(self.board_widget)
        
        self.add_widget(self.layout)
        
        # Load sound effects
        self.sound_move = SoundLoader.load('assets/sounds/move.wav')
        self.sound_jump = SoundLoader.load('assets/sounds/jump.wav')
        self.sound_capture = SoundLoader.load('assets/sounds/capture.wav')
        self.sound_game_end = SoundLoader.load('assets/sounds/game_end.wav')
        
        self.game_state = None
        
        # Start update clock
        Clock.schedule_interval(self.update, 1.0/60.0)

    def reset_game(self):
        """Reset the game screen state"""
        self.game_state = None
        self.board_widget.game_state = None
        self.board_widget.clear_board()
        self.p1_time.text = '--:--'
        self.p2_time.text = '--:--'
        self.p1_score.text = 'Player 1: 2'
        self.p2_score.text = 'Player 2: 2'

    def start_new_game(self, level_data, time_limit):
        """Initialize a new game"""
        self.game_state = GameState()
        self.game_state.start_new_game(level_data, 'pvp', time_limit)
        self.board_widget.game_state = self.game_state
        self._update_labels()
        self.board_widget._update_board()

    def update(self, dt):
        """Update game state and UI"""
        if not self.game_state:
            return
            
        self.game_state.update_time(dt)
        self._update_labels()
        
        if self.game_state.is_game_over and not self.manager.current == 'end':
            self.sound_game_end.play()
            Clock.schedule_once(lambda dt: self.show_game_end(), 1.5)

    def _update_labels(self):
        """Update score and time labels"""
        p1_count, p2_count = self.game_state.board.get_piece_counts()
        self.p1_score.text = f'Player 1: {p1_count}'
        self.p2_score.text = f'Player 2: {p2_count}'
        
        if self.game_state.time_limit:
            time1, time2 = self.game_state.get_current_time()
            self.p1_time.text = time1
            self.p2_time.text = time2

    def show_game_end(self):
        """Switch to end screen"""
        self.manager.current = 'end'

class BoardWidget(Widget):
    def __init__(self, game_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.game_state = None
        self.bind(pos=self._update_board, size=self._update_board)
        self.size_hint = (1, 1)

    def clear_board(self):
        """Clear the board state"""
        self.game_state = None
        self.canvas.clear()
        self._update_board()

    def _update_board(self, *args):
        """Update the board display"""
        self.canvas.clear()
        
        # Calculate board dimensions
        self.cell_size = min(self.width, self.height) / 7
        board_width = self.cell_size * 7
        board_height = self.cell_size * 7
        x_offset = (self.width - board_width) / 2
        y_offset = (self.height - board_height) / 2
        
        with self.canvas:
            # Draw board background
            Color(0.8, 0.8, 0.8)
            Rectangle(pos=(self.pos[0] + x_offset, self.pos[1] + y_offset), 
                     size=(board_width, board_height))
            
            # Draw grid lines
            Color(0.3, 0.3, 0.3)
            for i in range(8):
                Line(points=[
                    self.pos[0] + x_offset + i * self.cell_size,
                    self.pos[1] + y_offset,
                    self.pos[0] + x_offset + i * self.cell_size,
                    self.pos[1] + y_offset + board_height
                ])
                Line(points=[
                    self.pos[0] + x_offset,
                    self.pos[1] + y_offset + i * self.cell_size,
                    self.pos[0] + x_offset + board_width,
                    self.pos[1] + y_offset + i * self.cell_size
                ])

        # If there's no game state, stop here
        if not self.game_state:
            return
            
        # Draw pieces and obstacles
        with self.canvas:
            for x in range(7):
                for y in range(7):
                    piece = self.game_state.board.board[x][y]
                    if piece == 9:  # Untraversable cell
                        Color(0.3, 0.3, 0.3)  # Dark gray for obstacles
                        Rectangle(
                            pos=(
                                self.pos[0] + x_offset + x * self.cell_size,
                                self.pos[1] + y_offset + y * self.cell_size
                            ),
                            size=(self.cell_size, self.cell_size)
                        )
                    elif piece in [1, 2]:  # Player pieces
                        if piece == 1:
                            Color(0.9, 0.1, 0.1)  # Red for player 1
                        else:
                            Color(0.1, 0.1, 0.9)  # Blue for player 2
                            
                        Ellipse(
                            pos=(
                                self.pos[0] + x_offset + x * self.cell_size + self.cell_size * 0.1,
                                self.pos[1] + y_offset + y * self.cell_size + self.cell_size * 0.1
                            ),
                            size=(self.cell_size * 0.8, self.cell_size * 0.8)
                        )
            
            # Highlight selected piece
            if self.game_state.selected_piece:
                x, y = self.game_state.selected_piece
                Color(1, 1, 0, 0.3)
                Rectangle(
                    pos=(
                        self.pos[0] + x_offset + x * self.cell_size,
                        self.pos[1] + y_offset + y * self.cell_size
                    ),
                    size=(self.cell_size, self.cell_size)
                )
                
            # Highlight valid moves
            Color(0, 1, 0, 0.3)
            for move in self.game_state.valid_moves:
                x, y = move
                Rectangle(
                    pos=(
                        self.pos[0] + x_offset + x * self.cell_size,
                        self.pos[1] + y_offset + y * self.cell_size
                    ),
                    size=(self.cell_size, self.cell_size)
                )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or not self.game_state:
            return False
            
        board_width = self.cell_size * 7
        board_height = self.cell_size * 7
        x_offset = (self.width - board_width) / 2
        y_offset = (self.height - board_height) / 2
        
        board_x = int((touch.x - self.pos[0] - x_offset) // self.cell_size)
        board_y = int((touch.y - self.pos[1] - y_offset) // self.cell_size)
        
        if not (0 <= board_x < 7 and 0 <= board_y < 7):
            return False
            
        pos = (board_x, board_y)
        
        if not self.game_state.selected_piece:
            if self.game_state.select_piece(pos):
                self._update_board()
            return True
            
        if pos in self.game_state.valid_moves:
            from_pos = self.game_state.selected_piece
            dx = abs(from_pos[0] - pos[0])
            dy = abs(from_pos[1] - pos[1])
            is_jump = dx > 1 or dy > 1
            
            converted = self.game_state.make_move(self.game_state.selected_piece, pos)
            
            if is_jump:
                self.game_screen.sound_jump.play()
            else:
                self.game_screen.sound_move.play()
                
            if converted:
                self.game_screen.sound_capture.play()
            
            if self.game_state.is_game_over:
                self.game_screen.sound_game_end.play()
                Clock.schedule_once(lambda dt: self.game_screen.show_game_end(), 1.5)
                
            self._update_board()
            return True
            
        self.game_state.selected_piece = None
        self.game_state.valid_moves = []
        self._update_board()
        return True
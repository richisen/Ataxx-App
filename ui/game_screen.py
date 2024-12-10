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
        self.board_widget = BoardWidget()
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

    def start_new_game(self, level_data, time_limit):
        """Initialize a new game"""
        self.game_state = GameState()
        self.game_state.start_new_game(level_data, 'pvp', time_limit)
        self.board_widget.game_state = self.game_state
        self._update_labels()

    def update(self, dt):
        """Update game state and UI"""
        if not self.game_state:
            return
            
        self.game_state.update_time(dt)
        self._update_labels()
        
        if self.game_state.is_game_over:
            self.sound_game_end.play()
            # Short delay before showing end screen
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = None
        self.bind(pos=self._update_board, size=self._update_board)
        self.cell_size = dp(50)  # Will be recalculated based on widget size

    def _update_board(self, *args):
        """Redraw the entire board"""
        if not self.game_state:
            return

        self.canvas.clear()
        
        # Calculate cell size based on widget size
        self.cell_size = min(self.width, self.height) / 7
        
        with self.canvas:
            # Draw board background
            Color(0.2, 0.5, 0.3, 1)  # Dark green background
            Rectangle(pos=self.pos, size=self.size)
            
            # Draw grid and pieces
            for row in range(7):
                for col in range(7):
                    self._draw_cell(row, col)
            
            # Draw valid moves if a piece is selected
            if self.game_state.selected_piece:
                self._draw_valid_moves()

    def _draw_cell(self, row, col):
        """Draw a single cell and its contents"""
        x = self.pos[0] + col * self.cell_size
        y = self.pos[1] + row * self.cell_size
        
        with self.canvas:
            # Cell background
            Color(0.3, 0.6, 0.4, 1)
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))
            
            # Grid lines
            Color(0.2, 0.2, 0.2, 1)
            Line(rectangle=(x, y, self.cell_size, self.cell_size))
            
            # Draw piece if present
            cell_value = self.game_state.board.board[row][col]
            if cell_value == 1:  # Player 1
                Color(0.8, 0.2, 0.2, 1)  # Red
                Ellipse(pos=(x + self.cell_size*0.1, y + self.cell_size*0.1),
                       size=(self.cell_size*0.8, self.cell_size*0.8))
            elif cell_value == 2:  # Player 2
                Color(0.2, 0.2, 0.8, 1)  # Blue
                Ellipse(pos=(x + self.cell_size*0.1, y + self.cell_size*0.1),
                       size=(self.cell_size*0.8, self.cell_size*0.8))
            elif cell_value == 9:  # Obstacle
                Color(0.3, 0.3, 0.3, 1)  # Dark gray
                Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

    def _draw_valid_moves(self):
        """Highlight valid moves for selected piece"""
        with self.canvas:
            Color(1, 1, 0, 0.3)  # Semi-transparent yellow
            for move in self.game_state.valid_moves:
                x = self.pos[0] + move[1] * self.cell_size
                y = self.pos[1] + move[0] * self.cell_size
                Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

    def _board_to_widget_pos(self, row, col):
        """Convert board coordinates to widget coordinates"""
        return (self.pos[0] + col * self.cell_size,
                self.pos[1] + row * self.cell_size)

    def _widget_to_board_pos(self, x, y):
        """Convert widget coordinates to board coordinates"""
        board_x = int((x - self.pos[0]) // self.cell_size)
        board_y = int((y - self.pos[1]) // self.cell_size)
        if 0 <= board_x < 7 and 0 <= board_y < 7:
            return board_y, board_x  # Return row, col
        return None

    def on_touch_down(self, touch):
        """Handle touch events"""
        if not self.collide_point(*touch.pos) or not self.game_state:
            return False

        board_pos = self._widget_to_board_pos(*touch.pos)
        if not board_pos:
            return False

        row, col = board_pos
        
        # If a piece is already selected
        if self.game_state.selected_piece:
            if (row, col) in self.game_state.valid_moves:
                # Make the move
                is_jump = max(abs(row - self.game_state.selected_piece[0]),
                            abs(col - self.game_state.selected_piece[1])) > 1
                
                converted = self.game_state.make_move(
                    self.game_state.selected_piece,
                    (row, col)
                )
                
                # Play appropriate sound
                if is_jump:
                    self.parent.sound_jump.play()
                else:
                    self.parent.sound_move.play()
                
                if converted:
                    self.parent.sound_capture.play()
                
                # Animate the move
                self._animate_move(self.game_state.selected_piece, (row, col), converted)
                
            self.game_state.selected_piece = None
            self.game_state.valid_moves = []
            
        else:
            # Try to select a piece
            if self.game_state.select_piece((row, col)):
                pass  # Piece selected successfully
        
        self._update_board()
        return True

    def _animate_move(self, from_pos, to_pos, converted):
        """Animate piece movement and captures"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Calculate screen positions
        start_x, start_y = self._board_to_widget_pos(from_row, from_col)
        end_x, end_y = self._board_to_widget_pos(to_row, to_col)
        
        # Create moving piece animation
        with self.canvas:
            Color(0.8, 0.2, 0.2, 1) if self.game_state.current_player == 1 else Color(0.2, 0.2, 0.8, 1)
            piece = Ellipse(pos=(start_x + self.cell_size*0.1, start_y + self.cell_size*0.1),
                          size=(self.cell_size*0.8, self.cell_size*0.8))
        
        # Moving animation
        move_anim = Animation(pos=(end_x + self.cell_size*0.1, end_y + self.cell_size*0.1),
                            duration=0.3, t='out_quad')
        
        # For converted pieces, create scaling animations
        for conv_row, conv_col in converted:
            conv_x, conv_y = self._board_to_widget_pos(conv_row, conv_col)
            with self.canvas:
                Color(0.8, 0.2, 0.2, 1) if self.game_state.current_player == 1 else Color(0.2, 0.2, 0.8, 1)
                conv_piece = Ellipse(pos=(conv_x + self.cell_size*0.1, conv_y + self.cell_size*0.1),
                                   size=(self.cell_size*0.8, self.cell_size*0.8))
                
                anim = Animation(size=(self.cell_size*0.4, self.cell_size*0.4), duration=0.15) + \
                      Animation(size=(self.cell_size*0.8, self.cell_size*0.8), duration=0.15)
                anim.start(conv_piece)
        
        # Start the main piece movement animation
        move_anim.start(piece)
        
        # Schedule a board update after animations complete
        Clock.schedule_once(lambda dt: self._update_board(), 0.3)
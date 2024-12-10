from typing import Optional, Tuple
from .board import Board

class GameState:
    def __init__(self):
        """Initialize game state with default values"""
        self.board = Board()
        self.current_player = 1  # 1 or 2
        self.time_limit = None  # in minutes
        self.player1_time = 0  # in seconds
        self.player2_time = 0  # in seconds
        self.game_mode = 'pvp'
        self.is_game_over = False
        self.winner = None
        self.selected_piece = None
        self.valid_moves = []

    def start_new_game(self, level_data: dict, game_mode: str, time_limit: Optional[int]):
        """Initialize a new game with the given parameters"""
        self.board.load_from_json(level_data)
        self.game_mode = game_mode
        self.time_limit = time_limit
        if time_limit:
            self.player1_time = time_limit * 60  # Convert minutes to seconds
            self.player2_time = time_limit * 60
        self.current_player = 1
        self.is_game_over = False
        self.winner = None
        self.selected_piece = None
        self.valid_moves = []

    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> list:
        """Execute a move and handle game state changes"""
        if to_pos not in self.valid_moves:  # Changed from from_pos to to_pos
            return []
            
        converted = self.board.make_move(from_pos, to_pos, self.current_player)
        self.selected_piece = None
        self.valid_moves = []
        
        # Check game end conditions
        self.check_game_over()
        
        if not self.is_game_over:
            self.current_player = 3 - self.current_player  # Switch between 1 and 2
            
        return converted

    def update_time(self, dt: float):
        """Update game timer"""
        if not self.time_limit or self.is_game_over:
            return
        
        if self.current_player == 1:
            self.player1_time -= dt
            if self.player1_time <= 0:
                self.is_game_over = True
                self.winner = 2
        else:
            self.player2_time -= dt
            if self.player2_time <= 0:
                self.is_game_over = True
                self.winner = 1

    def check_game_over(self):
        """Check if the game has ended"""
        if not self.board.has_valid_moves(1) and not self.board.has_valid_moves(2):
            self.is_game_over = True
            p1_count, p2_count = self.board.get_piece_counts()
            if p1_count > p2_count:
                self.winner = 1
            elif p2_count > p1_count:
                self.winner = 2
            else:
                self.winner = 0  # Draw

    def select_piece(self, pos: Tuple[int, int]) -> bool:
        """Select a piece and calculate valid moves"""
        x, y = pos  # Using x,y consistently
        if self.board.board[x][y] == self.current_player:
            self.selected_piece = pos
            self.valid_moves = self.board.get_valid_moves(pos)
            return True
        return False

    def get_current_time(self) -> Tuple[str, str]:
        """Get formatted time strings for both players"""
        def format_time(seconds):
            minutes = int(seconds) // 60
            secs = int(seconds) % 60
            return f"{minutes:02d}:{secs:02d}"
            
        time1 = format_time(self.player1_time)
        time2 = format_time(self.player2_time)
        return time1, time2
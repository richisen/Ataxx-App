from typing import Optional, Tuple
from .board import Board

class GameState:
    def __init__(self):
        """Initialize game state with default values"""
        self.reset_state()
        
    def reset_state(self):
        """Reset all game state variables"""
        self.board = Board()
        self.current_player = 1
        self.time_limit = None
        self.player1_time = 0
        self.player2_time = 0
        self.game_mode = 'pvp'
        self.is_game_over = False
        self.winner = None
        self.selected_piece = None
        self.valid_moves = []

    def start_new_game(self, level_data: dict, game_mode: str, time_limit: Optional[int]):
        """Initialize a new game with the given parameters"""
        self.reset_state()  # Reset all state first
        self.board.load_from_json(level_data)
        self.game_mode = game_mode
        self.time_limit = time_limit
        if time_limit:
            self.player1_time = time_limit * 60
            self.player2_time = time_limit * 60

    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> list:
        """Execute a move and handle game state changes"""
        if to_pos not in self.valid_moves:
            return []
            
        converted = self.board.make_move(from_pos, to_pos, self.current_player)
        self.selected_piece = None
        self.valid_moves = []
        
        # Check game end conditions and get move availability
        p1_has_moves, p2_has_moves = self.check_game_over()
        
        if not self.is_game_over:
            # Get current piece counts
            p1_count, p2_count = self.board.get_piece_counts()
            
            # Determine if turn should switch
            if self.current_player == 1:
                # Switch to player 2 if they have moves
                if p2_has_moves:
                    self.current_player = 2
            else:  # Player 2
                # Switch to player 1 if they have moves
                if p1_has_moves:
                    self.current_player = 1
                
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
        p1_count, p2_count = self.board.get_piece_counts()
        
        # If either player has 0 pieces, game is immediately over
        if p1_count == 0:
            self.is_game_over = True
            self.winner = 2
            return False, False
        elif p2_count == 0:
            self.is_game_over = True
            self.winner = 1
            return False, False
            
        # Check if each player has valid moves
        p1_has_moves = self.board.has_valid_moves(1)
        p2_has_moves = self.board.has_valid_moves(2)
        
        # If both players have no moves, end game
        if not p1_has_moves and not p2_has_moves:
            self.is_game_over = True
            if p1_count > p2_count:
                self.winner = 1
            elif p2_count > p1_count:
                self.winner = 2
            else:
                self.winner = 0  # Draw
                
        return p1_has_moves, p2_has_moves

    def select_piece(self, pos: Tuple[int, int]) -> bool:
        """Select a piece and calculate valid moves"""
        x, y = pos
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
from typing import List, Tuple, Optional
import json

class Board:
    def __init__(self, size: Tuple[int, int] = (7, 7)):
        self.size = size
        self.board = [[0 for _ in range(size[1])] for _ in range(size[0])]
        self.selected_piece = None

    def load_from_json(self, board_data: dict):
        """Load board configuration from JSON data"""
        self.board = board_data['board']
        self.size = tuple(board_data['size'])

    def get_valid_moves(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return list of valid moves for a piece at given position"""
        valid_moves = []
        x, y = pos  # Using x,y consistently
        
        # Check adjacent cells (clone moves)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if self._is_valid_position((new_x, new_y)) and self.board[new_x][new_y] == 0:
                    valid_moves.append((new_x, new_y))

        # Check jump moves (two cells away)
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if abs(dx) <= 1 and abs(dy) <= 1:
                    continue
                if abs(dx) > 2 or abs(dy) > 2:
                    continue
                new_x, new_y = x + dx, y + dy
                if self._is_valid_position((new_x, new_y)) and self.board[new_x][new_y] == 0:
                    valid_moves.append((new_x, new_y))

        return valid_moves

    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], player: int) -> List[Tuple[int, int]]:
        """Execute a move and return list of converted pieces"""
        converted_pieces = []
        fx, fy = from_pos  # Using x,y consistently
        tx, ty = to_pos
        
        # Determine if this is a jump or clone move
        is_jump = max(abs(tx - fx), abs(ty - fy)) > 1
        
        # Make the move
        if is_jump:
            self.board[fx][fy] = 0
        self.board[tx][ty] = player
        
        # Convert adjacent pieces
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = tx + dx, ty + dy
                if self._is_valid_position((new_x, new_y)) and self.board[new_x][new_y] == (3 - player):
                    self.board[new_x][new_y] = player
                    converted_pieces.append((new_x, new_y))
        
        return converted_pieces

    def _is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if a position is valid and traversable on the board"""
        x, y = pos  # Using x,y consistently
        return (0 <= x < self.size[0] and 
                0 <= y < self.size[1] and 
                self.board[x][y] != 9)  # 9 indicates untraversable cell

    def get_piece_counts(self) -> Tuple[int, int]:
        """Return the count of pieces for each player"""
        count_1 = sum(row.count(1) for row in self.board)
        count_2 = sum(row.count(2) for row in self.board)
        return count_1, count_2

    def has_valid_moves(self, player: int) -> bool:
        """Check if a player has any valid moves available"""
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if self.board[x][y] == player and self.get_valid_moves((x, y)):
                    return True
        return False
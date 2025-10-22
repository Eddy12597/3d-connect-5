from stack import Stack
from collections import deque
import functools

class Side:
    WHITE = True
    BLACK = False


class Piece:
    def __init__(self, side: str | bool, x: int, y: int, z: int | None = None, id: int = -1) -> None:
        self.id = id
        self.x = x
        self.y = y
        
        if isinstance(z, int) and z < 0:
            raise RuntimeError(f"z is below 0 for piece {self.id}")
        self.z = z
        
        if isinstance(side, bool):
            self.side = side
        else:
            self.side = side.lower().strip()[0] == "w"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Piece):
            return False
        return (self.x == other.x and self.y == other.y and 
                self.z == other.z and self.side == other.side)
    
    def __repr__(self) -> str:
        side_str = "White" if self.side else "Black"
        return f"Piece({side_str}, ({self.x}, {self.y}, {self.z}), id={self.id})"


class Board:
    def __init__(self, xrad: int = 9, yrad: int = 9, maxh: int = 50, list_pieces: list[Piece] | None = None) -> None:
        self.xrad = xrad
        self.yrad = yrad
        self.maxh = maxh
        self.list_pieces: list[Piece] = list_pieces or []
        
        # Create grid with stacks
        self.grid: list[list[Stack[Piece]]] = [
            [Stack[Piece]() for _ in range(2 * yrad + 1)] 
            for _ in range(2 * xrad + 1)
        ]
        self.place_list(self.list_pieces)
    
    def place_list(self, list_pieces: list[Piece]) -> None:
        for piece in list_pieces:
            self.place(piece)
    
    def place(self, p: Piece) -> None:
        x, y = p.x, p.y
        if not (-self.xrad <= x <= self.xrad and -self.yrad <= y <= self.yrad):
            raise IndexError(f"Position ({x}, {y}) is out of bounds")
        
        z = self.grid[self.xrad + x][self.yrad + y].size()
        if z >= self.maxh:
            raise RuntimeError("Maximum Height Reached!")
        
        p.z = z
        self.grid[self.xrad + x][self.yrad + y].push(p)
        self.list_pieces.append(p)
    
    def __getitem__(self, coord: tuple[int, int, int]) -> Piece | None:
        x, y, z = coord
        if not (-self.xrad <= x <= self.xrad and -self.yrad <= y <= self.yrad):
            raise IndexError(f"Position ({x}, {y}) is out of bounds")
        
        stack = self.grid[self.xrad + x][self.yrad + y]
        if z < 0 or z >= stack.size():
            return None
        return stack.tolist()[z]
    
    def get_top_piece(self, x: int, y: int) -> Piece | None:
        if not (-self.xrad <= x <= self.xrad and -self.yrad <= y <= self.yrad):
            return None
        
        stack = self.grid[self.xrad + x][self.yrad + y]
        return stack.top() if stack.size() > 0 else None
    
    def check_single(self, piece: Piece, win_len: int = 5) -> bool:
        if piece.z is None:
            return False
        
        # 26 possible directions in 3D space (combinations of -1, 0, 1 excluding (0,0,0))
        directions = [
            (dx, dy, dz) 
            for dx in (-1, 0, 1) 
            for dy in (-1, 0, 1) 
            for dz in (-1, 0, 1) 
            if (dx, dy, dz) != (0, 0, 0)
        ]
        
        for dx, dy, dz in directions:
            count = 1  # Count the current piece
            
            # Check in positive direction
            for i in range(1, win_len):
                nx, ny, nz = piece.x + i * dx, piece.y + i * dy, piece.z + i * dz
                if not self._is_same_color_at(nx, ny, nz, piece.side):
                    break
                count += 1
            
            # Check in negative direction
            for i in range(1, win_len):
                nx, ny, nz = piece.x - i * dx, piece.y - i * dy, piece.z - i * dz
                if not self._is_same_color_at(nx, ny, nz, piece.side):
                    break
                count += 1
            
            if count >= win_len:
                return True
        
        return False
    
    def _is_same_color_at(self, x: int, y: int, z: int, side: bool) -> bool:
        """Check if there's a piece of the same color at the given position"""
        try:
            target_piece = self[x, y, z]
            return target_piece is not None and target_piece.side == side
        except IndexError:
            return False
    
    @functools.cache
    def check(self, win_len: int = 5) -> tuple[bool, bool]:
        """
        Check if either side has won.
        Returns: (white_won, black_won)
        """
        white_won = False
        black_won = False
        
        # Only check recent pieces for efficiency
        for piece in self.list_pieces[-win_len * 2:]:  # Check last few pieces
            if piece.z is None:
                continue
                
            if self.check_single(piece, win_len):
                if piece.side:
                    white_won = True
                else:
                    black_won = True
        
        return white_won, black_won
    
    def get_winner(self, win_len: int = 5) -> bool | None:
        """Get the winner if there is one, None otherwise"""
        white_won, black_won = self.check(win_len)
        if white_won and black_won:
            # This shouldn't happen in normal play, but handle it
            return None
        elif white_won:
            return Side.WHITE
        elif black_won:
            return Side.BLACK
        else:
            return None
    
    def __repr__(self) -> str:
        return f"Board(xrad={self.xrad}, yrad={self.yrad}, maxh={self.maxh}, pieces={len(self.list_pieces)})"
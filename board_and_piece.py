from colorama import Back, Style, Fore

class Side:
    WHITE = True
    BLACK = False
BOARD_RAD = 3
_idcnt = 0

class Piece:
    def __init__(self, side: str | bool, x: int, y: int, z: int | None = None, i: int = -1) -> None:
        global _idcnt
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
        
        if i == -1:
            i = _idcnt
            _idcnt += 1
        self.id = i
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Piece):
            return False
        return (self.x == other.x and self.y == other.y and 
                self.z == other.z and self.side == other.side)
    def __hash__(self) -> int:
        side_int = 1 if self.side else 0
        z_val = self.z if self.z is not None else -1
        return hash((self.x, self.y, z_val, side_int, self.id))
    
    def __repr__(self) -> str:
        side_str = "White" if self.side else "Black"
        return f"Piece({side_str}, ({self.x}, {self.y}, {self.z}), id={self.id})"


class Board:
    def __init__(self, xrad: int = BOARD_RAD, yrad: int = BOARD_RAD, maxh: int = 50, list_pieces: list[Piece] | None = None, win_len: int = 5) -> None:
        self.status: list[Piece] | None = None
        self.xrad = xrad
        self.yrad = yrad
        self.maxh = maxh
        self.win_len = win_len
        self.list_pieces: list[Piece] = list_pieces or []
        self.last_placed: Piece | None = None
        
        # 2D grid where each cell contains a list of pieces (stack replacement)
        self.grid: list[list[list[Piece]]] = [
            [[] for _ in range(2 * yrad + 1)] 
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
        
        stack = self.grid[self.xrad + x][self.yrad + y]
        if len(stack) >= self.maxh:
            raise RuntimeError("Maximum Height Reached!")
        
        p.z = len(stack)
        stack.append(p)
        self.list_pieces.append(p)
        
        # Update self.status with the winning line if found
        self.status = self.check(self.win_len)
        self.last_placed = p
    
    def __getitem__(self, coord: tuple[int, int, int]) -> Piece | None:
        x, y, z = coord
        if not (-self.xrad <= x <= self.xrad and -self.yrad <= y <= self.yrad):
            raise IndexError(f"Position ({x}, {y}) is out of bounds")
        
        stack = self.grid[self.xrad + x][self.yrad + y]
        if z < 0 or z >= len(stack):
            return None
        return stack[z]
    def _get_piece_at(self, x: int, y: int, z: int) -> Piece | None:
        """Helper method to get piece at coordinates without raising errors"""
        try:
            return self[x, y, z]
        except (IndexError, TypeError):
            return None
    
    def get_top_piece(self, x: int, y: int) -> Piece | None:
        if not (-self.xrad <= x <= self.xrad and -self.yrad <= y <= self.yrad):
            return None
        
        stack = self.grid[self.xrad + x][self.yrad + y]
        return stack[-1] if stack else None
    
    def check_single(self, piece: Piece, win_len: int = 5) -> list[Piece] | None:
        if piece.z is None:
            return None
        
        directions = [
            (dx, dy, dz) 
            for dx in (-1, 0, 1) 
            for dy in (-1, 0, 1) 
            for dz in (-1, 0, 1) 
            if (dx, dy, dz) != (0, 0, 0)
        ]
        
        for dx, dy, dz in directions:
            winning_pieces = [piece]
            
            # Check in positive direction
            for i in range(1, win_len):
                nx, ny, nz = piece.x + i * dx, piece.y + i * dy, piece.z + i * dz
                target_piece = self._get_piece_at(nx, ny, nz)
                if target_piece is None or target_piece.side != piece.side:
                    break
                winning_pieces.append(target_piece)
            
            # Check in negative direction  
            for i in range(1, win_len):
                nx, ny, nz = piece.x - i * dx, piece.y - i * dy, piece.z - i * dz
                target_piece = self._get_piece_at(nx, ny, nz)
                if target_piece is None or target_piece.side != piece.side:
                    break
                winning_pieces.append(target_piece)
            
            if len(winning_pieces) >= win_len:
                return winning_pieces
        
        return None
    
    def _is_same_color_at(self, x: int, y: int, z: int, side: bool) -> bool:
        try:
            target_piece = self[x, y, z]
            return target_piece is not None and target_piece.side == side
        except IndexError:
            return False
    
    def check(self, win_len: int = 5) -> list[Piece] | None:
        # Check only recent pieces for efficiency
        for piece in self.list_pieces[-win_len * 2:]:
            if piece.z is None:
                continue
                
            winning_line = self.check_single(piece, win_len)
            if winning_line:
                return winning_line
        
        return None
    
    # def get_winner(self, win_len: int = 5) -> bool | None:
    #     white_won, black_won = self.check(win_len)
    #     if white_won and black_won:
    #         return None
    #     elif white_won:
    #         return Side.WHITE
    #     elif black_won:
    #         return Side.BLACK
    #     else:
    #         return None
    
    def __repr__(self) -> str:
        return f"Board(xrad={self.xrad}, yrad={self.yrad}, maxh={self.maxh}, pieces={len(self.list_pieces)})"
    
    def __str__(self) -> str:
        stats = f"\n---\nGAME BOARD - Radius: ({self.xrad}, {self.yrad}), Pieces: {len(self.list_pieces)}\n"
        
        header = "   ║"
        for i in range(-self.xrad, self.xrad + 1):
            header += f"{i:^3}"
        
        board = "╔═══" + "═" * (len(header)-1) + "╗\n"
        board += "║ " + header + " ║\n"
        board += "║ " + "═" * (len(header)) +" ║\n"
                
        for y in range(-self.yrad, self.yrad + 1):
            board += "║ "
            board += f"{y:^3}║"
            for x in range(-self.xrad, self.xrad + 1):
                cell_stack = self.grid[x + self.xrad][y + self.yrad]
                cell_value = len(cell_stack)
                if cell_value == 1:
                    cell_value = f"{f" {Back.WHITE}{Fore.BLACK}W{Style.RESET_ALL}":^3} " if cell_stack[0].side else f"{f" {Back.BLUE}{Fore.WHITE}B{Style.RESET_ALL}":^3} "
                elif cell_value != 0:
                    cell_value = f" {Back.GREEN}{Fore.WHITE}{cell_value}{Style.RESET_ALL} "
                board += f"{cell_value:^3}"
            board += " ║\n"
        
        board += "╚═══" + "═" * (len(header)-1) + "╝"
        
        return f"{stats}{board}"
from stack import stack

# z cannot go below 0
class piece:
    def __init__(self, side: str | bool, x: int, y: int, z: int | None = None, id: int = -1) -> None: # white = true
        self.id = id
        self.x = x
        self.y = y
        if type(z) == int and z < 0:
            raise RuntimeError(f"z is below 0 for piece {self.id}")
        self.z = z
        
        if type(side) == bool:
            self.side = side
        else:
            self.side = side.lower().strip()[0] == "w"
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z and self.side == other.side

class board:
    def __init__(self, xrad: int = 9, yrad: int = 9, maxh: int = 50, listPieces: list[piece] | None = None) -> None:
        self.xrad = xrad
        self.yrad = yrad
        self.maxh = maxh
        self.listPieces: list[piece] = listPieces or []
        self.grid: list[list[stack[piece]]] = [
            [
                stack[piece]() for y in range(-yrad, yrad)    
            ] for x in range(-xrad, xrad)
        ]
        self.placeList(self.listPieces)
    
    def placeList(self, listPieces: list[piece]) -> None:
        for p in listPieces:
            self.place(p)
            
    def place(self, p: piece) -> None:
        x = p.x
        y = p.y
        z = self.grid[x][y].size()
        if z > self.maxh:
            raise RuntimeError("Maximum Height Reached!")
        p.z = z
        self.grid[x][y].push(p)
# gui.py
from ursina import *
from ursina.color import rgb
import queue
from board_and_piece import *

# thread-safe queue for events (filled from your CLI thread)
event_queue = queue.Queue[dict[str, bool | int | str]]()

# store GUI pieces so references are kept and we can later update/remove them
_gui_pieces = []

# tuning: how board coords map to world coords
BOARD_CELL_SIZE = 0.9     # distance between centers of adjacent cells in world units
BOARD_OFFSET_X = -4.0     # translate board so it's centered / visible
BOARD_OFFSET_Z = -4.0
PIECE_HEIGHT = 0       # vertical offset above the plane

class GUIPiece(Piece):
    def __init__(self, side, x, y, board: Board, z=None, i=-1,):
        """
        side: Side.WHITE or Side.BLACK
        x,y : board coordinates (integers)
        z   : vertical position in stack (0-based)
        """
        super().__init__(side, x, y, z, i)

        # map board coordinates (x,y) to Ursina world coordinates (wx, wy, wz)
        wx = BOARD_OFFSET_X + x * BOARD_CELL_SIZE
        wz = BOARD_OFFSET_Z + y * BOARD_CELL_SIZE
        
        # Use the provided z-coordinate instead of recalculating
        if z is None:
            # Fallback: use current stack height minus 1 (for the piece we're adding)
            z = len(board.grid[self.x][self.y]) - 1
        
        wy = (PIECE_HEIGHT + z) / 4
        
        print(f"Piece {self.id} at ({x}, {y}) placed at height {z}, world Y = {wy}")

        # Create an Entity and store it on the GUIPiece instance
        self.entity = Entity(
            model='models/go.obj',
            color=color.light_gray if side == Side.WHITE else color.dark_gray,
            position=Vec3(wx, wy, wz),
            scale=Vec3(0.4, 0.4, 0.3),
            rotation=Vec3(90, 0, 0)
        )

def _spawn_piece_from_event(event: dict, board):
    # Pass the z-coordinate from the event
    p = GUIPiece(event["side"], event["x"], event["y"], board, event.get("z"))
    _gui_pieces.append(p)  # keep a reference so it isn't GC'd


def update(board: Board):
    """
    Ursina will automatically call this, from main,py's update() wrapper.
    We drain the thread-safe queue filled by the CLI thread and spawn pieces.
    """
    handled = 0
    while not event_queue.empty():
        event = event_queue.get_nowait()
        # print(f"[GUI] processing event: {event}")
        handled += 1
        if event.get("type") == "spawn_piece":
            try:
                _spawn_piece_from_event(event, board)
            except Exception as e:
                print(f"[gui] failed to spawn piece: {e}")
    # if handled:
        # print(f"[gui] handled {handled} events")

def start_gui(xrad: int = 9, yrad: int = 9):
    app = Ursina(development_mode=True)
    
    # camera + lights
    EditorCamera()
    DirectionalLight(y=2, z=3, shadows=False)
    AmbientLight(color=color.rgba(120, 120, 120, 0.5))

    # ground / board plane - CENTERED AT ORIGIN
    ground = Entity(
        model='plane', 
        scale=Vec3(2 * xrad, 1, 2 * yrad), 
        color=color.gray, 
        position=Vec3(0, -0.4, 0)
    )

    sun = DirectionalLight()
    sun.look_at(Vec3(1, -2, -1))
    sun.color = rgb(255, 244, 229) 
    
    AmbientLight(color=rgb(100, 100, 100))

    app.run()
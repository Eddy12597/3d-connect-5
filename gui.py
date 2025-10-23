# gui.py
from ursina import *
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
PIECE_HEIGHT = 0.15       # vertical offset above the plane

class GUIPiece(Piece):
    def __init__(self, side, x, y, z=None, i=-1):
        """
        side: Side.WHITE or Side.BLACK
        x,y : board coordinates (integers)
        z   : optional vertical offset (unused here)
        """
        super().__init__(side, x, y, z, i)

        # map board coordinates (x,y) to Ursina world coordinates (wx, wy, wz)
        wx = BOARD_OFFSET_X + x * BOARD_CELL_SIZE
        wz = BOARD_OFFSET_Z + y * BOARD_CELL_SIZE
        wy = PIECE_HEIGHT

        # Create an Entity and store it on the GUIPiece instance
        self.entity = Entity(
            model='models/go.obj',
            color=color.white if side == Side.WHITE else color.black,
            position=Vec3(wx, wy, wz),
            scale=Vec3(0.6, 0.15, 0.6),   # flattened cylinder to look like a disk
            rotation=Vec3(90, 0, 0)
        )

def _spawn_piece_from_event(event: dict):
    p = GUIPiece(event["side"], event["x"], event["y"])
    _gui_pieces.append(p)  # keep a reference so it isn't GC'd


def start_gui():

    app = Ursina()
    # camera + lights
    EditorCamera()
    DirectionalLight(y=2, z=3, shadows=False)
    AmbientLight(color=color.rgba(120, 120, 120, 0.5))

    # ground / board plane
    ground = Entity(model='plane', scale=Vec3(10, 1, 10), color=color.gray, position=Vec3(0, 0, 0))

    # optional: draw a simple checkerboard visual using quads or multiple Entities
    # (left out for brevity — add if you want a visible board grid)

    app.run()

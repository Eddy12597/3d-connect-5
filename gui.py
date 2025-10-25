# gui.py
from ursina import *
from ursina.color import rgb
import queue
from board_and_piece import *

event_queue = queue.Queue[dict[str, bool | int | str]]()
_gui_pieces = []

# Tuning - centered around origin
BOARD_CELL_SIZE = 0.9
PIECE_HEIGHT = 0

class GUIPiece(Piece):
    def __init__(self, side, x, y, board: Board, z=None, i=-1):
        super().__init__(side, x, y, z, i)

        # Map board (x,y) to world coordinates centered at origin.
        # Keep Y inverted so CLI top/bottom matches Ursina view.
        wx = x * BOARD_CELL_SIZE
        wz = -y * BOARD_CELL_SIZE  # invert y-axis to match CLI orientation

        if z is None:
            z = len(board.grid[self.x][self.y]) - 1

        # tweak vertical placement if your model scale/units differ
        wy = (PIECE_HEIGHT + z) / 4

        # print(f"Piece {self.id} at board({x}, {y}) -> world({wx:.2f}, {wy:.2f}, {wz:.2f})")

        self.entity = Entity(
            model='models/go.obj',
            color=color.light_gray if side == Side.WHITE else color.dark_gray,
            position=Vec3(wx, wy, wz),
            scale=Vec3(0.4, 0.4, 0.3),
            rotation=Vec3(90, 0, 0)
        )

def _spawn_piece_from_event(event: dict, board):
    p = GUIPiece(event["side"], event["x"], event["y"], board, event.get("z"))
    _gui_pieces.append(p)

def update(board: Board):
    handled = 0
    while not event_queue.empty():
        event = event_queue.get_nowait()
        handled += 1
        if event.get("type") == "spawn_piece":
            try:
                _spawn_piece_from_event(event, board)
            except Exception as e:
                print(f"[gui] failed to spawn piece: {e}")

def start_gui(xrad: int = 9, yrad: int = 9):
    app = Ursina(development_mode=False)

    # Calculate board dimensions
    board_width = 2 * xrad + 1
    board_height = 2 * yrad + 1

    # Lighting
    sun = DirectionalLight(
        position=(10, 20, -10),
        rotation=(45, -30, 0),
        shadows=True,
        shadow_map_size=2048,
        color=rgb(255, 245, 235)
    )

    fill_light = DirectionalLight(
        position=(-5, 10, 5),
        rotation=(30, 10, 0),
        shadows=False,
        color=rgb(200, 220, 255)
    )

    AmbientLight(color=color.rgba(110, 110, 110, 0.3))

    # Ground centered at origin. plane model is centered so scale represents half-extent automatically.
    ground_size_x = board_width * BOARD_CELL_SIZE
    ground_size_z = board_height * BOARD_CELL_SIZE

    ground = Entity(
        model='plane',
        scale=Vec3(ground_size_x, 1, ground_size_z),
        color=color.gray,
        position=Vec3(0, -0.4, 0),
        texture='white_cube'
    )

    # Add grid lines with coordinate system matching CLI and centered at origin
    _create_grid_lines(xrad, yrad, BOARD_CELL_SIZE)

    # Optional test markers
    # _add_test_markers(xrad, yrad, BOARD_CELL_SIZE)

    EditorCamera()
    app.run()

def _create_coordinate_labels(xrad, yrad, cell_size):
    """Add coordinate labels to verify the coordinate system matches CLI"""
    # Corners in board coordinates (x, y)
    corners = [
        (-xrad, -yrad, "TL(-x,-y)"),  # Top Left
        (-xrad, yrad, "BL(-x,+y)"),   # Bottom Left
        (xrad, -yrad, "TR(+x,-y)"),   # Top Right
        (xrad, yrad, "BR(+x,+y)")     # Bottom Right
    ]

    for x, y, label in corners:
        wx = x * cell_size
        wz = -y * cell_size  # inverted y
        Text(
            text=label,
            position=(wx, 0.5, wz),
            scale=2,
            color=color.red
        )

def _create_grid_lines(xrad, yrad, cell_size):
    """Add grid lines matching the CLI coordinate system, centered at origin"""
    board_width = 2 * xrad + 1
    board_height = 2 * yrad + 1

    # Vertical lines (constant x)
    start_z = -yrad * cell_size
    end_z   = yrad  * cell_size
    for x in range(-xrad, xrad + 1):
        wx = x * cell_size
        line = Entity(
            model='cube',
            color=color.black if x != 0 else color.green,
            position=Vec3(wx, -0.39, (start_z + end_z) / 2),
            scale=Vec3(0.02, 0.02, (end_z - start_z))
        )

    # Horizontal lines (constant y)
    start_x = -xrad * cell_size
    end_x   =  xrad * cell_size
    for y in range(-yrad, yrad + 1):
        wz = -y * cell_size  # inverted y
        line = Entity(
            model='cube',
            color=color.black if y != 0 else color.green,
            position=Vec3((start_x + end_x) / 2, -0.39, wz),
            scale=Vec3((end_x - start_x), 0.02, 0.02)
        )

def _add_test_markers(xrad, yrad, cell_size):
    """Add test markers at key positions"""
    # Center marker (0,0)
    wx = 0 * cell_size
    wz = 0 * cell_size
    center_marker = Entity(
        model='sphere',
        color=color.red,
        position=Vec3(wx, 0.5, wz),
        scale=0.1 # type: ignore
    )

    # Top-left marker (should be at board (-xrad, -yrad))
    origin_wx = (-xrad) * cell_size
    origin_wz = -(-yrad) * cell_size  # invert y: -(-yrad) => +yrad
    origin_marker = Entity(
        model='cube',
        color=color.blue,
        position=Vec3(origin_wx, 0.5, origin_wz),
        scale=0.1 # type: ignore
    )

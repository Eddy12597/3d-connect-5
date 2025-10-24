import gui
import board_and_piece as game
from colorama import Back, Fore, Style
import threading
from queue import Queue

def test():
    board = game.Board()
    board.place(game.Piece(game.Side.WHITE, 0, 0))
    print(board.status)
    board.place(game.Piece(game.Side.BLACK, 0, 0))
    print(board.status)
    board.place(game.Piece(game.Side.WHITE, 0, 1))
    print(str(board))
    
def parseCommand(board: game.Board, x: str) -> None:
    tokens = x.split(" ")
    if tokens[0] in ("peek", "pk", "p"):
        x = int(input("Enter X (peek): ")) # type: ignore
        y = int(input("Enter Y (peek): ")) # type: ignore
        pk = " ".join([(f"{Back.WHITE}{Fore.BLACK}W{Style.RESET_ALL}" if p.side else f"{Back.BLACK}{Fore.WHITE}B{Style.RESET_ALL}") for p in board.grid[board.xrad + int(x)][board.yrad + y]])
        print(f"({x}, {y}): {pk}")


def cli_thread(board: game.Board, q: Queue):
    side = game.Side.WHITE
    print(str(board))
    
    while board.status is None:
        try:
            x_input = input("Enter X or command: ")
            
            # Check if it's a command first
            if not x_input.replace('-', '').isdigit():
                parseCommand(board, x_input)
                continue
                
            # Convert to int if it's a number
            x = int(x_input)
            y_input = input("Enter Y: ")
            
            if not y_input.replace('-', '').isdigit():
                print("Invalid Y coordinate. Please enter a number.")
                continue
                
            y = int(y_input)

            # Get the height BEFORE placing the piece
            stack = board.grid[board.xrad + x][board.yrad + y]
            height_before = len(stack)
            
            board.place(game.Piece(side, x, y))
            
            # The new piece will be at height = height_before
            q.put({
                "type": "spawn_piece",
                "side": side,
                "x": x,
                "y": y,
                "z": height_before  # Add the z-coordinate
            })
            
            side = not side
            print(f"SIDE: {"Black" if not side else "White"}")
            print(str(board))
            
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter numbers for coordinates.")
        except IndexError as e:
            print(f"Position out of bounds: {e}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
    print("Game ENDED!")
    print("Black" if side else "White")
board = game.Board()

# update() has to be placed in __main__
def update():
    gui.update(board)

def main() -> int:
    
    q = gui.event_queue
    global board
    threading.Thread(target=cli_thread, args=(board, q), daemon=True).start()

    # debug
    # q.put({"type": "spawn_piece",
    #        "side": game.Side.WHITE,
    #        "x": 0,
    #        "y": 0})
    gui.start_gui()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
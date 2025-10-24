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
        x = input("Enter X or command: ")
        try:
            x = int(x)
            y = int(input("Enter Y: "))
        except:
            parseCommand(board, x) # type: ignore
            continue

        try:
            board.place(game.Piece(side, x, y))
            q.put({
                "type": "spawn_piece",
                "side": side,
                "x": x,
                "y": y
            })
        except Exception as e:
            print(f"{type(e)}{e}")
        side = not side
        print(str(board))

# update() has to be placed in __main__
def update():
    gui.update()

def main() -> int:
    
    q = gui.event_queue
    board = game.Board()
    threading.Thread(target=cli_thread, args=(board, q), daemon=True).start()

    q.put({"type": "spawn_piece",
           "side": game.Side.WHITE,
           "x": 0,
           "y": 0})
    gui.start_gui()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
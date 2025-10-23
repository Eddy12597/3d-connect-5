import gui
import board_and_piece as game

def test():
    
    board = game.Board()
    board.place(game.Piece(game.Side.WHITE, 0, 0))
    print(board.status)
    board.place(game.Piece(game.Side.BLACK, 0, 0))
    print(board.status)
    board.place(game.Piece(game.Side.WHITE, 0, 1))
    print(str(board))
    

def main() -> int:
    
    test()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
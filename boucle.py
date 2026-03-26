from game import *
from bot import *
import time

plateau = Plateau(5)
j1 = RandomMoveBot(plateau.board[4][2], [case for case in plateau.board[0]], plateau)
j2 = RandomBot(plateau.board[0][2], [case for case in plateau.board[4]], plateau)
plateau.add_players(j1, j2)


current_player = j1
while not plateau.game_ended():
    print(plateau)
    print(current_player.play())
    time.sleep(1)
    current_player = plateau.get_other_player(current_player)

print(plateau)
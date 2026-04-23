from game import *
from bot import *
import time

plateau = Plateau(9)
j1 = AlphaStarBot(plateau.board[8][4], [case for case in plateau.board[0]], plateau)
j2 = RandomBot(plateau.board[0][4], [case for case in plateau.board[8]], plateau)
plateau.add_players(j1, j2)


current_player = j1
while not plateau.game_ended():
    print(plateau)
    print(current_player.play())
    time.sleep(0.3)
    current_player = plateau.get_other_player(current_player)

print(plateau)
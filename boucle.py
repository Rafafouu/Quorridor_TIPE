from game import *
import time

plateau = Plateau(9)
j1 = Joueur(plateau.board[8][4], [case for case in plateau.board[0]])
j2 = Joueur(plateau.board[0][4], [case for case in plateau.board[8]])
plateau.add_players(j1, j2)


current_player = j1
while not plateau.game_ended():
    current_player.play()
    print(plateau)
    time.sleep(1)
    current_player = plateau.get_other_player(current_player)
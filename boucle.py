from game import *
from bot import *
from render_pygame import QuoridorRenderer
import time

plateau = Plateau(9)
j2 = AlphaStarLessMoveBot(plateau.board[8][4], [case for case in plateau.board[0]], plateau, 3) #ROUGE
j1 = AlphaStarBot(plateau.board[0][4], [case for case in plateau.board[8]], plateau, 3) #BLEU
plateau.add_players(j1, j2)


renderer = QuoridorRenderer(dim=9)
renderer.run(plateau, j1, j2, plateau.game_ended)

"""current_player = j1

while not plateau.game_ended():
    print("-------------------")
    print("c'est au tour de ", "🔴" if current_player == j1 else "🔵")
    print(plateau)

    t = time.time()

    print(current_player.play())

    print("temps de réflexion : ", time.time() - t, " secondes")

    current_player = plateau.get_other_player(current_player)
    time.sleep(0.75)

print(plateau)
"""
from game import *
from bot import *
from render_pygame import QuoridorRenderer

dim = 5

plateau = Plateau(dim)
j1 = ASBot(plateau.board[dim-1][dim // 2], [case for case in plateau.board[0]], plateau, 5) #ROUGE
j2 = ASLMoveBot(plateau.board[0][dim // 2], [case for case in plateau.board[dim-1]], plateau, 5) #BLEU
plateau.add_players(j1, j2)


renderer = QuoridorRenderer(dim=dim)
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
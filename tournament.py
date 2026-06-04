import inspect
from game import *
import bot
import time

classes = [
    cls
    for name, cls in inspect.getmembers(bot, inspect.isclass)
    if cls.__module__ == bot.__name__ and name != "HumanBot"  and name != "AlphaBotSkeleton"
]




dim = 5
profondeur = 3

nb_games = 1
for bot1 in classes:
    for bot2 in classes:
        print("-------------------")
        print("game " + str(nb_games))
        print(bot1.__name__ + " vs " + bot2.__name__)

  

        plateau = Plateau(dim)

        if issubclass(bot1, bot.AlphaBotSkeleton):
            j1 = bot1(plateau.board[dim-1][dim // 2], [case for case in plateau.board[0]], plateau, profondeur) #ROUGE
        else:
            j1 = bot1(plateau.board[dim-1][dim // 2], [case for case in plateau.board[0]], plateau) #ROUGE
        

        if issubclass(bot2, bot.AlphaBotSkeleton):
            j2 = bot2(plateau.board[dim-1][dim // 2], [case for case in plateau.board[0]], plateau, profondeur) #BLEU
        else:
            j2 = bot2(plateau.board[dim-1][dim // 2], [case for case in plateau.board[0]], plateau) #BLEU

        
        plateau.add_players(j1, j2)


        current_player = j1
        
        while not plateau.game_ended():
            
            current_player.play()
            current_player = plateau.get_other_player(current_player)
        
        winner = plateau.get_other_player(current_player)
        print("Winner : " + (bot1.__name__ +" (j1)" if winner == j1 else bot2.__name__ + "(j2)"))

        nb_games = nb_games + 1

        
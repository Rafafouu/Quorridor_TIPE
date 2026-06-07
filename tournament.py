import inspect
import csv
from game import *
import bot
from collections import defaultdict
import time

banList = [
    "HumanBot",
    "AlphaBotSkeleton",
    "AlphaManhattanBot",
    "ASLBotSkeleton"
]

classes = [
    cls
    for name, cls in inspect.getmembers(bot, inspect.isclass)
    if cls.__module__ == bot.__name__ and name not in banList
]

barrieres = 5
dim = 5
profondeur_as = 4
profondeur_asl = 3 #as2l ils ont pareil c bon flemme

csv_filename = f"tournaments/Dim_{str(dim)}_Prof_{str(profondeur_as)}_{str(profondeur_asl)}" #sans .csv stp

bot_names = [cls.__name__ for cls in classes]

results = {b1: {b2: "" for b2 in bot_names} for b1 in bot_names}


stats = {
    name: {
        "j1_wins": 0,
        "j1_games": 0,
        "j2_wins": 0,
        "j2_games": 0
    }
    for name in bot_names
}


MOVE_LIMIT = 200 #apres ca compte comme égalité
game_id = 1



heure_debut = time.time()

# total number of games to play (used for ETA)
total_games = len(classes) * len(classes)

for bot1 in classes:
    for bot2 in classes:
        
        moves_count = 0

        print("-------------------")
        print(f"game {game_id}")
        print(f"{bot1.__name__} vs {bot2.__name__}")

        plateau = Plateau(dim)


        if issubclass(bot1, bot.AlphaBotSkeleton):
            j1 = bot1(
                plateau.board[dim-1][dim // 2],
                [case for case in plateau.board[0]],
                plateau,
                profondeur_asl if issubclass(bot1, bot.ASLBotSkeleton) else profondeur_as,
                barrieres=barrieres
            )
        else:
            j1 = bot1(
                plateau.board[dim-1][dim // 2],
                [case for case in plateau.board[0]],
                plateau,
                barrieres=barrieres
            )

        if issubclass(bot2, bot.AlphaBotSkeleton):
            j2 = bot2(
                plateau.board[0][dim // 2],
                [case for case in plateau.board[dim-1]],
                plateau,
                profondeur_asl if issubclass(bot2, bot.ASLBotSkeleton) else profondeur_as,
                barrieres=barrieres
            )
        else:
            j2 = bot2(
                plateau.board[0][dim // 2],
                [case for case in plateau.board[dim-1]],
                plateau,
                barrieres=barrieres
            )

        plateau.add_players(j1, j2)

        current_player = j1

        while not plateau.game_ended():
            if moves_count > MOVE_LIMIT:
                print("Trop long ya égalité c bon")
                break
            
            current_player.play()
            current_player = plateau.get_other_player(current_player)
            moves_count = moves_count + 1

        print(f"Nombre de coups : {moves_count}")
        winner = plateau.get_other_player(current_player) if moves_count <= MOVE_LIMIT else None


        schizophrene = (bot1.__name__ == bot2.__name__)

        if winner == j1:
            winner_name = bot1.__name__
            result = "J1"

            stats[bot1.__name__]["j1_wins"] += 1
        elif winner == j2:
            winner_name = bot2.__name__
            result = "J2"

            stats[bot2.__name__]["j2_wins"] += 1
        else: #si ya égalité (move limit)
            winner_name = "Draw"
            
            stats[bot1.__name__]["j1_wins"] += 0.5
            stats[bot2.__name__]["j2_wins"] += 0.5


        stats[bot1.__name__]["j1_games"] += 1
        stats[bot2.__name__]["j2_games"] += 1
        

        print(f"Winner : {winner_name} ({'j1' if winner == j1 else 'j2' if winner == j2 else ''})")

        results[bot1.__name__][bot2.__name__] = result

        game_id += 1

        # ETA reporting
        games_completed = game_id - 1
        elapsed = time.time() - heure_debut
        remaining = total_games - games_completed
        if games_completed > 0 and remaining > 0:
            avg = elapsed / games_completed
            eta = avg * remaining
            h = int(eta // 3600)
            m = int((eta % 3600) // 60)
            s = int(eta % 60)
            print(f"ETA: {h:02d}:{m:02d}:{s:02d} (remaining {remaining} games, avg {avg:.2f}s/game)")
        elif remaining == 0:
            print("ETA: done")
        else:
            print("ETA: calculating...")





#tableau résultats
with open(f"{csv_filename}.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow(["J1 \\ J2"] + bot_names)

    for b1 in bot_names:
        row = [b1]
        for b2 in bot_names:
            row.append(results[b1][b2])
        writer.writerow(row)




#stats sur les winrates

total_j1_wins = 0
total_j1_games = 0
total_j2_wins = 0
total_j2_games = 0


with open(f"{csv_filename}_winrates.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "bot",
        "winrate_j1",
        "winrate_j2",
        "winrate_global"
    ])

    for b in bot_names:
        j1_g = stats[b]["j1_games"]
        j2_g = stats[b]["j2_games"]

        j1_w = stats[b]["j1_wins"]
        j2_w = stats[b]["j2_wins"]

        total_j1_wins += j1_w
        total_j1_games += j1_g
        total_j2_wins += j2_w
        total_j2_games += j2_g

        total_games = j1_g + j2_g
        total_wins = j1_w + j2_w

        winrate_j1 = j1_w / j1_g if j1_g else 0
        winrate_j2 = j2_w / j2_g if j2_g else 0
        winrate_global = total_wins / total_games if total_games else 0

        writer.writerow([
            b,
            round(winrate_j1, 3),
            round(winrate_j2, 3),
            round(winrate_global, 3)
        ])
    
    writer.writerow([
        "GLOBAL",
        round(total_j1_wins / total_j1_games, 3) if total_j1_games else 0,
        round(total_j2_wins / total_j2_games, 3) if total_j2_games else 0,
        ""
    ])

print("---------------")
print(f"Sauvegardé dans {csv_filename}.csv")
print(f"Temps d'exécution : {time.time() - heure_debut} secondes")
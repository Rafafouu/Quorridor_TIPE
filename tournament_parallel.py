#!/usr/bin/env python3
"""Parallel tournament runner.

This runs matches (bot1 vs bot2) in separate processes and collects results in the main process.
It mirrors the logic from `tournament.py` for instantiating bots.

Usage:
    python3 tournament_parallel.py --workers 4 --dim 5

By default workers=cpu_count()-1.
"""
import argparse
import inspect
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import csv

import bot


banList = [
    "HumanBot",
    "AlphaBotSkeleton",
    "AlphaManhattanBot",
    "ASLBotSkeleton",
]


def collect_classes():
    return [name for name, cls in inspect.getmembers(bot, inspect.isclass) if cls.__module__ == bot.__name__ and name not in banList]


# Worker function (top-level so it can be pickled)
def run_one_match(args):
    """Run a single match in a worker process.

    args: tuple(bot1_name, bot2_name, dim, profondeur_as, profondeur_asl, move_limit)
    returns: (bot1_name, bot2_name, result, elapsed_seconds)
    """
    bot1_name, bot2_name, dim, profondeur_as, profondeur_asl, move_limit, barrieres = args
    # Import modules locally in worker to avoid pickling issues
    import bot as botmod
    from game import Plateau

    start = time.time()

    plateau = Plateau(dim)
    Bot1 = getattr(botmod, bot1_name)
    Bot2 = getattr(botmod, bot2_name)

    # instantiate j1
    if issubclass(Bot1, botmod.AlphaBotSkeleton):
        j1 = Bot1(
            plateau.board[dim - 1][dim // 2],
            [case for case in plateau.board[0]],
            plateau,
            profondeur_asl if issubclass(Bot1, botmod.ASLBotSkeleton) else profondeur_as,
        )
    else:
        j1 = Bot1(plateau.board[dim - 1][dim // 2], [case for case in plateau.board[0]], plateau)

    # instantiate j2
    if issubclass(Bot2, botmod.AlphaBotSkeleton):
        j2 = Bot2(
            plateau.board[0][dim // 2],
            [case for case in plateau.board[dim - 1]],
            plateau,
            profondeur_asl if issubclass(Bot2, botmod.ASLBotSkeleton) else profondeur_as,
        )
    else:
        j2 = Bot2(plateau.board[0][dim // 2], [case for case in plateau.board[dim - 1]], plateau)

    plateau.add_players(j1, j2)

    # set starting barriers if provided
    if barrieres is not None:
        try:
            j1.barrieres = barrieres
            j2.barrieres = barrieres
        except Exception:
            pass

    current_player = j1
    moves_count = 0

    while not plateau.game_ended():
        if moves_count > move_limit:
            break
        current_player.play()
        current_player = plateau.get_other_player(current_player)
        moves_count += 1

    winner = plateau.get_other_player(current_player) if moves_count <= move_limit else None
    if winner == j1:
        result = "J1"
    elif winner == j2:
        result = "J2"
    else:
        result = "Draw"

    elapsed = time.time() - start
    return (bot1_name, bot2_name, result, elapsed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=max(1, multiprocessing.cpu_count() - 1))
    parser.add_argument("--dim", type=int, default=5)
    parser.add_argument("--profondeur_as", type=int, default=3)
    parser.add_argument("--profondeur_asl", type=int, default=4)
    parser.add_argument("--move_limit", type=int, default=200)
    parser.add_argument("--barrieres", type=int, default=None, help="Starting number of barriers for each player (overrides default)")
    parser.add_argument("--out", type=str, default=None, help="CSV output filename (defaults to tournaments/Dim_...)")
    args = parser.parse_args()

    dim = args.dim
    profondeur_as = args.profondeur_as
    profondeur_asl = args.profondeur_asl
    move_limit = args.move_limit
    barrieres = args.barrieres

    classes = collect_classes()
    pairs = [(a, b) for a in classes for b in classes]
    total = len(pairs)

    if args.out:
        csv_filename = args.out
    else:
        csv_filename = f"tournaments/Dim_{dim}_Prof_{profondeur_as}_{profondeur_asl}.csv"

    results = {b1: {b2: "" for b2 in classes} for b1 in classes}

    start_all = time.time()

    # Prepare tasks (only primitive data to avoid heavy pickling)
    tasks = [(a, b, dim, profondeur_as, profondeur_asl, move_limit, barrieres) for (a, b) in pairs]

    print(f"Running {total} matches with {args.workers} workers...")

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(run_one_match, t): t for t in tasks}
        done = 0
        for fut in as_completed(futures):
            try:
                b1, b2, res, elapsed = fut.result()
            except Exception as e:
                # record failure
                t = futures[fut]
                b1, b2 = t[0], t[1]
                res = "Error"
                elapsed = 0
                print(f"Match {b1} vs {b2} failed in worker: {e}")

            results[b1][b2] = res
            done += 1
            elapsed_total = time.time() - start_all
            avg = elapsed_total / done
            remaining = total - done
            eta = int(avg * remaining)
            print(f"[{done}/{total}] {b1} vs {b2} => {res} in {elapsed:.1f}s; ETA ≈ {eta}s")

    # write CSV
    # ensure directory exists
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["J1 \\ J2"] + classes)
            for b1 in classes:
                row = [b1]
                for b2 in classes:
                    row.append(results[b1][b2])
                writer.writerow(row)
    except Exception as e:
        print(f"Failed to write CSV {csv_filename}: {e}")

    # compute and write winrates (like tournament.py)
    try:
        stats = {
            name: {
                "j1_wins": 0,
                "j1_games": 0,
                "j2_wins": 0,
                "j2_games": 0,
            }
            for name in classes
        }

        for b1 in classes:
            for b2 in classes:
                res = results[b1][b2]
                stats[b1]["j1_games"] += 1
                stats[b2]["j2_games"] += 1

                if res == "J1":
                    stats[b1]["j1_wins"] += 1
                elif res == "J2":
                    stats[b2]["j2_wins"] += 1
                else:  # Draw or other
                    if res == "Draw":
                        stats[b1]["j1_wins"] += 0.5
                        stats[b2]["j2_wins"] += 0.5

        total_j1_wins = 0
        total_j1_games = 0
        total_j2_wins = 0
        total_j2_games = 0

        winrates_filename = csv_filename.replace('.csv', '') + "_winrates.csv"
        with open(winrates_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["bot", "winrate_j1", "winrate_j2", "winrate_global"])

            for b in classes:
                j1_g = stats[b]["j1_games"]
                j2_g = stats[b]["j2_games"]

                j1_w = stats[b]["j1_wins"]
                j2_w = stats[b]["j2_wins"]

                total_j1_wins += j1_w
                total_j1_games += j1_g
                total_j2_wins += j2_w
                total_j2_games += j2_g

                total_g = j1_g + j2_g
                total_w = j1_w + j2_w

                winrate_j1 = j1_w / j1_g if j1_g else 0
                winrate_j2 = j2_w / j2_g if j2_g else 0
                winrate_global = total_w / total_g if total_g else 0

                writer.writerow([b, round(winrate_j1, 3), round(winrate_j2, 3), round(winrate_global, 3)])

            writer.writerow([
                "GLOBAL",
                round(total_j1_wins / total_j1_games, 3) if total_j1_games else 0,
                round(total_j2_wins / total_j2_games, 3) if total_j2_games else 0,
                "",
            ])
    except Exception as e:
        print(f"Failed to write winrates CSV: {e}")

    print("Done. Total time:", time.time() - start_all)


if __name__ == "__main__":
    main()

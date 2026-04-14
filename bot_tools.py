from game import *

class Action:
    def __init__(self, kind, data): 
        self.kind = kind      
        self.data = data      


def is_wall_legal(self, i, j, is_vertical):  #ressemble a try place wall mais on back up tt le tps
    if not self.can_wall(i, j, is_vertical):
        return False

    saved = []

    def save_and_cut(case, direction):
        saved.append((case, direction, getattr(case, direction)))
        setattr(case, direction, None)

    if not is_vertical:
        save_and_cut(self.board[i][j], "up")
        save_and_cut(self.board[i][j+1], "up")
        save_and_cut(self.board[i-1][j], "down")
        save_and_cut(self.board[i-1][j+1], "down")
    else:
        save_and_cut(self.board[i][j], "left")
        save_and_cut(self.board[i+1][j], "left")
        save_and_cut(self.board[i][j-1], "right")
        save_and_cut(self.board[i+1][j-1], "right")

    legal = (
        self.can_finish_BFS(self.j1)
        and self.can_finish_BFS(self.j2)
    )

    for case, attr, val in saved:
        setattr(case, attr, val)

    return legal


def plateau_get_actions(self, joueur):

    actions = []

    for c in self.get_accessible_cases(joueur):
        actions.append(Action("move", c))

    if joueur.barrieres > 0:
        for i in range(self.dim):
            for j in range(self.dim):
                for v in (False, True):
                    if self.is_wall_legal(i, j, v):
                        actions.append(Action("wall", (i, j, v)))

    return actions



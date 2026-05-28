from collections import deque
import heapq
from importlib.resources import path

BARRIERE_START = 10

class Case : 

    def __lt__(self, other): #pour la heapq apparemment jsp
        return False

    def __init__(self,row,col,left= None,right = None,up= None,down = None):
        self.row = row
        self.col = col
        self.left = left
        self.right = right
        self.up = up
        self.down= down
    
    def __repr__(self): #sert plus trop
        l = self.left is not None
        r = self.right is not None
        u = self.up is not None
        d = self.down is not None

        mapping = {
            (1,1,1,1): "╬ ",

            (1,1,0,0): "═ ",
            (0,0,1,1): "║ ",

            (1,0,1,0): "╝ ",
            (0,1,1,0): "╚ ",
            (1,0,0,1): "╗ ",
            (0,1,0,1): "╔ ",

            (1,1,1,0): "╩ ",
            (1,1,0,1): "╦ ",
            (1,0,1,1): "╣ ",
            (0,1,1,1): "╠ ",

            (0,0,0,1): "╥ ",
            (0,0,1,0): "╨ ",
            (1,0,0,0): "╡ ",
            (0,1,0,0): "╞ ",

            (0,0,0,0): "Ⓞ"
        }

        return mapping.get((l, r, u, d), "?")
    
    def get_accessible_neighbors(self): #avoir les voisins
        voisins = []

        if self.left:
            voisins.append(self.left)
        if self.right:
            voisins.append(self.right)
        if self.up:
            voisins.append(self.up)
        if self.down:
            voisins.append(self.down)
        
        return voisins



#faire inhéritance de classe pour créer des joueurs aux comportements différents
class Joueur:

    def __init__(self,case: Case, goal : list[Case], plateau:"Plateau"):
        self.case = case
        self.goal = goal
        self.plateau = plateau
        self.barrieres = BARRIERE_START
    
    def try_move(self, destination : Case):
        if destination in self.plateau.get_accessible_cases(self):
            self.case = destination
            return True
        return False
    


    def a_star_shortest_physical_path(self): #NE PREND PAS EN COMPTE L'AUTRE JOUEUR
        start = self.case

        # chaque element = (f, g, current, path_taken)
        # g = distance entre départ et current
        # f = g + h (Manhattan distance)
        
        priority_queue = [(0 + manhattan_distance_to_goal(start, self), 0, start, [start])]
        visited = {
            start: 0
        }

        while len(priority_queue) > 0:
            f, g, current, path = heapq.heappop(priority_queue)

            if current in self.goal:
                return path

            neighbors = current.get_accessible_neighbors()

            for neighbor in neighbors:
                if neighbor not in visited or g + 1 < visited[neighbor]: #on update le voisin si on trouve un chemin plus court vers lui
                    visited[neighbor] = g + 1
                    h = manhattan_distance_to_goal(neighbor, self)
                    heapq.heappush(priority_queue, (g + 1 + h, g + 1, neighbor, path + [neighbor]))
        
        return None #aucun chemin



    
    def try_place_wall(self, i, j, is_vertical=False):
        
        if self.barrieres <= 0:
            return False

        result = self.plateau.is_wall_legal(i, j, is_vertical)
        if result:
            self.barrieres -= 1
            self.plateau.place_wall(i, j, is_vertical)
        
        return result


    

    def play(self):
        print("OVERWRITE THIS PLZ")

class Action: #les actions a jouer genre se deplacer / poser une barrière
    def __init__(self, action_type, destination=None, i=None, j=None, is_vertical=None):
        self.type = action_type 
        
        
        self.destination = destination

        self.i = i
        self.j = j
        self.is_vertical = is_vertical  
    
    def __repr__(self):
        return str(self.type)+ str(self.destination) + str(self.i)+str(self.j)+str(self.is_vertical)


class Plateau :
    def __init__(self,dimension):
        self.dim = dimension
        self.board = [[Case(i,j) for j in range(self.dim)] for i in range(self.dim)]

        for i in range(self.dim):
            for j in range(self.dim):
                if i>0:
                    self.board[i][j].up = self.board[i-1][j]
                if i<self.dim-1:
                    self.board[i][j].down = self.board[i+1][j]
                if j>0:
                    self.board[i][j].left = self.board[i][j-1]
                if j<self.dim-1:
                    self.board[i][j].right = self.board[i][j+1]
        self.j1 : Joueur = None
        self.j2 : Joueur= None
    
    def add_players(self, j1, j2):
        self.j1 = j1
        self.j2 = j2

    #peut placer un mur PHYSIQUEMENT
    def can_wall(self, i, j, is_vertical):
        
        if not is_vertical:

            if i <= 0 or i >= self.dim:
                return False

            if j < 0 or j >= self.dim - 1:
                return False

            # overlap
            if self.board[i][j].up is None:
                return False

            if self.board[i][j+1].up is None:
                return False

            # crossing wall
            # vertical centered on same intersection
            if (
                self.board[i][j+1].left is None
                and self.board[i-1][j+1].left is None
            ):
                return False

            return True

        else:

            if j <= 0 or j >= self.dim:
                return False

            if i < 0 or i >= self.dim - 1:
                return False

            # overlap
            if self.board[i][j].left is None:
                return False

            if self.board[i+1][j].left is None:
                return False

            # crossing wall
            if (
                self.board[i+1][j].up is None
                and self.board[i+1][j-1].up is None
            ):
                return False

            return True
    
    def can_finish_BFS(self,joueur):  #dépassé 
        vu = set()
        case = joueur.case
        file = deque()
        file.append(case)
        while file :
            case = file.popleft()
            if not case:
                continue
            
            if case in joueur.goal:
                return True
            for v in [case.up, case.down, case.left, case.right]:
                        if v and v not in vu:
                            vu.add(v)
                            file.append(v)
        return False
    
    def can_finish_dfs(self, joueur): #dfs smart qui sent l'odeur du goal hmm miam miam
        start = joueur.case
        visited = set()
        pile = [start]

        while len(pile) > 0:
            current = pile.pop()

            if current in visited:
                continue

            visited.add(current)

            if current in joueur.goal:
                return True
            
            voisins = sorted(current.get_accessible_neighbors(), key=lambda v: manhattan_distance_to_goal(v, joueur), reverse=True)

            for v in voisins:
                if v not in visited:
                    pile.append(v)
        
        return False

    def can_finish_dumb_dfs(self, joueur): #dfs débile basique sans odorat
        start = joueur.case
        visited = {start} #set qui contient start 
        pile = [start]

        while pile:
            current = pile.pop()

            if current in joueur.goal:
                return True

            for v in current.get_accessible_neighbors():
                if v not in visited:
                    visited.add(v)
                    pile.append(v)
        
        return False


    def save_and_cut(self,saved,case, direction):
            saved.append((case, direction, getattr(case, direction)))
            setattr(case, direction, None)


    #essaye de placer un mur (vérifie physiquement + autorisé par les regles)

    def is_wall_legal(self, i, j, is_vertical):

        if not self.can_wall(i, j, is_vertical):
            return False

        saved = []

        if not is_vertical:
            self.save_and_cut(saved, self.board[i][j], "up")
            self.save_and_cut(saved, self.board[i][j+1], "up")
            self.save_and_cut(saved, self.board[i-1][j], "down")
            self.save_and_cut(saved, self.board[i-1][j+1], "down")
        else:
            self.save_and_cut(saved, self.board[i][j], "left")
            self.save_and_cut(saved, self.board[i+1][j], "left")
            self.save_and_cut(saved, self.board[i][j-1], "right")
            self.save_and_cut(saved, self.board[i+1][j-1], "right")

        legal = (
            self.can_finish_dumb_dfs(self.j1)
            and self.can_finish_dumb_dfs(self.j2)
        )

        for case, attr, val in saved:
            setattr(case, attr, val)

        return legal
    
    def place_wall(self,i,j,is_vertical): #prend UN COUP LEGAL    §§§§§§§§§!!!!!!!!
        saved = []
        if not is_vertical:
            self.save_and_cut(saved,self.board[i][j], "up")
            self.save_and_cut(saved,self.board[i][j+1], "up")
            self.save_and_cut(saved,self.board[i-1][j], "down")
            self.save_and_cut(saved,self.board[i-1][j+1], "down")
        else:
            self.save_and_cut(saved,self.board[i][j], "left")
            self.save_and_cut(saved,self.board[i+1][j], "left")
            self.save_and_cut(saved,self.board[i][j-1], "right")
            self.save_and_cut(saved,self.board[i+1][j-1], "right")

        return saved

        
    def game_ended(self):
        return (self.j1.case in self.j1.goal) or (self.j2.case in self.j2.goal)
    

    def __repr__(self):
        string = ""

        col_1, row_1 = self.j1.case.col, self.j1.case.row
        col_2, row_2 = self.j2.case.col, self.j2.case.row

        for i in range(self.dim):
            for j in range(self.dim):

                if (i==row_1 and j==col_1):
                    string = string + "🔴"
                elif (i==row_2 and j==col_2):
                    string = string + "🔵"
                else:
                    string = string + str(self.board[i][j])
                
            string = string + "\n"

        return string
    
    def get_other_player(self,player):
        if player == self.j1 :
            return self.j2
        return self.j1
    
    def get_accessible_cases(self,j_current: Joueur):
        l = []
        j_other = self.get_other_player(j_current)

        #down
        if j_current.case.down:
            if j_current.case.down != j_other.case:
                l.append(j_current.case.down)
            else:
                if j_current.case.down.down :
                    l.append(j_current.case.down.down)  

                else :
                    if j_current.case.down.right :
                        l.append(j_current.case.down.right)  

                    if j_current.case.down.left :
                        l.append(j_current.case.down.left)        

        #up
        if j_current.case.up:
            if j_current.case.up != j_other.case:
                l.append(j_current.case.up)
            else:
                if j_current.case.up.up :
                    l.append(j_current.case.up.up)  

                else :
                    if j_current.case.up.right :
                        l.append(j_current.case.up.right)  

                    if j_current.case.up.left :
                        l.append(j_current.case.up.left)
        

        #left
        if j_current.case.left:
            if j_current.case.left != j_other.case:
                l.append(j_current.case.left)
            else:
                if j_current.case.left.left :
                    l.append(j_current.case.left.left)  

                else :
                    if j_current.case.left.up :
                        l.append(j_current.case.left.up)  

                    if j_current.case.left.down :
                        l.append(j_current.case.left.down)        

        #right
        if j_current.case.right:
            if j_current.case.right != j_other.case:
                l.append(j_current.case.right)
            else:
                if j_current.case.right.right :
                    l.append(j_current.case.right.right)  

                else :
                    if j_current.case.right.up :
                        l.append(j_current.case.right.up)  

                    if j_current.case.right.down :
                        l.append(j_current.case.right.down)  
        
        return list(set(l))
    
    def get_all_legal_actions(self, joueur : Joueur):
        actions = []
        
        for dest_case in self.get_accessible_cases(joueur):
            actions.append(Action("MOVE", dest_case))
            
        
        if joueur.barrieres > 0:

            player_path = joueur.a_star_shortest_physical_path()
            other_path = self.get_other_player(joueur).a_star_shortest_physical_path()

            player_edges = path_to_edges(player_path)
            other_edges = path_to_edges(other_path)
            path_edges = player_edges | other_edges

            for i in range(self.dim):
                for j in range(self.dim):
                    for b in [True, False]:
                        if not self.can_wall(i, j, b):
                            continue

                        # get the 2 edges this wall would cut
                        if not b:  # horizontal wall at (i,j): cuts up/down edges
                            wall_edges = {
                                (self.board[i][j],   self.board[i-1][j]),
                                (self.board[i-1][j], self.board[i][j]),
                                (self.board[i][j+1], self.board[i-1][j+1]),
                                (self.board[i-1][j+1], self.board[i][j+1]),
                            }
                        else:  # vertical wall at (i,j): cuts left/right edges
                            wall_edges = {
                                (self.board[i][j],   self.board[i][j-1]),
                                (self.board[i][j-1], self.board[i][j]),
                                (self.board[i+1][j], self.board[i+1][j-1]),
                                (self.board[i+1][j-1], self.board[i+1][j]),
                            }

                        if wall_edges & path_edges:
                            # wall cuts a path edge — need full legality check
                            if self.is_wall_legal(i, j, b):
                                actions.append(Action("WALL", i=i, j=j, is_vertical=b))
                        else:
                            # wall doesn't touch any path edge — can_wall is enough
                            actions.append(Action("WALL", i=i, j=j, is_vertical=b))
                                

                        
        return actions

    def get_less_legal_actions(self, joueur):
        actions = []

        other_player = self.get_other_player(joueur)

        for dest_case in self.get_accessible_cases(joueur):
            actions.append(Action("MOVE", dest_case))

        if joueur.barrieres <= 0:
            return actions

        min_col = max(0, min(joueur.case.col, other_player.case.col) - 1)
        max_col = min(self.dim - 1,
                    max(joueur.case.col, other_player.case.col) + 1)

        for i in range(self.dim):

            for j in range(min_col, max_col + 1):

                for b in [True, False]:

                    if self.is_wall_legal(i, j, b):
                        actions.append(
                            Action(
                                "WALL",
                                i=i,
                                j=j,
                                is_vertical=b
                            )
                        )

        return actions

    def apply_action(self, joueur, action):
        if action.type == "MOVE":
            old_case = joueur.case
            joueur.case = action.destination
            return ("MOVE",old_case)   #pour backup
            
        elif action.type == "WALL":
            joueur.barrieres -= 1
            return ("WALL",joueur.plateau.place_wall(action.i, action.j, action.is_vertical)) #pour backup

    def undo_action(self,joueur,backup):
        back_type = backup[0]
        back_action = backup[1]

        if back_type == "MOVE":
            joueur.case = back_action #old_case

        elif back_type == "WALL":
            joueur.barrieres += 1

            for case, attr, val in back_action: #juste repris de is_wall_legal
                setattr(case, attr, val)


def path_to_edges(path):
        edges = set()
        for k in range(len(path) - 1):
            a, b = path[k], path[k+1]
            edges.add((a, b))
            edges.add((b, a))  
        return edges


def manhattan_distance_to_goal(case, player):
    return abs(case.row - player.goal[0].row)
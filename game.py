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
    
    def __repr__(self):
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

class Action:
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
    def can_wall(self,i,j,is_vertical): 
        if not is_vertical:
            
            if i<1 or j>=self.dim - 1 :

                return False
            if self.board[i][j].right ==None and self.board[i-1][j].right == None :
                return False

            if self.board[i][j].up == None or self.board[i][j+1].up == None:
                return False
            
        else :
            if i>= self.dim - 1 or j<1 : 

                return False
            if self.board[i][j].up == None and self.board[i][j-1].up == None :
                return False
            if self.board[i][j].left == None or self.board[i+1][j].left == None :
                return False
            
        return True
    
    def can_finish_BFS(self,joueur):
        vu = set()
        case = joueur.case
        file = [case]
        while file :
            if not case:
                continue
            
            case = file.pop(0)
            if case in joueur.goal:
                return True
            if case not in vu : 
                vu.add(case)
                if case.up:
                    file.append(case.up)
                if case.down:
                    file.append(case.down)
                if case.right:
                    file.append(case.right)
                if case.left:
                    file.append(case.left)
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
            self.can_finish_BFS(self.j1)
            and self.can_finish_BFS(self.j2)
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


    def get_all_legal_actions(self, joueur):
        actions = []
        
        for dest_case in self.get_accessible_cases(joueur):
            actions.append(Action("MOVE", dest_case))
            
        
        if joueur.barrieres > 0:
            for i in range(self.dim):
                for j in range(self.dim):
                    
                    if self.is_wall_legal(i, j, is_vertical=False):
                        actions.append(Action("WALL", i=i, j=j, is_vertical=False))
                   
                    if self.is_wall_legal(i, j, is_vertical=True):
                        actions.append(Action("WALL", i=i, j=j, is_vertical=True))
                        
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






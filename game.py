BARRIERE_START = 10


class Case : 
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

        result = self.plateau.try_place_wall(i, j, is_vertical)
        if result:
            self.barrieres -= 1
        
        return result

    def play(self):
        print("OVERWRITE THIS PLZ")




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
        vu = []
        case = joueur.case
        file = [case]
        while file :
            if not case:
                continue
            
            case = file.pop(0)
            if case in joueur.goal:
                return True
            if case not in vu : 
                vu.append(case)
                if case.up:
                    file.append(case.up)
                if case.down:
                    file.append(case.down)
                if case.right:
                    file.append(case.right)
                if case.left:
                    file.append(case.left)
        return False 

    #essaye de placer un mur (vérifie physiquement + autorisé par les regles)
    def try_place_wall(self, i, j, is_vertical=False):
        if not self.can_wall(i, j, is_vertical):

            return False

        saved = []

        def save_and_cut(case, direction):
            saved.append((case, direction, getattr(case, direction)))
            setattr(case, direction, None)

        # APPLY
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

        

        #si on peut plus finir on revient a l'état initual et on renvoie false
        if not (self.can_finish_BFS(self.j1) and self.can_finish_BFS(self.j2)):
            for case, attr, val in saved: 
                setattr(case, attr, val)

            return False

        return True

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






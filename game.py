class Case : 
    def __init__(self,row,col,left= None,right = None,up= None,down = None):
        self.row = row
        self.col = col
        self.left = left
        self.right = right
        self.up = up
        self.down= down
        self.has_player = False
        
    
    def __repr__(self):
        l = self.left is not None
        r = self.right is not None
        u = self.up is not None
        d = self.down is not None

        mapping = {
            (1,1,1,1): "╬",

            (1,1,0,0): "═",
            (0,0,1,1): "║",

            (1,0,1,0): "╝",
            (0,1,1,0): "╚",
            (1,0,0,1): "╗",
            (0,1,0,1): "╔",

            (1,1,1,0): "╩",
            (1,1,0,1): "╦",
            (1,0,1,1): "╣",
            (0,1,1,1): "╠",

            (0,0,0,1): "╥",
            (0,0,1,0): "╨",
            (1,0,0,0): "╡",
            (0,1,0,0): "╞",

            (0,0,0,0): "Ⓞ"
        }

        return mapping.get((l, r, u, d), "?")


class Joueur:

    def __init__(self,case: Case,goal):
        self.case = case
        self.goal = goal
        self.bar= BARRIERE_START




class Plateau :
    def __init__(self,dimension,j1,j2):
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
        self.j1 = j1
        self.j2 = j2

    def can_wall(self,i,j,is_vertical): 
        if not is_vertical:
            
            if i<1 or j>=self.dim - 1 :
                print("dumbass")
                return False
            if self.board[i][j].right ==None and self.board[i-1][j].right == None :
                return False

            if self.board[i][j].up == None or self.board[i][j+1].up == None:
                return False
            
        else :
            if i>= self.dim - 1 or j<1 : 
                print("dumbass")
                return False
            if self.board[i][j].up == None and self.board[i][j-1].up == None :
                return False
            if self.board[i][j].left == None or self.board[i+1][j].left == None :
                return False
            
        return True
    
    def can_finish_BFS(self,case,goal):
        vu = [] 
        file = [case]
        while file :
            case = file[0]
            if case.row == goal:
                return True
            if case not in vu : 
                vu.append(case)
                file.append(case.up)
                file.append(case.down)
                file.append(case.right)
                file.append(case.left)
        return False 
 
    def place_wall(self, i, j, is_vertical=False): 
        if self.can_wall(i,j,is_vertical):
            if not is_vertical: 
                self.board[i][j].up = None
                self.board[i][j+1].up = None
                self.board[i-1][j].down = None
                self.board[i-1][j+1].down = None

            if is_vertical :
                self.board[i][j].left = None
                self.board[i+1][j].left = None
                self.board[i][j-1].right = None
                self.board[i+1][j-1].right = None

    def __repr__(self):
        string = ""
        for i in range(self.dim):
            for j in range(self.dim):
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




BARRIERE_START = 10
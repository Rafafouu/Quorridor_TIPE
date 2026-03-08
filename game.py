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
        return False #chaque joueur devra etre check avec son goal respectif pour can wall
 
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
    

class Joueur : 
    pass

board = Plateau(9)
print(board)
board.place_wall(0,0,False)
print(board)
board.place_wall(1,1,False)
print(board)
board.place_wall(1,1,True)
print(board)

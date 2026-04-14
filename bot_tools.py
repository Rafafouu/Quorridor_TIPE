from game import *

class Action:
    def __init__(self, action_type, destination=None, i=None, j=None, is_vertical=None):
        self.type = action_type 
        
        
        self.destination = destination

        self.i = i
        self.j = j
        self.is_vertical = is_vertical  

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
            return old_case   #pour backup
            
        elif action.type == "WALL":
            joueur.barrieres -= 1
            return joueur.plateau.place_wall(action.i, action.j, action.is_vertical) #pour backup



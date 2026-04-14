from game import *
import heapq

def manhattan_distance_to_goal(case, player):
    return min([abs(case.row - goal_case.row) + abs(case.col - goal_case.col) for goal_case in player.goal])

def a_star_shortest_path(player):
    start = player.case
    
    # chaque element = (f, g, current, path_taken)
    # g = distance entre départ et current
    # f = g + h (Manhattan distance)
    
    priority_queue = [(0 + manhattan_distance_to_goal(start, player), 0, start, [])]
    visited = {
        start: 0
    }

    while len(priority_queue) > 0:
        f, g, current, path = heapq.heappop(priority_queue)

        if current in player.goal:
            return path

        neighbors = []


        if g == 0: #si c'est le premier tour faut prendre en compte la position de l'adversaire
            neighbors = player.plateau.get_accessible_cases(player)
        else: #on s'occupe pas du joueur adverse psk tfacon il va bouger
            if current.up: neighbors.append(current.up)
            if current.down: neighbors.append(current.down)
            if current.left: neighbors.append(current.left)
            if current.right: neighbors.append(current.right)

        for neighbor in neighbors:
            if neighbor not in visited or g + 1 < visited[neighbor]: #on update le voisin si on trouve un chemin plus court vers lui
                visited[neighbor] = g + 1
                h = manhattan_distance_to_goal(neighbor, player)
                heapq.heappush(priority_queue, (g + 1 + h, g + 1, neighbor, path + [neighbor]))
    
    return None #aucun chemin


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



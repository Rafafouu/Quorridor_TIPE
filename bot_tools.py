from game import *
import heapq

#tu veux juste pas coder comme si t avais une pile parce que devoir dire qu on importe une bibliothèque juste
#pour des piles et files je trouve ca con



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

def alpha_beta(eval ,plateau : Plateau ,profondeur : int,alpha : int,beta : int, joueur : Joueur, maxi : bool):
    """
    on prend en paramètre : la fonction d'évaluation (logique)
                            le plateau qui nous sert a avoir l'état actuel de la position
                            alpha,beta : principe pour élager des branches selon alpha beta
                            joueur : celui avec lequel on appel la fonction la 1ere fois : reste cst
                            maximise : savoir si on maximise ou pas 
    
    Cas de base : 
        on a une profondeur de 0 à regarder donc fini

    sinon :
        soit on maximise et le joueur est joueur sinon c est other joueur,
        on regarde toutes les actions disponibles et on évalue en appelant recursivement en changeant le booléen maxi jusqu'a la bonne profondeur
        on revient à la situation du plateau avant l opération
        on met ensuite a jour alpha,beta, le meilleur coup et l'évaluation

    renvoie : un couple (score, meilleur coup)
    
    """
    if profondeur ==  0 :
        return (eval(Plateau,joueur),None)   #cas de base
    
    if maxi :   #tour de joueur 
        current = joueur
        value = -float("inf")   
        liste_actions = plateau.get_all_legal_actions(current)
        if not liste_actions:
            print("pas d actions dispo, looser")

        for act in liste_actions : 
            backup = plateau.apply_action(current, act)
            
            score,coup = alpha_beta(eval,plateau,profondeur - 1, alpha,beta,joueur,False)

            plateau.undo_action(current,backup)

            if score > value:
                value = score
                best = act

            alpha = max(alpha,value)
            if beta<=alpha :
                break

        return value,best

    else :  #tour de other player 
        current = Plateau.get_other_player(joueur)
        value = float("inf")
        liste_actions = plateau.get_all_legal_actions()
        if not liste_actions:
            print("pas d actions dispo, looser")

        for act in liste_actions : 
            backup = plateau.apply_action(current, act)
            
            score,coup = alpha_beta(eval,plateau,profondeur - 1, alpha,beta,joueur,True)

            plateau.undo_action(current,backup)

            if score < value:
                value = score
                best = act

            alpha = min(beta,value)
            if beta<=alpha :
                break

        return value,best
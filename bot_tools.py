from game import *





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
    if plateau.game_ended() :
        return (eval(joueur),None)
    

    if profondeur ==  0 :
        return (eval(joueur),None)   #cas de base
    
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
        current = joueur.plateau.get_other_player(joueur)
        value = float("inf")
        liste_actions = plateau.get_all_legal_actions(current)

        if not liste_actions:
            print("pas d actions dispo, looser")

        for act in liste_actions : 
            backup = plateau.apply_action(current, act)
            
            score,coup = alpha_beta(eval,plateau,profondeur - 1, alpha,beta,joueur,True)

            plateau.undo_action(current,backup)

            if score < value:
                value = score
                best = act

            beta = min(beta,value)
            if beta<=alpha :
                break

        return value,best


#TODO verifier les g=0 c'est probablement des 1 surement
def a_star_shortest_path(joueur):
        start = joueur.case

        # chaque element = (f, g, current, path_taken)
        # g = distance entre départ et current
        # f = g + h (Manhattan distance)
        
        priority_queue = [(0 + manhattan_distance_to_goal(start, joueur), 0, start, [start])]
        visited = {
            start: 0
        }

        while len(priority_queue) > 0:
            f, g, current, path = heapq.heappop(priority_queue)

            if current in joueur.goal:
                return path[1::] #on retourne le chemin sans la position de départ

            neighbors = []


            if g == 0: #si c'est le premier tour faut prendre en compte la position de l'adversaire
                neighbors = joueur.plateau.get_accessible_cases(joueur)
            else: #on s'occupe pas du joueur adverse psk tfacon il va bouger
                neighbors = current.get_accessible_neighbors()

            for neighbor in neighbors:
                if neighbor not in visited or g + 1 < visited[neighbor]: #on update le voisin si on trouve un chemin plus court vers lui
                    visited[neighbor] = g + 1
                    h = manhattan_distance_to_goal(neighbor, joueur)
                    heapq.heappush(priority_queue, (g + 1 + h, g + 1, neighbor, path + [neighbor]))
        
        return None #aucun chemin


def eval_a_star(joueur : Joueur):
        
        if joueur.case in joueur.goal:
            return +1000000000
        
        other = joueur.plateau.get_other_player(joueur)
        if other.case in other.goal:
            return -1000000000

        j_path = joueur.a_star_shortest_physical_path()
        other_path = other.a_star_shortest_physical_path()

        """if j_path is None:
            return -100000
        if other_path is None:
            return +100000"""

        #on veut le plus haut score :
        #on veut que NOTRE chemin soit petit, donc négatif pour que l'éval diminue s'il s'allonge
        #on veut que le chemin de l'adversaire soit grand, donc positif pour que l'éval augmente s'il s'allonge
        #pondéré comme ça c'est plus important d'avoir son propre chemin court (strat offensive)
        return -1.5*len(j_path) + len(other_path) 

def eval_manhattan(joueur: Joueur):
    other = joueur.plateau.get_other_player(joueur)
    return -manhattan_distance_to_goal(joueur.case,joueur) + manhattan_distance_to_goal(other.case,other)

def alpha_beta_less_move(eval ,plateau : Plateau ,profondeur : int,alpha : int,beta : int, joueur : Joueur, maxi : bool,debug = False):
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
    if plateau.game_ended() :
        return (eval(joueur),None)
    
    if profondeur ==  0 :
        return (eval(joueur),None)   #cas de base
    
    if maxi :   #tour de joueur 
        current = joueur
        value = -float("inf")   
        liste_actions = plateau.get_less_legal_actions(current)
        if debug :
            print(len(liste_actions))
        
        if not liste_actions:
            print("pas d actions dispo, looser")

        for act in liste_actions : 
            backup = plateau.apply_action(current, act)
            score,coup = alpha_beta_less_move(eval,plateau,profondeur - 1, alpha,beta,joueur,False,debug = False)

            plateau.undo_action(current,backup)

            if score > value:
                value = score
                best = act

            alpha = max(alpha,value)
            if beta<=alpha :
                break

        return value,best

    else :  #tour de other player 
        current = joueur.plateau.get_other_player(joueur)
        value = float("inf")
        liste_actions = plateau.get_less_legal_actions(current)
        if not liste_actions:
            print("pas d actions dispo, looser")

        for act in liste_actions : 
            backup = plateau.apply_action(current, act)
            
            score,coup = alpha_beta_less_move(eval,plateau,profondeur - 1, alpha,beta,joueur,True,debug = False)

            plateau.undo_action(current,backup)

            if score < value:
                value = score
                best = act

            beta = min(beta,value)
            if beta<=alpha :
                break

        return value,best
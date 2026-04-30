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
    if profondeur ==  0 :
        return (eval(joueur),None)   #cas de base
    
    if maxi :   #tour de joueur 
        current = joueur
        value = -float("inf")   
        liste_actions = plateau.get_all_legal_actions(current)
        print(len(liste_actions ))
        print()
        
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

def eval_a_star(joueur : Joueur):
        return -len(joueur.a_star_shortest_path()) + len(joueur.plateau.get_other_player(joueur).a_star_shortest_path()) 

def eval_manhattan(joueur: Joueur):
    other = joueur.plateau.get_other_player(joueur)
    return -manhattan_distance_to_goal(joueur.case,joueur) + manhattan_distance_to_goal(other.case,other)


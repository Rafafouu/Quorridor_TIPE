from game import *

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
        score = 0 
        score +=  -1.5*len(j_path)
        score += len(other_path)
        score += 0.25 * (joueur.barrieres - other.barrieres)
        #on veut le plus haut score :
        #on veut que NOTRE chemin soit petit, donc négatif pour que l'éval diminue s'il s'allonge
        #on veut que le chemin de l'adversaire soit grand, donc positif pour que l'éval augmente s'il s'allonge
        #pondéré comme ça c'est plus important d'avoir son propre chemin court (strat offensive)

        if joueur.previous_case is not None:
            if len(j_path) > 0 and j_path[0] == joueur.previous_case:
                score -= 40  # pénalise le fait de revenir en arrière
        return score 


def eval_stall(joueur: Joueur):
    if joueur.case in joueur.goal:
        return +1000000000
        
    other = joueur.plateau.get_other_player(joueur)
    if other.case in other.goal:
        return -1000000000

    j_path = joueur.a_star_shortest_physical_path()
    other_path = other.a_star_shortest_physical_path()

    score = 0
    score += -len(j_path)
    score += 2*len(other_path)
    score += 0.1 * (joueur.barrieres - other.barrieres)
    if joueur.previous_case is not None:
        if len(j_path) > 0 and j_path[0] == joueur.previous_case:
            score -= 40  # pénalise le fait de revenir en arrière
    return score


def eval_aggresive(joueur: Joueur):
    if joueur.case in joueur.goal:
        return +1000000000
        
    other = joueur.plateau.get_other_player(joueur)
    if other.case in other.goal:
        return -1000000000

    j_path = a_star_shortest_path(joueur)
    other_path = a_star_shortest_path(other)

    score = 0
    score = -3*len(j_path) + len(other_path) + 2 * (joueur.barrieres - other.barrieres)
    if joueur.previous_case is not None:
        if len(j_path) > 0 and j_path[0] == joueur.previous_case:
            score -= 40  # pénalise le fait de revenir en arrière
    return score


def eval_accessible_cases(joueur: Joueur):

    if joueur.case in joueur.goal:
        return 1000000000

    plateau = joueur.plateau
    other = plateau.get_other_player(joueur)

    if other.case in other.goal:
        return -1000000000
    
    j_path = a_star_shortest_path(joueur)
    o_path = a_star_shortest_path(other)

    j_len = len(j_path)
    o_len = len(o_path)

    score = 0
    score += -2.2 * j_len
    score +=  1.8 * o_len
    score += 0.25 * len(plateau.get_accessible_cases(joueur))
    score -= 0.25 * len(plateau.get_accessible_cases(other))
    score += 0.4 * (joueur.barrieres - other.barrieres)

    if joueur.previous_case is not None:
        if len(j_path) > 0 and j_path[0] == joueur.previous_case:
            score -= 40  # pénalise le fait de revenir en arrière


    return  score 

def eval_center(joueur: Joueur):

    if joueur.case in joueur.goal:
        return 1000000000

    plateau = joueur.plateau
    other = plateau.get_other_player(joueur)

    if other.case in other.goal:
        return -1000000000

    j_path = a_star_shortest_path(joueur)
    o_path = a_star_shortest_path(other)

    j_len = len(j_path)
    o_len = len(o_path)

    center_col = (plateau.dim - 1) / 2
    center_weight = 0.9 * (j_len / plateau.dim)

    score = 0
    score += -2.2 * j_len
    score +=  1.8 * o_len

    score += center_weight * (plateau.dim - abs(joueur.case.col - center_col))
    score -= center_weight * (plateau.dim - abs(other.case.col - center_col))

    score += 0.4 * (joueur.barrieres - other.barrieres)
    if joueur.previous_case is not None:
        if len(j_path) > 0 and j_path[0] == joueur.previous_case:
            score -= 40  # pénalise le fait de revenir en arrière
    return score






def eval_manhattan(joueur: Joueur):
    other = joueur.plateau.get_other_player(joueur)
    return -manhattan_distance_to_goal(joueur.case,joueur) + manhattan_distance_to_goal(other.case,other)







def eval_giga_smart(joueur: Joueur):

    other = joueur.plateau.get_other_player(joueur)

    if joueur.case in joueur.goal:
        return 1000000

    if other.case in other.goal:
        return -1000000


    my_path = a_star_shortest_path(joueur)
    opp_path = a_star_shortest_path(other)

    if my_path is None:
        return -10000

    if opp_path is None:
        return 10000

    my_dist = len(my_path)
    opp_dist = len(opp_path)

    score = 0


    # 1. le chemin adverse et le notre valent autant (très importants)
    score += 20 * (opp_dist - my_dist)






    # 2. TEMPO
    # à distance égale, celui qui joue est avantagé
    if my_dist == opp_dist:
        score += 3





    #3. Valeur des murs
    phase = my_dist + opp_dist

    # plus la fin approche, moins les murs valent
    wall_weight = max(0.3, phase / 20)

    score += wall_weight * 2 * (joueur.barrieres - other.barrieres)




    #4. tactique positionnelle
    # éviter les mouvements sur le coté inutiles
    center = joueur.plateau.dim // 2

    score -= 0.3 * abs(joueur.case.col - center)





    # 5. Encourager a gagner si on peut

    # encourage les positions quasi gagnantes
    score -= 3 * my_dist



    # 6. mode défensif

    # si l'adversaire est proche de gagner on l'empeche
    if opp_dist <= 3:
        score -= 15

    # 7. anti retour en arrière

    if joueur.previous_case is not None:
        if len(my_path) > 0 and my_path[0] == joueur.previous_case:
            score -= 40 

    return score
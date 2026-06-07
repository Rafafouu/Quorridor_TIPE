from game import *
import random
from bot_tools import *

#bouge au hasard, place aucune barriere
class RandomMoveBot(Joueur):

    def play(self):
        return self.try_move(random.choice(self.plateau.get_accessible_cases(self)))

class RandomBot(Joueur):
    def play(self):
        liste_actions = self.plateau.get_all_legal_actions(self)
        self.plateau.apply_action(self,random.choice(liste_actions))
        return True


class HumanBot(Joueur):
    def play(self):
        pass

        """if self.barrieres > 0:
            ans = int(input ("placer une barriere : 1 \n se déplacer : 2 \n votre choix : "))
            if ans == 1 : 
                vert = int(input("entrez 1 si vous voulez une barrière verticale : "))
                i = int(input("Entrez indice i (colonne) de la barrière : "))
                j = int(input("Entrez indice j (ligne) de la barrière : "))
                worked = self.try_place_wall(i, j, vert==1)

                if not worked:
                    print("barrière non valide")
                    return self.play()

            elif ans == 2 :
                moves = self.plateau.get_accessible_cases(self)
                for i in range(len (moves)) :
                    print(str(i) + " : ", moves[i].row, moves[i].col)
                ans = int(input("choose your case : "))
                self.try_move(moves[ans])    

            else:
                print( "bravo tu as cassé le game tu dois te sentir si fier de toi")
                return self.play()

        else : 
            moves = self.plateau.get_accessible_cases(self)
            for i in range(len (moves)) :
                print(str(i) + " : ", moves[i].row, moves[i].col)
            ans = int(input("choose your case : "))
            if ans > len(moves):
                return self.play()
            
            self.try_move(moves[ans])    
            return True"""


class AStarBot(Joueur):
    def play(self):
        path = a_star_shortest_path(self)
        if path:
            return self.try_move(path[1])
        return False


class AlphaBotSkeleton(Joueur): #squelette de bot pour les alpha beta, c'est juste joueur avec un attribut hauteur en plus
    def __init__(self, case, goal, plateau, hauteur, barrieres=BARRIERE_START):
        super().__init__(case, goal, plateau, barrieres=barrieres)
        self.hauteur = hauteur



class ASLBotSkeleton(AlphaBotSkeleton):
    pass


class ASBot(AlphaBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta(eval_a_star,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True
    
class AlphaManhattanBot(AlphaBotSkeleton): 

    def play(self):
        eval, act = alpha_beta(eval_manhattan,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True


class ASLMoveBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_a_star,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True
    
    
class AS2LMoveBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_less_move(eval_a_star,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act) 
        return True

class ASLStallBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_stall,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True
    
class ASStallBot(AlphaBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta(eval_stall,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True
    
class ASLAggressiveBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_aggresive,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True

class ASAggressiveBot(AlphaBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta(eval_aggresive,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True
    

class ASCenterBot(AlphaBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta(eval_center,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True
    
class ASLCenterBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_center,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True
    
class ASOpenSpacesBot(AlphaBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta(eval_accessible_cases,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True

class ASLOpenSpacesBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_accessible_cases,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True


class ASGigaSmartBot(AlphaBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta(eval_giga_smart,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True)
        self.plateau.apply_action(self,act)
        return True

class ASLGigaSmartBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_giga_smart,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True
    
class ASLSmartBot(ASLBotSkeleton):
    
    def play(self):
        eval, act = alpha_beta_less_move(eval_smart,self.plateau, self.hauteur, -float("inf"),float("inf"),self,True,False)
        self.plateau.apply_action(self,act)
        return True 
    


from game import *
import random
from bot_tools import *

#bouge au hasard, place aucune barriere
class RandomMoveBot(Joueur):

    def play(self):
        return self.try_move(random.choice(self.plateau.get_accessible_cases(self)))


#place toutes ses barrieres au hasard puis bouge au hasard
class RandomBot(Joueur):

    def place_random_barrier(self):
        i, j =  random.randint(0, self.plateau.dim-1), random.randint(0, self.plateau.dim-1),
        is_vertical = random.choice([True, False])

        ok = self.try_place_wall(i, j, is_vertical)
        while not ok:

            i, j =  random.randint(0, self.plateau.dim-1), random.randint(0, self.plateau.dim-1),
            is_vertical = random.choice([True, False])

            ok = self.try_place_wall(i, j, is_vertical)
        
        return ok

    def play(self):
        if self.barrieres > 0:
            return self.place_random_barrier()
        else:
            return self.try_move(random.choice(self.plateau.get_accessible_cases(self)))
        

class HumanBot(Joueur):
    def play(self):

        if self.barrieres > 0:
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
                return self.play
            
            self.try_move(moves[ans])    
            return True


class AStarBot(Joueur):

    #TODO bot qui utilise A* avec comme heuristique la distance de manhattan avec l'arrivée

    def play(self):
        path = a_star_shortest_path(self)
        if path:
            return self.try_move(path[0])
        return False

        
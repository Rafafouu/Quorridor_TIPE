from game import *
import random

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
        
class AStarBot(Joueur):
    
    #TODO bot qui utilise A* avec comme heuristique la distance de manhattan avec l'arrivée

    def play(self):
        pass
        
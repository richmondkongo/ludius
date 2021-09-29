from player import Player
# from board import Board
import random
import numpy as np
import pandas as pd
from datetime import datetime 
from time import sleep 

class IA(Player):

    #Team modify this
    name = "Luduis"
    
    def __init__(self,position, gameSize):
        print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
        Player.__init__(self,position, gameSize)
        self.player_index = 0 if self.playerColor == 'black' else 1


    def action_possible(self, board, step):
        """
        Donne l'ensemble des actions possibles d'un joueur donné
        """
        if step == 1:
            actions = list()
            for origin in self.getMovingPiece(board, self.playerColor):
                # on obtient la liste de tout les pions du joueur actuel qui peuvent bouger (les origines possibles) 
                for destination in self.getRealsMoves(board, origin[0], origin[1]):
                    # vu qu'on a les orignes on peut mtn pour chaque origine rechercher les des destinations possibles
                    actions.append((origin[0], origin[1], destination[0], destination[1]))
        else:
            # dans le cas où on est encore en mode pose de pion, tout ce qui est vide excepté le milieu est une potentielle action
            b = np.array(board)
            b[2, 2] = 'center' if (step == 0) else b[2, 2]

            # indice de toute les positions qui n'ont aucun pion
            vide = np.where(b == None)
            vide = list(zip(vide[0], vide[1]))
            actions = vide
        
        return actions

    
    def get_score(self, step, board):
        if step == 0:
            return (0, 0)
        else:
            b = np.array(board) 
            return (12-len(np.where(b == 'black')[0]), 12-len(np.where(b == 'white')[0]))
    

    #Rewrite the abstract method
    def play(self, dethToCover, board, step):
        # getName(): nom du joueur
        # getRealsMoves(board, 0, 0): tu lui donnes une position et il te dit quels sont tes pions qui peuvent atteindre ce point (toi seul)
        # getPossibleMoves(0, 0): tu lui donnes une position et il te retourne tout les voisins
        # playerColor: couleur du joueur
        # getMovingPiece(board, self.playerColor): # liste de mes pions qui peuvent bouger
        # getPlayerPiece(board): mes pièces actuels
        
        config = pd.read_hdf('data/config.h5')
        actions = self.action_possible(board=board, step=step)

        print(f'\n\n\n\n  ---{self.playerColor}({config.depth[0]})\nactions possibles:{actions}\n{np.array(board)}')
        if config.depth[0] == config.depth[config.shape[0]-1] and config.shape[0] > 1:
            # on vérifie si on est à l'état ou on s'est arrêté à la partie précédente
            config.width[0] = config.width[config.shape[0]-1]
        else:
            config.width[0] = 0
        config.to_hdf('data/config.h5', key='df', mode='w')
        config.to_csv('data/config.csv', sep=',')
        if config.depth[0] >= 139:
            print(f'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii:\n{config.depth[config.shape[0]-1]}')
            sleep(10)

        index_error = False
        try:
            actions[config.width[0]]
        except IndexError:
            index_error = True
        
        if not index_error:
            self.save_action(self.player_index, actions, step, board)

            if step == 0:
                # a, b = self.playRandom(board,step)
                a, b = actions[config.width[0]]
                return a, b
            elif step == 1:
                # a, b, c, d = self.playRandom(board, step)
                a, b, c, d = actions[config.width[0]]
                return a, b, c, d
        else:
            print("Problème indexe")
            sleep(10)

    

    def save_action(self, player, actions, game_step, board):
        # on sauvegarde l'état du jeu actuelle
        df = pd.read_hdf('data/data.h5')
        config = pd.read_hdf('data/config.h5')
        
        id = f'D{config.depth[0]}-W{config.width[0]}-P{player}-S{game_step}'
        try:
            # permet de donner l'id de son parent 
            parent = df.iloc[config.depth[0]-1].id
        except:
            parent = None

        if 1:
        #if (df[df.board.astype(str) == str(board)].shape[0] == 0):# and (df[df.action == actions[config.width[0]]].shape[0] == 0):
            # permet d'éviter d'enregistrer les états déjà existant
            #print(f'+++\t{df[df.board.astype(str) == str(board)]}')
            # on sauvegarde l'état si le board et les actions possibles n'existe pas déjà en base
            df = df.append({ 
                #'id': datetime.timestamp(datetime.now()),
                'id': id,
                'board': board, 
                'score': self.get_score(game_step, board), 
                'mvt': actions, 
                'action': actions[config.width[0]],
                'depth': config.depth[0],
                'width': config.width[0], 
                'player': player, 
                'step': game_step, 
                'winner': -1,
                'parent': parent
            }, ignore_index=True)

            df.to_hdf('data/data.h5', key='df', mode='w')
            df.to_csv('data/jeu.csv', sep=',') 

        config.depth[0] += 1
        config.to_hdf('data/config.h5', key='df', mode='w')
        config.to_csv('data/config.csv', sep=',')

        #if config.depth[0]-1 == config.depth[config.shape[0]-2] and config.shape[0] > 1:
        #        print(f'+++{config}')
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


    #Rewrite the abstract method
    def play(self, dethToCover, board, step):
        # getName(): nom du joueur
        # getRealsMoves(board, 0, 0): tu lui donnes une position et il te dit quels sont tes pions qui peuvent atteindre ce point (toi seul)
        # getPossibleMoves(0, 0): tu lui donnes une position et il te retourne tout les voisins
        # playerColor: couleur du joueur
        # getMovingPiece(board, self.playerColor): # liste de mes pions qui peuvent bouger
        # getPlayerPiece(board): mes pièces actuels
        
        config = pd.read_hdf('data/config.h5')
        actions = self.action_possible(board=board, color=self.playerColor, step=step)

        print(f'\n\n\n\n  ---{self.playerColor}({config.depth[0]})\nactions possibles:{actions}')
        if config.depth[0] == config.depth[config.shape[0]-1] and config.shape[0] > 1:
            config.width[0] = config.width[config.shape[0]-1]
            config.to_hdf('data/config.h5', key='df', mode='w')
            print(f'----------on y est: {config}')
            #sleep(10)

        self.save_action(self.player_index, actions, step, board)
        if step == 0:
            # a, b = self.playRandom(board,step)
            a, b = actions[config.width[0]]
            return a, b
        elif step == 1:
            # a, b, c, d = self.playRandom(board, step)
            a, b, c, d = actions[config.width[0]]
            return a, b, c, d

    
    def action_possible(self, board, color, step):
        """
        Donne l'ensemble des actions possibles d'un joueur donné
        """
        b = np.array(board)
        b[2, 2] = 'center' if (step == 0) else b[2, 2]

        # indice de toute les positions qui n'ont aucun pion
        vide = np.where(b == None)
        vide = list(zip(vide[0], vide[1]))

        if step == 1:
            actions = list()
            for origin in self.getMovingPiece(board,self.playerColor):
                for destination in self.getRealsMoves(board,origin[0],origin[1]):
                    actions.append((origin[0], origin[1], destination[0], destination[1]))
        else:
            # dans le cas où on est encore en mode pose de pion, tout ce qui est vide excepté le milieu est une potentielle action
            actions = vide
        
        return actions
    

    def save_action(self, player, actions, game_step, board):
        df = pd.read_hdf('data/data.h5')
        config = pd.read_hdf('data/config.h5')
        id = f'D{config.depth[0]}-W{config.width[0]}-P{player}-S{game_step}'
        try:
            parent = df.iloc[config.depth[0]-1].id
        except:
            parent = None
        #if df.iloc[np.where(list_id == id)[0]].shape[0] == 0:

        if (df[df.board.astype(str) == str(board)].shape[0] == 0) and (df[df.action == actions[config.width[0]]].shape[0] == 0):
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

            #nb_child = len(df[df.parent == df.iloc[config.depth[0]].id])
            # config = pd.DataFrame({ 'depth': [config.depth[0]+1], 'width': [config.width[0]] })
            config.depth[0] += 1
            config.to_hdf('data/config.h5', key='df', mode='w')
            config.to_csv('data/config.csv', sep=',')

    

    def move(self, step):
        self.df = pd.read_hdf('data/data.h5')
        config = pd.read_hdf('data/config.h5')
        print(f'{self.df.shape}')
        action = self.df.iloc[config.depth[0]].mvt[config.width[0]]
        return action if step == 0 else (action[0][0], action[0][1], action[1][0], action[1][1])


    def playRandom(self, board,step):
        playable=[]
        if(step==0):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if self.canPlayHere(board,step,i,j):
                        playable.append((i,j))
            choix =playable[random.randint(0, len(playable)-1)]
            return choix[0],choix[1]
        if(step==1):
            origins=self.getMovingPiece(board,self.playerColor)
            origin=origins[random.randint(0, len(origins)-1)]
            destinations=self.getRealsMoves(board,origin[0],origin[1])
            destination=destinations[random.randint(0,len(destinations)-1)]
            #print(origin[0],origin[1],destination[0],destination[1])
            return (origin[0],origin[1],destination[0],destination[1])
        return -1
    
    
    def get_score(self, step, board):
        if step == 0:
            return (0, 0)
        else:
            b = np.array(board) 
            return (12-len(np.where(b == 'black')[0]), 12-len(np.where(b == 'white')[0]))
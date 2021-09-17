# Created by HaroldKS at 09/09/2018
import pickle, signal, copy
from functools import wraps
import errno
import os

import numpy as np
import pandas as pd
from datetime import datetime

class Trace:
    def __init__(self, board, names):
        self.initial_board = copy.deepcopy(board)
        self.names = names
        self.winner = -1
        self.actions = []
        self.score = [0,0] # est tjr égale à 0, ne jamais l'utiliser


    def add_action(self, player, action, game_step, board, score):
        pass


    def write(self):
        df = pd.read_hdf('data/data.h5')
        last = df.shape[0] - 1
        df.loc[last, 'winner'] = 0 if df.loc[last, 'score'][0] > df.loc[last, 'score'][1] else (1 if df.loc[last, 'score'][0] < df.loc[last, 'score'][1] else 2)
        df.to_hdf('data/data.h5', key='df', mode='w')
        df.to_csv('data/jeu.csv', sep=',')
        #print(df_)

    def action_possible(self, board, player, step):
        """
        Donne l'ensemble des actions possibles d'un joueur donné
        """
        color = 'black' if player == 0 else 'white'
        b = np.array(board)
        b[2, 2] = 'center' if (step == 0) else b[2, 2]

        # indice de toute les positions qui n'ont aucun pion
        vide = np.where(b == None)
        vide = list(zip(vide[0], vide[1]))
        #vide = [(2, 2)] if self.config.depth[0] == 23 else list(zip(vide[0], vide[1]))

        if self.config.depth[0] == 24:
            vide = [(2, 2)]
            b[2, 2] = None

        #if step == 1:
        if step == 1 or self.config.depth[0] == 24:
            # ici nous sommes dans le cas où tout les pions ont été posé, il reste à bouger les pions
            # vide représentera les destinations possibles, on cherche à présent les départs en voyant les pions actuels du présent joueur qui peuvent y accéder
            action = list()
            for v in vide:
                # cette recherche les positions aux alentours du point concerné
                alentour = self.alentour(v)
                for w in alentour:
                    # on sélectionne les pions du joueur actuel qui peuvent accéder à ce point
                    if b[w] == color:
                        action.append((w, v))
        else:
            # dans le cas où on est encore en mode pose de pion, tout ce qui est vide excepté le milieu une potentielle action
            action = vide
        
        return action
    
    def alentour(self, coords):
        """
        Donne l'ensemble des points valables (haut, bas, gauche, droit) d'un point dont les coordonnées sont passés en paramètre
        """
        x = coords[0]
        y = coords[1]
        al = list()
        gauche = (y-1) if (y-1) >= 0 else None 
        droit = (y+1) if (y+1) <= 4 else None
        bas = (x-1) if (x-1) >= 0 else None 
        haut = (x+1) if (x+1) <= 4 else None 
        if gauche != None:
            al.append((x, gauche))
        if droit != None:
            al.append((x, droit))
        if bas != None:
             al.append((bas, y))
        if haut != None:
            al.append((haut, y))
        return al

    def load_trace(self, f):
        p = pickle.load(open(f, 'rb'))
        return p

    def get_actions(self):
        return self.actions

    def get_last_board(self):
        if not self.actions:
            return self.initial_board
        else:
            return self.actions[-1]

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.setitimer(signal.ITIMER_REAL,seconds) #used timer instead of alarm
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wraps(func)(wrapper)
    return decorator
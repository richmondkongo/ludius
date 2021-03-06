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
        pass
        #print(df_)

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
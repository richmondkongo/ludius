import os
import numpy as np
import pandas as pd
from datetime import datetime

#if not os.path.exists("data/data.h5"): # or 1:
if not os.path.exists("data/data.h5") or 1:
    df = pd.DataFrame(columns=['id', 'board', 'score', 'mvt', 'action', 'depth', 'width', 'player', 'step', 'winner', 'parent'])
    df.to_hdf('data/data.h5', key='df', mode='w')

    config = pd.DataFrame({ 'depth': [0], 'width': [0] })
    config.to_hdf('data/config.h5', key='df', mode='w')
    config.to_csv('data/config.csv', sep=',')

tps = 0.000001
#tps = 2
#os.system('python ai_game_cli_timeout.py -ai0 ludius/ludius_ai.py -ai1 ia_player.py -s {}'.format(tps))
os.system('python ai_game_cli_timeout.py -ai0 ludius/ludius_ai.py -ai1 ludius/ludius_ai_2.py -s {}'.format(tps))

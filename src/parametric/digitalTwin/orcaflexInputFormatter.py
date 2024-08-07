#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 12:15:12 2023

@author: goharshoukat

format the input outputs from the raw data files from orcaflex
"""

import numpy as np
import pandas as pd
import os

tension = pd.read_excel('data/processing_barge_model_Results.xlsx', 'Resultslintensions').to_numpy()
line1 = tension[:,0::3]
line2 = tension[:,1::3]
line3 = tension[:,2::3]
offset = pd.read_excel('data/processing_barge_model_Results.xlsx', 'Resultsxy').to_numpy()
offset = offset[:,::2]
seaStates = pd.read_excel('data/processing_barge_model_Results.xlsx', 'SeaStates')

df = pd.DataFrame({'max_tension_1':np.nan, 'mean_tension_1':np.nan, 
                   'max_tension_2':np.nan, 'mean_tension_2':np.nan, 
                   'max_tension_3':np.nan, 'mean_tension_3':np.nan, 
                   'max_offset':np.nan, 
                   'mean_offset':np.nan, 
                   'Hs':seaStates['Wave height (m)'], 
                   'Tp':seaStates['wave period (Tp)']})

for i in range(len(df)):
    df.loc[i, 'max_tension_1'] = np.max(line1[:, i])
    df.loc[i, 'mean_tension_1'] = np.mean(line1[:, i])
    
    df.loc[i, 'max_tension_2'] = np.max(line2[:, i])
    df.loc[i, 'mean_tension_2'] = np.mean(line2[:, i])
    
    df.loc[i, 'max_tension_3'] = np.max(line3[:, i])
    df.loc[i, 'mean_tension_3'] = np.mean(line3[:, i])
    
    df.loc[i, 'max_offset'] = np.max(offset[:, i])
    df.loc[i, 'mean_offset'] = np.mean(offset[:, i])

df.to_csv('data/orcaflexFormatted.csv', index=False)

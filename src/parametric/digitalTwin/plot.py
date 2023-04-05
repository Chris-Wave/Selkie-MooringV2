#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:47:52 2022

@author: goharshoukat

script to generate plots of the original files

Generate plots from original CPT data
"""

import pandas as pd
import numpy as np
from glob import glob
import os
import matplotlib.pyplot as plt
##############################################################################

# %% read output from modelled data
#and remove the unnecessary folders in the directory.
#Sixteenth reconstruct results in test directory and then in the training dir
reconstructed = sorted(os.listdir('output/Model Evaluation/First Attempt/'))
if '.DS_Store' in reconstructed:
   reconstructed.remove('.DS_Store')

trainX = pd.read_csv('data/X-training.csv', dtype = str)
trainY = pd.read_csv('data/y-training.csv', dtype=str)
testX =  pd.read_csv('data/X-test.csv', dtype = str)
testY = pd.read_csv('data/Y-test.csv', dtype = str)
trainX = trainX.astype('float64')
trainY=trainY.astype('float64')
testX= testX.astype('float64')
testY= testY.astype('float64')

test_recons = {}
train_recons = {}


for mod in reconstructed:
    path = 'output/Model Evaluation/First Attempt/{}/'.format(mod)
    training_recons = pd.read_csv(path + 'reconstructed.csv')
    testing_recons = pd.read_csv(path + 'reconstructed_test.csv')
    test_recons[mod] = testing_recons
    train_recons[mod] = training_recons



for mod in train_recons:
    fig, ax = plt.subplots(ncols=4, nrows=2, figsize=(30,30))
    ax[0,0].scatter(train_recons[mod]['mean_tension_1'], trainX['mean_tension_1'])         
    ax[0,0].set_title('mean tension 1')
    
    ax[0,1].scatter(train_recons[mod]['max_tension_1'], trainX['max_tension_1'])         
    ax[0,1].set_title('max tension 1')
    
    ax[0,2].scatter(train_recons[mod]['mean_tension_2'], trainX['mean_tension_2'])         
    ax[0,2].set_title('mean tension 2')
    
    ax[0,3].scatter(train_recons[mod]['max_tension_2'], trainX['max_tension_2'])         
    ax[0,3].set_title('max tension 2')

    ax[1,0].scatter(train_recons[mod]['mean_tension_3'], trainX['mean_tension_3'])         
    ax[1,0].set_title('mean tension 3')
    
    ax[1,1].scatter(train_recons[mod]['max_tension_3'], trainX['max_tension_3'])         
    ax[1,1].set_title('max tension 3')
    
    ax[1,2].scatter(train_recons[mod]['mean_offset'], trainX['mean_offset'])         
    ax[1,2].set_title('mean offset')
    
    ax[1,3].scatter(train_recons[mod]['max_offset'], trainX['max_offset'])         
    ax[1,3].set_title('max offset')
    
    plt.savefig('output/Model Evaluation/plots/First Attempt/{}_training.png'.format(mod), dpi=300)
    plt.close()

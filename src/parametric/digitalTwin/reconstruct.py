#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 09:51:45 2022

@author: goharshoukat

Script does the following:
    1. Reloads models saved in a specific folder
    2. model evaluates data from input of test data
    3. Plots the data predictions
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

model_dir = os.listdir(r'Models/First Attempt/')
if '.DS_Store' in model_dir:
    model_dir.remove('.DS_Store') # remove hidden fiel from directory

trainX = pd.read_csv('data/X-training.csv', dtype = str)
trainY= pd.read_csv('data/y-training.csv', dtype=str)
testX =  pd.read_csv('data/X-test.csv', dtype = str)
trainX = trainX.astype('float64')
trainY=trainY.astype('float64')
testX= testX.astype('float64')

X = np.array(trainX[['max_tension_1', 'mean_tension_1', 'max_tension_2',
       'mean_tension_2', 'max_tension_3', 'mean_tension_3', 'max_offset',
       'mean_offset', 'Hs', 'Tp']].copy())
Y = np.array(trainY[['max_tension_1', 'mean_tension_1', 'max_tension_2',
       'mean_tension_2', 'max_tension_3', 'mean_tension_3', 'max_offset',
       'mean_offset']].copy())

##obtain the scalar for the training X values
scalar_trainer_X = MinMaxScaler(feature_range=(0,1))
trainX= scalar_trainer_X.fit_transform(X)
#obtain the scalar for the training Y values
scalar_trainer_Y = MinMaxScaler(feature_range=(0,1))
trainY = scalar_trainer_Y.fit_transform(Y)


#assign the columns of X as inputs for making predictions using the model
#this is for reconstructing the results of the training dataset
X1 = X[:, 0]       #max tension 1
X2 = X[:, 1]       #mean tension 1
X3 = X[:, 2]       #max tension 2
X4 = X[:, 3]       #mean tension 2
X5 = X[:, 4]       #max tension 3
X6 = X[:, 5]       #mean tension 3
X7 = X[:, 6]       #max offset
X8 = X[:, 7]       #mean offset
X9 = X[:, 8]       #Hs
X10 = X[:, 9]      #Tp

#this is for reconstructing the results of the training dataset
tX = np.array(testX[['max_tension_1', 'mean_tension_1', 'max_tension_2',
       'mean_tension_2', 'max_tension_3', 'mean_tension_3', 'max_offset',
       'mean_offset', 'Hs', 'Tp']].copy())
tX = scalar_trainer_X.transform(tX)
tX1 = tX[:, 0]       #max tension 1
tX2 = tX[:, 1]       #mean tension 1
tX3 = tX[:, 2]       #max tension 2
tX4 = tX[:, 3]       #mean tension 2
tX5 = tX[:, 4]       #max tension 3
tX6 = tX[:, 5]       #mean tension 3
tX7 = tX[:, 6]       #max offset
tX8 = tX[:, 7]       #mean offset
tX9 = tX[:, 8]       #Hs
tX10 = tX[:, 9]      #Tp

#Each ml model in the output will have 5 files reconstructed
for ml_model in model_dir:
    model = tf.keras.models.load_model('Models/First Attempt/' + ml_model)
    outdir = r'output/Model Evaluation/First Attempt/' + ml_model

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

#reconstrucct the results of training dataset to see how the models
#do against actual data
    
    results = model.predict(
    {
        'max_tension_1' : X1,
        'mean_tension_1': X2,
        'max_tension_2' : X3,
        'mean_tension_2' : X4,
        'max_tension_3' : X5,
        'mean_tension_3': X6,
        'max_offset' : X7,
        'mean_offset' : X8,
        'Hs' : X9,
        'Tp' : X10
    }
    )
    results = np.array(results)
    results = np.transpose(results[:,:,0])
    #rescale the test values as per the previous scalar_trainer_y
    results = scalar_trainer_Y.inverse_transform(results)
    df = pd.DataFrame({
        'max_tension_1':results[:,0], 'mean_tension_1':results[:,1], 
        'max_tension_2':results[:,2], 'mean_tension_2':results[:,3],
        'max_tension_3':results[:,4], 'mean_tension_3':results[:,5],
        'max_offset':results[:,6], 'mean_offset':results[:,7]
        })


    df.to_csv(outdir + '/reconstructed.csv',index = False)


#using the same model as above, reconstruct the entire library of data, including
#the training data to understand how the model performs on the training set
#using the same initial for loop.
    
    results = model.predict(
    {
        'max_tension_1' : tX1,
        'mean_tension_1': tX2,
        'max_tension_2' : tX3,
        'mean_tension_2' : tX4,
        'max_tension_3' : tX5,
        'mean_tension_3': tX6,
        'max_offset' : tX7,
        'mean_offset' : tX8,
        'Hs' : tX9,
        'Tp' : tX10
    }
    )
    results = np.array(results)
    results = np.transpose(results[:,:,0])
    #rescale the test values as per the previous scalar_trainer_y
    results = scalar_trainer_Y.inverse_transform(results)
    df = pd.DataFrame({
        'max_tension_1':results[:,0], 'mean_tension_1':results[:,1], 
        'max_tension_2':results[:,2], 'mean_tension_2':results[:,3],
        'max_tension_3':results[:,4], 'mean_tension_3':results[:,5],
        'max_offset':results[:,6], 'mean_offset':results[:,7]
        })
    outdir = r'output/Model Evaluation/First Attempt/' + ml_model + '/'
    
    if not os.path.isdir(outdir):
          os.mkdir(outdir)

    df.to_csv(outdir + '/reconstructed_test.csv', index=False)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 10:31:30 2022

@author: goharshoukat

Sixteenth model attempt

Only to understand how to use tensorflow
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers

import os
import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from customCallBack import PlotLearning
from model_definition import model_definition
#print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
###############################################################################
#import training dataset
trainX = pd.read_csv('data/X-training.csv', dtype = str)
trainY= pd.read_csv('data/y-training.csv', dtype=str)
trainX = trainX.astype('float64')
trainY=trainY.astype('float64')

X = np.array(trainX[['max_tension_1', 'mean_tension_1', 'max_tension_2',
       'mean_tension_2', 'max_tension_3', 'mean_tension_3', 'max_offset',
       'mean_offset', 'Hs', 'Tp']].copy())
Y = np.array(trainY[['max_tension_1', 'mean_tension_1', 'max_tension_2',
       'mean_tension_2', 'max_tension_3', 'mean_tension_3', 'max_offset',
       'mean_offset']].copy())

X, Y = shuffle(X, Y)
###############################################################################

# %% X and Y are scaled as per their independent
scalarX = MinMaxScaler(feature_range=(0,1))
X  = scalarX.fit_transform(X)


#scale tY wrt input Y matrix
scalarY = MinMaxScaler(feature_range=(0, 1))
Y = scalarY.fit_transform(Y)

###############################################################################
#training data
# divide all the inputs into seperate vectors
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

Y1 = Y[:, 0]       #max tension 1
Y2 = Y[:, 1]       #mean tension 1
Y3 = Y[:, 2]       #max tension 2
Y4 = Y[:, 3]       #mean tension 2
Y5 = Y[:, 4]       #max tension 3
Y6 = Y[:, 5]       #mean tension 3
Y7 = Y[:, 6]       #max offset
Y8 = Y[:, 7]       #mean offset

###############################################################################
#create the 4 different inputs that will feed into the model
input1 =  keras.Input(shape=(1,), name = 'max_tension_1')
input2 = keras.Input(shape=(1,), name = 'mean_tension_1')
input3 = keras.Input(shape = (1,), name = 'max_tension_2')
input4 = keras.Input(shape=(1, ), name = 'mean_tension_2')
input5 = keras.Input(shape = (1,), name = 'max_tension_3')
input6 = keras.Input(shape=(1, ), name = 'mean_tension_3')
input7 = keras.Input(shape = (1,), name = 'max_offset')
input8 = keras.Input(shape=(1, ), name = 'mean_offset')
input9 = keras.Input(shape = (1,), name = 'Hs')
input10 = keras.Input(shape=(1, ), name = 'Tp')
#merge the 4 inputs into one vector for matrix multiplication
merge = layers.Concatenate(axis = 1)([input1, input2, input3, input4,
                                      input5, input6, input7, input8, input9,
                                      input10])


#list of nodes in the model.

#call the model_definition function which has 4 different models
#the model also has optimizer information
model_def = model_definition()['models']
optim     = model_definition()['optimizers']
#optim = ['adam']
activationFunc = ['LeakyReLU']
attempt = 'First' #quantifies the different tweaks made.

#for activation in activationFunc:
#    for o in optim:
for mod in model_def:
    #make output folder to house the model files
    model_dir = r"Models/{} Attempt/{}/".format(attempt, mod)
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)

    n_nodes = model_def[mod] #variable to extract array with layers
    #implementation via for loops
    for index, nodes in enumerate(n_nodes):
        if index == 0:
            l = layers.Dense(nodes, activation=tf.keras.layers.LeakyReLU(alpha=0.1))(merge)
        #if index == 0 or index == 1 or index == 3 or index == 5 or index == 7:
        if index == 0 or index == 1:
            l = layers.Dropout(0.1)(l)
        l = layers.Dense(nodes, activation=tf.keras.layers.LeakyReLU(alpha=0.1),
                         kernel_regularizer=regularizers.L1L2(l1=1e-6, l2=1e-6),
                bias_regularizer=regularizers.L1(1e-6),
                activity_regularizer=regularizers.L1(1e-6))(l)





    #create the 2 outputs for the last layer
    output1 = layers.Dense(1, activation='linear', name = 'max_tension_1_out')(l)
    output2 = layers.Dense(1, activation='linear', name = 'mean_tension_1_out')(l)
    output3 = layers.Dense(1, activation='linear', name = 'max_tension_2_out')(l) 
    output4 = layers.Dense(1, activation='linear', name = 'mean_tension_2_out')(l)
    output5 = layers.Dense(1, activation='linear', name = 'max_tension_3_out')(l) 
    output6 = layers.Dense(1, activation='linear', name = 'mean_tension_3_out')(l)
    output7 = layers.Dense(1, activation='linear', name = 'max_offset_out')(l) 
    output8 = layers.Dense(1, activation='linear', name = 'mean_offset_out')(l)

    model = keras.Model(
        inputs = [input1, input2, input3, input4, input5, input6, input7, 
                  input8, input9, input10],
        outputs = [output1, output2, output3, output4, output5, output6, output7,
                   output8]
    )

    keras.utils.plot_model(model, model_dir + 'model.pdf', show_shapes=True)
    model.compile(
        optimizer = tf.keras.optimizers.Adam(),
        loss = {
            'mean_offset_out' : keras.losses.MeanSquaredError(),
            'max_offset_out' : keras.losses.MeanSquaredError(),
        },
    )

    model.summary()

    #create directory to save checkpoints
    checkpoint_path = model_dir


    #save weights at the end of each epoch
    batch_size = 2
    plt_callback = PlotLearning(model_dir) 
    model_save_callback = keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        monitor='loss',
        mode='min',
        save_best_only=True, period = 10)
    #provides access to loss etc
    #can be accessed via different keys
    #history.keys()
    history = model.fit(
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
        },
        {
            'max_tension_1_out' : Y1,
            'mean_tension_1_out': Y2,
            'max_tension_2_out' : Y3,
            'mean_tension_2_out' : Y4,
            'max_tension_3_out' : Y5,
            'mean_tension_3_out': Y6,
            'max_offset_out' : Y7,
            'mean_offset_out' : Y8,
        },
        validation_split = 0.1,

        batch_size=batch_size, epochs = 300, verbose=1, shuffle=True,
        callbacks=[plt_callback, model_save_callback]
    )



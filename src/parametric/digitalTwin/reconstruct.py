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


test_files = pd.read_csv('datasets/summary.csv', usecols=['test']).dropna()
train_files = pd.read_csv('datasets/summary.csv', usecols=['train'])

test_data_dict = {} #cache all test file data in a
train_data_dict = {} #added to validate performance on training data
#load the cpt data for each test file
data_dir = 'datasets/cpt_filtered_datasets/'
for file in test_files.test:
    test_data_dict[file] = pd.read_csv(data_dir + file)

for file in train_files.train:
    train_data_dict[file] = pd.read_csv(data_dir + file)
#above code on training data makes use of inidivual data files without noise
#the next few lines will make use of the entire training dataset with noise

#generate the MinMaxScaler from the trained data to fit this on to the testing
#data. creating a new scalar would add discrepancies and false predictions
train = pd.read_csv('datasets/train.csv', dtype = str)
train = train.astype('float64')

#trainX contains only the input for the trainer which will be used to
#scale the test file inputs

trainX = np.array(train[['Depth', 'lat', 'lng', 'bathymetry']].copy())
scalar_trainer_X = MinMaxScaler(feature_range=(0,1))
trainX  = scalar_trainer_X.fit_transform(trainX)

#obtain the scalar for the training Y values
scalar_trainer_Y = MinMaxScaler(feature_range=(0,1))
trainY = np.array(train[['Smooth qt', 'Smooth fs']].copy())
trainY = scalar_trainer_Y.fit_transform(trainY)


#Each ml model in the output will have 5 files reconstructed
for ml_model in model_dir:
    model = tf.keras.models.load_model('/Users/goharshoukat/Documents/GitHub/synthetic-CPT/Models/Sixteenth Attempt/Scaled/' + ml_model)
    outdir = r'output/Model Evaluation/Sixteenth Attempt/test/' + ml_model

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    for file in test_data_dict:
        df = test_data_dict[file]
        tX = np.array(df[['Depth', 'latitude', 'longitude', 'bathymetry']].copy())
        tX = scalar_trainer_X.transform(tX)
        tX1 = tX[:, 0]       #depth
        tX2 = tX[:, 1]       #lat
        tX3 = tX[:, 2]       #lng
        tX4 = tX[:, 3]       #bathy

        results = model.predict(
        {
        'depth' : tX1, 'lat' : tX2, 'lng' : tX3,
        'bathymetry' : tX4
        })
        results = np.array(results)
        results = np.transpose(results[:,:,0])
        #rescale the test values as per the previous scalar_trainer_y
        results = scalar_trainer_Y.inverse_transform(results)
        df2 = pd.DataFrame({'depth' : df['Depth'] ,
            'latitude' : df['latitude'], 'longitude' : df['longitude'],
            'qt' : results[:,0], 'fs':results[:,1]})


        df2.to_csv(outdir + '/reconstructed_{}.csv'.format(file[:-4]), index = False)


#using the same model as above, reconstruct the entire library of data, including
#the training data to understand how the model performs on the training set
#using the same initial for loop.
    for file in train_data_dict:
        df = train_data_dict[file]
        tX = np.array(df[['Depth', 'latitude', 'longitude', 'bathymetry']].copy())
        tX = scalar_trainer_X.transform(tX)
        tX1 = tX[:, 0]       #depth
        tX2 = tX[:, 1]       #lat
        tX3 = tX[:, 2]       #lng
        tX4 = tX[:, 3]       #bathy

        results = model.predict(
        {
        'depth' : tX1, 'lat' : tX2, 'lng' : tX3,
        'bathymetry' : tX4
        })
        results = np.array(results)
        results = np.transpose(results[:,:,0])
        #rescale the test values as per the previous scalar_trainer_y
        results = scalar_trainer_Y.inverse_transform(results)
        df2 = pd.DataFrame({'depth' : df['Depth'] ,
            'latitude' : df['latitude'], 'longitude' : df['longitude'],
            'qt' : results[:,0], 'fs':results[:,1]})

        #adjust the outdir for the training dataset
        outdir = r'output/Model Evaluation/Sixteenth Attempt/' + ml_model

        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        df2.to_csv(outdir + '/reconstructed_{}.csv'.format(file[:-4]), index = False)

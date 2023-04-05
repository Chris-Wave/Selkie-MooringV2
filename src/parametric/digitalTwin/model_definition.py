#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  8 09:52:02 2022

@author: goharshoukat

This script defines the different models and the two optimizers which will
be used


"""

import numpy as np

def model_definition():
    model1 = np.exp(np.linspace(2, 6, 5)).astype(int)
    model1 = np.append(model1, model1[::-1])
    model1 = np.delete(model1, 4)



    model2 = np.exp(np.linspace(3, 6, 4)).astype(int)
    model2 = np.append(model2, model2[::-1])
    model2 = np.delete(model2, 4)

    model3 = np.exp(np.linspace(4, 6, 3)).astype(int)
    model3 = np.append(model3, model3[::-1])
    model3 = np.delete(model3, 3)

    model4 = np.exp(np.linspace(5, 6, 2)).astype(int)
    model4 = np.append(model4, model4[::-1])
    model4 = np.delete(model4, 2)

    model5 = [np.array((np.exp(6))).astype(int)]

    models = {'Model1' : model1, 'Model2' : model2,
               'Model3' : model3, 'Model4' : model4,
               'Model5' : model5}
#    models = {'Model4' : model4,
#               'Model5' : model5}

    optimizers = ['adam']
    return {'models' : models, 'optimizers' : optimizers}

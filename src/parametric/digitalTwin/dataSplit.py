#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 16:27:56 2023

@author: goharshoukat

Script takes in the results from orcaFlexInputFormatter and selkieInputFormatter
and creates a 70-30% split
"""
import pandas as pd
from sklearn.model_selection import train_test_split
selkie=pd.read_csv('data/selkie-formatted.csv')
orcaflex=pd.read_csv('data/orcaflexFormatted.csv')

df = pd.merge(selkie, orcaflex, how='outer', suffixes=(' selkie', ' orcaflex'), on=('Hs', 'Tp'))
df.to_csv('data/combined-selkie-orcaflex-datapoints.csv')

# =============================================================================
# X = df[['Hs', 'Tp', 'max tension 1 selkie', 'mean tension 1 selkie', 
#           'max tension 2 selkie', 'mean tension 2 selkie', 
#           'max tension 3 selkie', 'mean tension 3 selkie', 'max offset selkie',
#           'mean offset selkie']]
# 
# =============================================================================
X = selkie
y = orcaflex
y = y.drop(['Hs', 'Tp'], axis=1)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42)


X_train.to_csv('data/X-training.csv')
X_test.to_csv('data/X-test.csv')
y_train.to_csv('data/y-training.csv')
y_test.to_csv('data/y-test.csv')

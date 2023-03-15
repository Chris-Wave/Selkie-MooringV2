#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 14:39:45 2023

@author: goharshoukat

function to extract load offset from the moorpy code and compare it with the 
orcaflex results
"""
import os
import numpy as np
import pandas as pd
import math
import Selkie_Mooring_ver102 as sm
from Selkie_Mooring_ver102 import static_forceV2
from utilities import orcaflex
def load_displacement_curve(mooring, line_elements = 41, max_iteration = 200, plot_on = False, out_direc = False):
    #Input
    #mooring : {} : dictionary passed on by mooring_definition function
    #needs to contain data on hydrodynbamic loading and static loading
    #line_elements : int : number of elements the mooring line needs to be divided into
    
    #Output
    #two items are output
    #1. data : dataframe : results of all the iterations
    #2. resolved System for the last iteration
    
    
    #Initialize values for design loop optimization
    rank = mooring['moorConfig']['moorType']['rank']
    num_lines= mooring['moorConfig']['min_num_legs']

    itr_num = 0 

    #initial rank of line properties to use, the user may set this to a higher number in order to skip lines with low weight/stiffness that don't provide enough stiffness for their models
    rank = 0

    #initialising empty results
    data = []
    Results_Detail = {}
    
    
# Loop to check if design is passing

    
    # Optimisation loops
    # Cat & taut: increase chain/line size until max reached, then add another mooring line and start at smallest chain/line size
    
    delta = 1
    x_min = -15
    x_max = 15+delta
    
    x_range = np.arange(x_min,x_max, delta)
    resolvedSystem = sm.Moor_CreateV2(mooring, num_lines, rank) #resolved system information
    resolvedSystem['ms'].bodyList[0].f6Ext = np.array([0, 0, 0, 0, 0, 0])
    
    Max_dynamic_tensions = np.zeros((1,num_lines))
    Anchor_force = np.zeros((2,num_lines,3))             
    Anchor_force_horz = np.zeros((num_lines))     
    Anchor_force_vert = np.zeros((num_lines))
    
    loading = pd.DataFrame({'x' : x_range, 'max-tension':np.nan, 'LineForces_FE':np.nan, 'LineForces_AC':np.nan,})
    for i in range(np.size(x_range)):
        
        resolvedSystem['ms'].bodyList[0].setPosition(np.array([x_range[i], 0, 0, 0, 0, 0]))
        resolvedSystem['ms'].bodyList[0].type = 1
        resolvedSystem['ms'].solveEquilibrium(tol=0.01, maxIter=5000)
        plot_on = 0
        if plot_on == 1:
             fig, ax = resolvedSystem['ms'].plot() 
        
        
        
        for Linei in range(num_lines):   
            Max_dynamic_tensions[0,Linei] = max(resolvedSystem['ms'].lineList[Linei].getLineTens())
            Anchor_force[0,Linei,:] = resolvedSystem['ms'].lineList[Linei].getEndForce(0)
            Anchor_force[1,Linei,:] = resolvedSystem['ms'].lineList[Linei].getEndForce(1)
            Anchor_force_horz[Linei] = math.sqrt(Anchor_force[0,Linei,0]**2+Anchor_force[0,Linei,1]**2)
            Anchor_force_vert[Linei] = Anchor_force[0,Linei,2]
            Line_position_temp = resolvedSystem['ms'].lineList[Linei].getLineCoords(0.0, 0)
            #flag for Chris. Check this out. 
            loading.loc[i, 'x'] = x_range[i]
            loading.loc[i, 'max-tension'] = Max_dynamic_tensions[0, Linei]
        

            temp_LineForces_FE, temp_LineForces_AC = orcaflex(x_range[i],mooring, resolvedSystem, num_lines,i)
            loading.loc[i, 'LineForces_FE'] =temp_LineForces_FE
            loading.loc[i, 'LineForces_AC'] =temp_LineForces_AC
        os.chdir(r'C:\GitHub\Mooring\src\parametric')
    return loading
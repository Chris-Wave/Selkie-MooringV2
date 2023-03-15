#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:46:23 2022

@author: goharshoukat


This file contains utilities functions designed to reduce clutter and nested
if else statements
"""
import os
import numpy as np
def cat_mooring(**kwargs):
    #Input
    #stud : str :  "studless" or "studlink"
    #grade : str :  options: "R4-RO4","R3s", "R3","RQ3-API","R5"

    #Output
    #dictionary containing information on mooring chain material, source and 
    #rank limit
    #rank limit : max number of chain types given in the tables
    
    config = {'Type' : 'Cat', 'moor_material' : 'chain', 'source' : 'Vrhof', 'rank_limit' : 62, 
           'stud' : 'studless', 'grade' : 'R3s'}
    config.update(**dict(zip(config.keys() & kwargs.keys(), map(kwargs.get, config.keys() & kwargs.keys()))))
    #config.update(kwargs)
    return config

def tau_mooring(**kwargs):
    #Input
    #angle : float : degrees, default value at 30, 
    #Output
    #dictionary containing information on mooring chain material, source and 
    #rank limit
    #rank limit : max number of chain types given in the tables
    config = {'Type' : 'Tau', 'moor_material' : 'polyester', 'source' : "BridonBekaert", 
            'rank_limit' : 25, 'angle' : 30}
    config.update(**dict(zip(config.keys() & kwargs.keys(), map(kwargs.get, config.keys() & kwargs.keys()))))
    return config

def invalid_mooring():
    raise Exception ("Invalid mooring type selected. Please choose either 'Cat' or 'Tau' ")
    
def moor_type(type_, args):
    #Input
    #type_ : str : user defined mooring type 1)'cat' or 2) 'tau'
    
    #Output
    #returns the proeprties of the type of moorign selected,
    #otherwise raises an exception with an error message
    args = args or {}

    type_ = type_.lower() #convert it into lower case letters just to be sure
    mooring = {'cat' : cat_mooring, 'tau' : tau_mooring}
    return mooring.get(type_, invalid_mooring)(**args)
# =============================================================================
# 
# 
# moorType = {
#     'Type' : 'Tau',
#     
#     'keyword args' : 
#        {
#             'angle' : 30, 
#            'stud' : 'studless',
#            'grade' : 'R3s',
#        }
#        }
# 
# moor_type(moorType['Type'], moorType['keyword args'])
# =============================================================================

def wec(**kwargs):
    config =  {'Type' : 'WEC'}
    config.update(**dict(zip(config.keys() & kwargs.keys(), map(kwargs.get, config.keys() & kwargs.keys()))))
    return config

#tec properties to be defined later
def tec(**kwargs):
    config = {
        'Type' : 'TEC',
        'Rotor Diameter' : None,
        'Thrust Coeff' : None
        }
    config.update(**dict(zip(config.keys() & kwargs.keys(), map(kwargs.get, config.keys() & kwargs.keys()))))
    return config

def box(**kwargs):
    config = {
        'shape' : 'Box', 
        'wet width' : None,
        'draft' : 10,
        'freeboard' : 10,
        'NemohFile' : 'test_Rectangle_07_03b'
        }
    config.update(**dict(zip(config.keys() & kwargs.keys(), map(kwargs.get, config.keys() & kwargs.keys()))))
    return config

def cyl(**kwargs):
    config = {
        'shape' : 'Cyl',
        'radius' : None,
        'draft' : 10,
        'freeboard' : 10,
        'NemohFile' : 'test_Rectangle_07_03b'
        }
    config.update(**dict(zip(config.keys() & kwargs.keys(), map(kwargs.get, config.keys() & kwargs.keys()))))
    return config


def floatGeom(type_, geom, args):
    args = args or {}
    type_ = type_.lower()
    geom = geom.lower()
    
    props = {'wec' : wec, 'tec' : tec}
    config = props.get(type_)(**args)
 
    g_props = {'box' : box, 'cyl' : cyl}
    config2 = g_props.get(geom)(**args)

    return {'Converter' : config, 'Geometry' : config2}









# =============================================================================
# def fn(type_, *args:None, **kwargs:{}):
#     mooring = {'cat' : cat_mooring, 'tau' : tau_mooring}
#     print(kwargs)
#     return mooring.get(type_, invalid_mooring)(*args)    
# 
# fn('cat', 'studless', 'R2')
# 
# 
# 
# =============================================================================
def mkdir(path):
    #function to check if folder exists. if not, creates it
    #no return
    if not os.path.isdir(path):
        os.makedirs(path)
        
def output(outdirec, Moor_System_Return, dataframe, plot_on = True):
    #ensure directory exists
    mkdir(outdirec)
    
    #dump the dataframe
    dataframe.to_csv(outdirec + '/results.csv')
    Moor_System_Return.unload(outdirec + '/system_return.txt')
    
    if plot_on:
        fig, ax = Moor_System_Return.plot(color='red')   
        
# =============================================================================
#     
# def box_type():
#     #returns the shape type - 'box'
#     return 'Box'
#     
# def cyl_type():
#     #returns the shape type - 'cyl' for cylinder type
# def wec_type():
#     #returns the float type 
# def floatType(name):
#     #Input
#     #takes a string input
#     #options are 'WEC' or 'TEC'
#         
#     
# =============================================================================


# =============================================================================
# Angle between lines in a leg
# =============================================================================
def bisector(lines, leg_angle, line_angle):
    
    left = int(lines / 2)
    right = left
    
    rightAng = np.zeros((right,1))
    rightAng = [line_angle*(i+1) - line_angle/2 for i in range(right)]
    rightAng = [leg_angle - i  for i in rightAng]

    lefttAng = np.zeros((left,1))
    leftAng = [line_angle*(i) + line_angle/2 for i in range(left)]
    leftAng = [leg_angle + i  for i in leftAng]
    
    return np.matrix.flatten(np.array([rightAng, leftAng]))

def angleGenerator(lines, leg_angle, line_angle = 2):
    #input
    #lines : int : number of lines per leg
    line_angle = np.deg2rad(line_angle)
    line_angle = (line_angle)
    if (lines > 1) & (lines % 2 == 0):
        left = int(lines / 2)
        right = left
        
        rightAng = np.zeros((right,1))
        rightAng = [line_angle*(i+1) - line_angle/2 for i in range(right)]
        rightAng = [leg_angle - i  for i in rightAng]

        lefttAng = np.zeros((left,1))
        leftAng = [line_angle*(i) + line_angle/2 for i in range(left)]
        leftAng = [leg_angle + i  for i in leftAng]
        angle = np.matrix.flatten(np.array([rightAng, leftAng]))
    elif (lines>1) & (lines % 2  != 0 ):
        lines = lines - 1
        left = int(lines / 2)
        right = left
        
        rightAng = np.zeros((right,1))
        rightAng = [line_angle*(i+1) for i in range(right)]
        rightAng = [leg_angle - i  for i in rightAng]

        lefttAng = np.zeros((left,1))
        leftAng = [line_angle*(i+1) for i in range(left)]
        leftAng = [leg_angle + i  for i in leftAng]
        angle = np.matrix.flatten(np.array([rightAng, leftAng]))
        angle = np.append(angle, leg_angle)
    else:
        angle = [leg_angle]
    return angle    
        
#angle = angleGenerator(5, 135, line_angle=2)
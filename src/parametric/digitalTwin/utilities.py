#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:46:23 2022

@author: goharshoukat


This file contains utilities functions designed to reduce clutter and nested
if else statements
"""
import os
import matplotlib.pyplot as plt
import numpy as np

def orcaflex(x,mooring, resolvedSystem, num_lines,itr_num, angle=0):
    fair_radius = mooring['moorConfig']['fair_radius'] #to save space below, variable created
    fair_draft = mooring['moorConfig']['fair_draft'] #to save space below, variable created
    # need to add Pos_Anc and Pos_Fair to the new loops which create the MoorPy connections
    anc_radius= mooring['moorConfig']['moorType']['anchor_radius']
    total_lines = num_lines * mooring['moorConfig']['lines_per_leg']
    Pos_Anc = np.array([anc_radius*np.cos(angle), anc_radius*np.sin(angle), np.ones(total_lines)*-resolvedSystem['ms'].depth], dtype=float)
    Pos_Fair = np.array([fair_radius*np.cos(angle), fair_radius*np.sin(angle), np.ones(total_lines)*-fair_draft], dtype=float)
    
        
    os.chdir("C:/Program Files (x86)/Orcina/OrcaFlex/11.3/OrcFxAPI/Python")
    import OrcFxAPI
    
    #Note, OrcaFlex model should be set up with normal SI Units, Kg,m and N, not the default kN. Go to OF General tapp to set
    model = OrcFxAPI.Model(r'\\server\users\cwright\Documents\GDG\Hydrodynamics\WaveForce\OrcaWave\Rectangle_Base_Case.dat')
    environment = model.environment
    environment.Depth = mooring['Environment']['depth']
    linetype = model['Linetype1']
    if mooring['moorConfig']['moorType']['Type'] == "Cat":
        linetype.MassPerUnitLength = resolvedSystem['ms'].lineTypes['chain'].mlin 
        linetype.EA = resolvedSystem['ms'].lineTypes['chain'].EA
        linetype.OD = 1.8*resolvedSystem['ms'].lineTypes['chain'].input_d  #1.8 stud vs 1.9? studless add if statment here
        linetype.ID = 0
        linetype.EIx = 0 #No bending stiffness
        linetype.GJ = 0 #No torsional stiffness
    elif mooring['moorConfig']['moorType']['Type'] == "Tau":
        linetype.MassPerUnitLength = resolvedSystem['ms'].lineTypes['polyester'].mlin 
        linetype.EA = resolvedSystem['ms'].lineTypes['polyester'].EA
        linetype.OD = resolvedSystem['ms'].lineTypes['polyester'].input_d 
        linetype.ID = 0
        linetype.EIx = 0 #No bending stiffness
        linetype.GJ = 0 #No torsional stiffness
    
    line_length = mooring['moorConfig']['moorType']['line_length']
    for Linei in range(0,num_lines):  
        line = model.CreateObject(OrcFxAPI.otLine, 'Line'+str(1+Linei))
        
        line.EndAConnection = 'WEC'
        line.EndBConnection = 'Anchored'
        line.EndAX =  Pos_Fair[Linei]
        line.EndBX =  Pos_Anc[Linei]
        line.EndAY =  0
        line.EndBY =  0
        line.EndAZ =  Pos_Fair[Linei]
        line.EndBZ =  0 # Anchored is referenced with regard to sea floor ### Pos_Anc[2,Linei]    
        line.Length[0] = line_length
        
        #Lay azimuth only required if using soil friction
        #line.LayAzimuth = -180+angle[Linei]*180/math.pi #OrcaFlex Coord system
        line.StaticsSeabedFrictionPolicy= 'None'
        line.TargetSegmentLength[0] = 1
    
    model.CalculateStatics()
    vessel = model['WEC'] #vessel name in this example
    vessellist = (vessel,) # if calculating for a single vessel, the comma is required to define it as a tuple / list

    
    #This next code calculates the mooring stiffness matrix at the unload and meanlaoded positions
    #using both OrcaFlex's FEM and ANalytical Methods mooring solvers
    
    #OrcaFlex finite element linearised stiffness matrix
    Kbody_0_OF_FEM = OrcFxAPI.CalculateMooringStiffness(vessellist)
    
    #OrcaFlex apply mean load
    vessel.IncludedInStatics = 'None'
    vessel.IncludeAppliedLoads ='No'
    #vessel.NumberOfLocalAppliedLoads = 0

    vessel.InitialX = x


    model.SaveData(r'C:\GitHub\Mooring\src\parametric\laoding\MyFile_FE{}.dat'.format(itr_num))
 
    model.CalculateStatics()
    #OrcaFlex finite element linearised stiffness matrix
    LineForces_FE = line.TimeHistory("Effective Tension", None, OrcFxAPI.oeEndA)
    

    #OrcaFlex analyticial catenerary linearised stiffness matrix
    
    for Linei in range(0,num_lines): 
        line = model['Line'+str(1+Linei)]
        line.Representation = 'Analytic catenary' #default was Finite element; 
    
    model.CalculateStatics()

    
    model.SaveData(r'C:\GitHub\Mooring\src\parametric\laoding\\MyFile_AC{}.dat'.format(itr_num))
    
    model.CalculateStatics()
    
    LineForces_AC = line.TimeHistory("Effective Tension", None, OrcFxAPI.oeEndA)
    
    return  LineForces_FE, LineForces_AC
  
def cat_mooring(**kwargs):
    #Input
    #stud : str :  "studless" or "studlink"
    #grade : str :  options: "R4-RO4","R3s", "R3","RQ3-API","R5"

    #Output
    #dictionary containing information on mooring chain material, source and 
    #rank limit
    #rank limit : max number of chain types given in the tables
    
    config = {'Type' : 'Cat', 'moor_material' : 'chain', 'source' : 'Vrhof', 
              'rank' :1, 'line_length' : 10, 'anchor_radius' : 3,'rank_limit' : 62, 
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
            'rank_limit' : 25, 'angle' : 30, 'rank' :1, 'line_length' : 10, 
            'anchor_radius' : 3}
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


def mkdir(path):
    #function to check if folder exists. if not, creates it
    #no return
    if not os.path.isdir(path):
        os.makedirs(path)
        
def output(outdirec, Moor_System_Return, dataframe, length, radius, plot_on = True, window=True):
    #ensure directory exists
    mkdir(outdirec)
    
    #dump the dataframe
    dataframe.to_csv(outdirec + '/results.csv')
    Moor_System_Return.unload(outdirec + '/system_return.txt')
    
    if plot_on:
        fig, ax = Moor_System_Return.plot(color='red')   
        ax.set_title('length: {}, radius: {}'.format(length, radius))  
        plt.savefig(outdirec+'/l-{} r-{}.png'.format(length, radius), dpi = 300)
        if not window: 
            plt.close()

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
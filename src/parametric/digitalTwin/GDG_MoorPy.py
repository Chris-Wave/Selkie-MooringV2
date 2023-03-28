 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 16:40:48 2022

@author: goharshoukat


"""
import numpy as np
import pandas as pd
import math
import Selkie_Mooring_ver102 as sm
from Selkie_Mooring_ver102 import static_forceV2
from utilities import moor_type
import matplotlib.pyplot as plt
   
def mooring_definition(moorConfig, environment,
                       nemohFile = 'test_Rectangle_07_03b',
                       ):

    #inputs 
    #moorConfig : {} : dictionary of information on mooring configuration
    #mass_dict : dict : dictionary containing mass and intertia terms
    #environment : dict : dictionary item containing environment variables
    #moorType : str : 1) 'Cat' or 2) 'Tau'
    #Loads BridonBekaert polyester line properties and outputs table of EA at varying tensions
    #moorLineDataFile : str : path to the data file + file name with information on the mooring data
    #default set incase of testing
    #the default values of the files have been setup already
    #MoorLine_Data = np.genfromtxt(moorLineDataFile, delimiter=',')
    
        
    #Extract the hydrodynamic response
    Hydro = sm.LoadNEMOHV2(nemohFile)
    
    mooring_type_props = moor_type(moorConfig['moorType']['Type'], moorConfig['moorType']['keyword args'])
    environment['period'] = environment['Tp'] / 1.2 #add correct factor here
    environment['wave_height'] = environment['Hs'] / math.sqrt(2)
    #mass of system and inertia
    m = np.diag(np.array([Hydro['mass'], Hydro['mass'], Hydro['mass'],
                          Hydro['Ixx'], Hydro['Iyy'],Hydro['Izz']]))


    #mooring line configuration updated
    moorConfig['m'] = m
    moorConfig['moorType'] = mooring_type_props  
    
    #Calculate the static forces on the system
    Mean_Force = static_forceV2(moorConfig, environment)
    print("Body mean force is {}".format(Mean_Force))
 

    
    return {'Mean_Force' : Mean_Force, 'Hydrodynamic_forces' : Hydro, 
            'moorConfig' : moorConfig, 'Environment' : environment}

def solver(mooring, line_elements = 41, max_iteration = 200, plot_on = False, out_direc = False):
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
    
    resolvedSystem = sm.Moor_CreateV2(mooring, num_lines, rank) #resolved system information
    
    #Check if surge and sway mean offsets are in allowable limit
    if max(resolvedSystem['Mean_offset'][0:2]) * mooring['moorConfig']['SF_Offset'] < mooring['moorConfig']['offset_limit_mean']: 
        Mean_offset_check = 1
    else: 
        Mean_offset_check = 0
    #Hydrodynamic properties updated by adding terms frm resolved system
    mooring['Hydrodynamic_forces']['m'] = mooring['moorConfig']['m']
    mooring['Hydrodynamic_forces']['K_m'] = resolvedSystem['Kbody_mean_force']
    mooring['Hydrodynamic_forces']['Badd'] = mooring['moorConfig']['Badd']
    mooring['Hydrodynamic_forces']['DOF'] = mooring['moorConfig']['DOF']
    
    #Calculate RAOs
   #Calculate RAOs
    if mooring['Environment']['type']=='ISSC':
        WaveSpec = sm.ISSC_Create(mooring['Environment']['Hs'], 
                              mooring['Environment']['Tp'], freq_min=0.01, 
                              freq_max=10, freq_num=1000)
        
    elif mooring['Environment']['type'] == 'JONSWAP':
        tp = mooring['Environment']['Tp']
        Hs = mooring['Environment']['Hs']
        gamma = mooring['Environment']['gamma']
        WaveSpec = sm.jonswap(tp = tp, Hs=Hs, freqs= np.arange(0.01, 10.0, 10/1000),
                              gamma = gamma)
     
    Motion, RAO = sm.rao_calc(mooring['Hydrodynamic_forces'], WaveSpec)
    Motion['Mean_offset'] = resolvedSystem['Mean_offset']
    Motion['max_offset'] = Motion['Max_dynamic_motion'] + Motion['Mean_offset']
    Motion['max_offset'].resize(6)
    
    if plot_on: 
        plt.plot(WaveSpec['freq'],WaveSpec['S'])   
        plt.plot(RAO['omega'][:,0,0],RAO['rao'][:,0])
        plt.plot(WaveSpec['freq'],RAO['rao_WaveS'][:,0])
    #RAOs

    # Sets the vessel to max offset and solve the system equilibrium
    resolvedSystem['ms'].bodyList[0].setPosition(Motion['max_offset'])
    resolvedSystem['ms'].bodyList[0].type = 1
    resolvedSystem['ms'].solveEquilibrium(tol=0.01, maxIter=5000)
    
    if plot_on: 
        #fig, ax = Moor_System_Return.plot(color='red')   
        #plt.savefig('Test1_Maxoffset.png', dpi = 300)
        resolvedSystem['ms'].plot(colortension=True, cbar_tension=True)
        #plt.savefig('Test1_Maxoffset_T.png', dpi = 300)
        
    print(f"Body offset position at max offset is {np.round(Motion['max_offset'],2)}")
    
    Max_dynamic_tensions = np.zeros((1,num_lines))
    Anchor_force = np.zeros((2,num_lines,3))             
    Anchor_force_horz = np.zeros((num_lines))     
    Anchor_force_vert = np.zeros((num_lines))
     
    #Line_position_temp  = tuple() 
    depth_fair_seabed =mooring['Environment']['depth']-mooring['moorConfig']['fair_draft']
    line_length= mooring['moorConfig']['moorType']['line_length']
    anc_radius= mooring['moorConfig']['moorType']['anchor_radius']
    
    Line_position =  np.zeros((num_lines, 4, line_elements)) #41 is default number of line elements, change to variable later
    for Linei in range(num_lines):   
        Max_dynamic_tensions[0,Linei] = max(resolvedSystem['ms'].lineList[Linei].getLineTens())
        Anchor_force[0,Linei,:] = resolvedSystem['ms'].lineList[Linei].getEndForce(0)
        Anchor_force[1,Linei,:] = resolvedSystem['ms'].lineList[Linei].getEndForce(1)
        Anchor_force_horz[Linei] = math.sqrt(Anchor_force[0,Linei,0]**2+Anchor_force[0,Linei,1]**2)
        Anchor_force_vert[Linei] = Anchor_force[0,Linei,2]
        Line_position_temp = resolvedSystem['ms'].lineList[Linei].getLineCoords(0.0, 0)
        #flag for Chris. Check this out. 
        for modei in range(4):   
            Line_position[Linei,modei,:]=Line_position_temp[modei]


    if mooring['moorConfig']['moorType']['Type'] == "Cat":      
        MBL = resolvedSystem['ms'].lineTypes['chain'].MBL
        line_d = resolvedSystem['ms'].lineTypes['chain'].input_d
        Cost = num_lines * resolvedSystem['ms'].lineTypes['chain'].cost * \
            resolvedSystem['line_length'] # Cost per metre taken from DTOceanPlus_D5.6_Station
        if line_length > depth_fair_seabed:
            rmax = math.sqrt(line_length**2 - depth_fair_seabed**2)
            rmin = line_length - depth_fair_seabed
            if anc_radius > rmax or anc_radius < rmin:
                geometric_check = 0
            else:
                geometric_check = 1
        else:
            geometric_check = 0
            
    elif mooring['moorConfig']['moorType']['Type'] == "Tau":  
        MBL = resolvedSystem['ms'].lineTypes['polyester'].MBL
        line_d = resolvedSystem['ms'].lineTypes['polyester'].input_d
        Cost = num_lines * resolvedSystem['ms'].lineTypes['polyester'].cost * \
            resolvedSystem['line_length'] # Cost per metre taken from DTOceanPlus_D5.6_Station
        if line_length > depth_fair_seabed:
            rmax = math.sqrt(line_length**2 - depth_fair_seabed**2)
            if anc_radius > rmax:
                geometric_check = 0
            else:
                geometric_check = 1
        else:
            geometric_check = 0
        
    #Max line tension design check
  
    if max(max(Max_dynamic_tensions))*mooring['moorConfig']['SF_Offset'] < MBL: Max_dynamic_tensions_check = 1
    else: Max_dynamic_tensions_check = 0
    
  
    
    #Check if surge and sway max offsets are in allowable limit
    if max(Motion['max_offset'][0:2])*mooring['moorConfig']['SF_Offset'] < mooring['moorConfig']['offset_limit_total']: 
        Max_offset_check = 1
    else:
        Max_offset_check = 0
    
    #runs until all design checks pass
    time_period_test = sm.period_test(mooring['moorConfig']['Tn_limit'], mooring['moorConfig']['m'], 
                   mooring['moorConfig']['added_mass'], resolvedSystem['Kbody_0'])
    
    if time_period_test == 1:
        Period_check = 1
    else:
        Period_check = 0

    
    
    #appends results to dict,  t his nested dict indexing gets a bit messy tho.
    #Results_Detail["Run: {}".format(int(itr_num) )] = [Stiff, rank,Anchor_force_horz,Anchor_force_vert]
    
    #appends results, similair to anchor/foundaiton "dimensions"
    data.append([num_lines, line_d, round(resolvedSystem['line_length'], 2),
                 round(resolvedSystem['anc_radius'], 2),
                 max(Anchor_force_horz), max(Anchor_force_vert), Cost, 
                 Mean_offset_check, Max_offset_check, Max_dynamic_tensions_check,
                 geometric_check, Period_check])

    
    #the second output is for the last iteration only
    return (pd.DataFrame(data, 
            columns=['No. lines', 'diameter', 'Line length', 'Anchor Radius',
                     'Anc Horiz', 'Anc Vert', 'Cost', 'Mean offset', 
                     'Max offset','Max tensions', 'Geometry', 'Natural Period']), resolvedSystem['ms'])
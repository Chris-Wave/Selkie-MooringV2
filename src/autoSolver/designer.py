#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 14:48:54 2022

@author: cwright/gshoukat

This is the designer script. It borrows configuration definiton, input parameter
update and optimization functions from GDG_MoorPy.py, utilities.py and 
Selkie_Mooring_ver102.py

The script is based off of NREL's Moorpy repository
"""
import os
import numpy as np
from GDG_MoorPy import mooring_definition, optimizer
from utilities import output, floatGeom

"""
Environmental factors are input here
1. Hs : Significant wave height
2. Tp : peak wave period
3. wind_vel : velocity of wind
4. current_vel : current velocity
5. depth : bathymetry at the site
"""

# environment variables
Hs              = 5                                             #m
Tp              = 14                                            #s
wind_vel        = 20                                            #m/s
current_vel     = 2                                             #m/s
depth           = 45                                            #m
spectrum_type = 'JONSWAP' # option - 'JONSWAP', 'ISSC'

#following two parameters need to provided if JONSWAP spectrum is used
Hs = 1
gamma = 3.3

environment     = {
                   'type': spectrum_type, 
                   'Hs' : Hs, 'Tp' : Tp, 'wind_vel' : wind_vel,
                   'current_vel' : current_vel, 'depth' : depth, 
                   'gamma' : gamma, 'Hs' : Hs
                   }

# floating body variables
#The user can select which degrees of freedom to conisder for the dynamic part of the mooring design, select in order x,y,z,rx,ry,rz, 1 = on, 0 = off

"""
Define the degrees of freedom of the system. 
1 implies freedom
0 implies restriction
"""

DOF_X           = 1
DOF_Y           = 1
DOF_Z           = 0
DOF_RX          = 0
DOF_RY          = 0
DOF_RZ          = 0

#
DOF = np.array([DOF_X, DOF_Y, DOF_Z, DOF_RX, DOF_RY, DOF_RZ]) 
# Note that all 6DOF are included for static and mean offset position. total offset is mean offset + dynamic offset so still will have some components of other DOF  


"""
Platform geometry is defined here

float_type needs to be chosen from two available options
1. TEC  - Turbine Energy Converter
2. WEC - Wave Energy Converter

For the shape of the platform:
1. Box - Box shaped (rectangular or square cross section). The geometric arguments
needed for box type geomtry is:
    a. 'wet width'
2. Cyl - cylinderical (circular cross section)
    a. radius
    
The dictionary below specified parameters for both floater type and platform 
shape. Once the type and shpare are defined however,  only the relevant properties
will be processed and returned. The other properties can be ignored. 
"""

# Additional damping matrix
Badd            =np.zeros((6, 6))
Badd[3,3]       = 10000000
Badd[4,4]       = 400000000
Badd[4,4]       = 400000000

#added mass matrix 6 x 5
added_mass_infinite = np.zeros((6, 6)) 

#provie individual values for 6 Degrees. 
Tn_xx = 2
Tn_yy = 2
Tn_zz = 0
Tn_xy = 0
Tn_Rx = 0
Tn_Ry = 0
Tn_Rz = 0
Tn_limit = np.array([Tn_xx, Tn_yy, Tn_zz, Tn_Rx, Tn_Ry, Tn_Rz])
 

#natural period limit. 
#nemoh default file names goes in here. 
floater         = {
                    'Type' : "WEC", # WEC or TEC
                    'Shape' : "Box", # Cyl or Box
                    'kwargs' :
                        {
                            #tec parameter
                            'Thrust Coeff' : 0.2,
                            
                            #TEC parameter
                            'Rotor Diameter' : 4,
                            
                            #cylinder parameter
                            'radius' : 10,
                
                            #box parameter
                            'wet width' : 20,
                            
                            
                            #General Parameters
                            'draft' : 10,
                            
                            'freeboard' : 10,

                            
                            #Provide File name if default not used. 
                            'NemohFile' : os.path.abspath('../sampleGeometry/Default_Body_Cylinder')
                            }
                    }
    
    
floaterConfig   = floatGeom(floater['Type'], floater['Shape'], floater['kwargs'])



"""
Define morring type. two possibilities:
1. Cat - Catenary
2. Tau - Taut

If the Mooring type selected is 'Cat', further options for properties are:
    1. stud : 
        a. 'studlink'
        b. 'studless'
    2. grade : 
        a. 'R4-R04'
        b. 'R3s'
        c. 'R3'
        d. 'RQ3-API'
        e. 'R5'
    3. moor_material
        a. chain for Cat
        b. polyester for tau
    4. rank_limit
        a. 25 for tau
        b. 62 for Cat
        

All of the arguments can be changed to fit the need of the user. Please use the
format given below to adjust the values. You can add or delete values as per your
preference. 

If however, the type selected is 'Tau', taut angle needs to be defined:
    1. angle : default value of 30 deg
    2. moor_material
    3. source
    4. rank_limit

The equations below provide default settings for both catenary and taut type
moorings. When you chose either one of them, the other expressions can be ignored
They are provided for the ease of the user only to quickly alternate between 
the two types. 
"""

#if the mooring type is a catenary type, stud and grade need to be specified
#as per the options available above  
                      #angle of the taut mooring line anchor
moorType        = {
                    'Type' : 'Tau', #Tau
                    
                    'keyword args' : 
                       {
                           'stud' : 'studless',
                           'grade' : 'R3s',
                           'moor_material' : 'polyester', #or polyester for Tau, chain for Cat
                            'rank_limit' : 25,
                            'angle' : 30,
                            'source' : 'BridonBekaert', #Vrhof for Cat and "BridonBekaert" for taut
                       }
                   }

    
    
PreTen_Ratio     = 0.2                                              # Ratio of pretension to MBL
fair_radius      = 10                                               # m radius of fairleand from model centre
fair_draft       = 10                                               # m draft of fairleand from model centre

# design check limits
offset_limit_total  = 30                                            # m Total offset limit
offset_limit_mean   = 20                                            # m Mean offset limit

min_num_legs    = 3                                                 #number of mooring legs
lines_per_leg   = 2                                                #number of lines in each leg 
angle_between_lines = 2
SF_Moor         = 1.8                                              # NonDim #Tension
SF_Offset       = 1                                                # NonDim #Offset
itr_num_max     = 200

output_folder = 'Test' #adjust the naem as per own requirements. Folder needs not exist. Script will handle it. 




# =============================================================================
# Please do not change anything in the section below. 
# =============================================================================
moorConfig      = {'moorType' : moorType, 'DOF' : DOF, 
                   'floaterConfig' : floaterConfig,'draft' : floaterConfig['Geometry']['draft'], 
                   'freeboard' : floaterConfig['Geometry']['freeboard'], 'Badd' : Badd, 'added_mass' : added_mass_infinite,
                   'PreTen_Ratio' : PreTen_Ratio, 'fair_radius' : fair_radius, 
                   'fair_draft' : fair_draft, 'min_num_legs' : min_num_legs, 
                   'lines_per_leg' : lines_per_leg, 'angles_between_lines' : angle_between_lines,
                   'SF_Moor' : SF_Moor, 'SF_Offset' : SF_Offset,
                   'offset_limit_total' : offset_limit_total, 
                   'offset_limit_mean' : offset_limit_mean,
                   'Tn_limit' : Tn_limit}



#Foloowing function contains call to Nehoh data directory
#It is expecteed that the default file names are present
#and that the user does not alter the file names. 
#changes to filenames will require changes to the function loadNemohFunctionV2
#in a future iteration with OOP, this functionality will be provided
#user will be able to overwright default file names and default constant values
#for Selkie this is kept predefined and any changers will have to be made within
#the consituent functions
#mooring_definition makes use of loadNemohFunctionV2

#function returns a dictionary that updates the input parameters as well
#Env and Body will be updated. 

#nemoh file argument will come in here from the floater dict
mooring                 = mooring_definition(moorConfig, environment,
                                             nemohFile = floaterConfig['Geometry']['NemohFile'])
Results, systemReturn   = optimizer(mooring, max_iteration=itr_num_max)
output(output_folder, systemReturn, Results, plot_on = True)

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 14:05:21 2022

@author: cwright
"""


# Format taken from MoorPy's MoorProps

import numpy as np
import moorpy as mp
from Selkie_Mooring_ver102 import *

def getLinePropsFunSelkie(rank, type_, source, stud = 'studless', name="", grade = False):
    ''' 
    - This function requires at least one input: the line rank (0 is smallest available chain).
    - The rest of the inputs are optional: describe the desired type of line (chain, polyester, wire, etc.),
    the type of chain (studless or studlink), the source of data (Orcaflex-original or altered), or a name identifier
    - The function will output a MoorPy linetype object
    # Load Chain data from Vrhof brochure. Col 1: chain diameter (mm), Col 2:6, chain breaking load (kN) for grades R4-RO4,	R3s,R3,RQ3-API,R5. Col 7:8, mass for stud & studless (Kg)
'''
    
    if source=="Vrhof":
        #VrhofTable.csv has added hearder names so need to change input format here.
        Chain_Data = np.delete(np.genfromtxt(r'data/VrhofTable.csv', delimiter=','),0,0)
        if type_=="chain":
            #dmm = Chain_Data[rank,0]*1000
            dmm = Chain_Data[rank,0]
            
            d = dmm
            if grade=="R4-RO4":
                MBL = Chain_Data[rank,1]
            elif grade=="R3s":
                MBL = Chain_Data[rank,2]
            elif grade=="R3":
                MBL = Chain_Data[rank,3] 
            elif grade=="RQ3-API":
                MBL = Chain_Data[rank,4]
            elif grade=="R5":
                MBL = Chain_Data[rank,5] 
                
            
            if stud=="studless":
                massden = Chain_Data[rank,6]    #[kg/m]
                EA = 0.854e8*d**2*1000      #[N]
                d_vol = 1.8*d               #[m]
            elif stud=="studlink" or stud=="stud":
                massden = Chain_Data[rank,7]     #[kg/m]
                EA = 1.010e8*d**2*1000      #[N]
                d_vol = 1.89*d              #[m]
            else:
                raise ValueError("getLineProps error: Choose either studless or stud chain type ")
         # cost taken directly from MoorPy getlineProps functions
        # Derived from Equimar graph: https://tethys.pnnl.gov/sites/default/files/publications/EquiMar_D7.3.2.pdf
            if type_=="chain":
                cost = 1.5*massden             #[€/m]
            elif type_=="nylon" or type_=="polyester" or type_=="polypropylene":
                cost = (0.235*(MBL/9.81/1000))*1.29         #[$/m]
            elif type_=="wire" or type_=="wire-wire" or type_=="IWRC" or type_=='fiber' or type_=='wire-fiber':
                cost = (0.18*(MBL/9.81/1000) + 90)*1.29     #[$/m]
            else:
                raise ValueError("getLineProps error: Linetype not valid. Choose from given rope types or chain ")

    elif source=="BridonBekaert":
        #added hear names here so need to change this format
        Poly_Data = np.delete(np.genfromtxt(r'data/MoorLine.csv', delimiter=','), 0, 0)
        
        #Poly EA not needed anymore
        #Poly_EA = np.genfromtxt(r'data/BridonBekaert.csv',delimiter=',')
        d_vol = Poly_Data[rank,0]
        dmm = Poly_Data[rank,0]
        massden = Poly_Data[rank,1]
        MBL = Poly_Data[rank,3]
        EA = MBL/0.1378
        
        #Taken from MoorPy original, we'll need our own values here, or as user input
        cost = (0.235*(MBL/9.81))*1.29  
        
    elif source=="Orcaflex-original":
        d = dmm/1000  # orcaflex uses meters https://www.orcina.com/webhelp/OrcaFlex/
        
        if type_=="chain":
            c = 1.96e4 #grade 2=1.37e4; grade 3=1.96e4; ORQ=2.11e4; R4=2.74e4
            MBL = c*d**2*(44-80*d)*1000     #[N]  The same for both studless and studlink
            if stud=="studless":
                massden = 19.9*d**2*1000    #[kg/m]
                EA = 0.854e8*d**2*1000      #[N]
                d_vol = 1.8*d               #[m]
            elif stud=="studlink" or stud=="stud":
                massden = 21.9*d**2*1000    #[kg/m]
                EA = 1.010e8*d**2*1000      #[N]
                d_vol = 1.89*d              #[m]
            else:
                raise ValueError("getLineProps error: Choose either studless or stud chain type ")
        
        elif type_=="nylon":
            massden = 0.6476*d**2*1000      #[kg/m]
            EA = 1.18e5*d**2*1000           #[N]
            MBL = 139357*d**2*1000          #[N] for wet nylon line, 163950d^2 for dry nylon line
            d_vol = 0.85*d                  #[m]
        elif type_=="polyester":
            massden = 0.7978*d**2*1000      #[kg/m]
            EA = 1.09e6*d**2*1000           #[N]
            MBL = 170466*d**2*1000          #[N]
            d_vol = 0.86*d                  #[m]
        elif type_=="polypropylene":
            massden = 0.4526*d**2*1000      #[kg/m]
            EA = 1.06e6*d**2*1000           #[N]
            MBL = 105990*d**2*1000          #[N]
            d_vol = 0.80*d                  #[m]
        elif type_=="wire-fiber" or type_=="fiber":
            massden = 3.6109*d**2*1000      #[kg/m]
            EA = 3.67e7*d**2*1000           #[N]
            MBL = 584175*d**2*1000          #[N]
            d_vol = 0.82*d                  #[m]
        elif type_=="wire-wire" or type_=="wire" or type_=="IWRC":
            massden = 3.9897*d**2*1000      #[kg/m]
            EA = 4.04e7*d**2*1000           #[N]
            MBL = 633358*d**2*1000          #[N]
            d_vol = 0.80*d                  #[m]
        else:
            raise ValueError("getLineProps error: Linetype not valid. Choose from given rope types or chain ")
            
        
        
        # cost
        # Derived from Equimar graph: https://tethys.pnnl.gov/sites/default/files/publications/EquiMar_D7.3.2.pdf
        if type_=="chain":
            cost = (0.21*(MBL/9.81/1000))*1.29              #[$/m]
        elif type_=="nylon" or type_=="polyester" or type_=="polypropylene":
            cost = (0.235*(MBL/9.81/1000))*1.29         #[$/m]
        elif type_=="wire" or type_=="wire-wire" or type_=="IWRC" or type_=='fiber' or type_=='wire-fiber':
            cost = (0.18*(MBL/9.81/1000) + 90)*1.29     #[$/m]
        else:
            raise ValueError("getLineProps error: Linetype not valid. Choose from given rope types or chain ")



    elif source=="Orcaflex-altered":
        d = dmm/1000  # orcaflex uses meters https://www.orcina.com/webhelp/OrcaFlex/
        
        if type_=="chain":
            c = 2.74e4 #grade 2=1.37e4; grade 3=1.96e4; ORQ=2.11e4; R4=2.74e4
            MBL = (371360*d**2 + 51382.72*d)*(c/2.11e4)*1000 # this is a fit quadratic term to the cubic MBL equation. No negatives
            if stud=="studless":
                massden = 19.9*d**2*1000        #[kg/m]
                EA = 0.854e8*d**2*1000          #[N]
                d_vol = 1.8*d                   #[m]
            elif stud=="studlink" or stud=="stud":
                massden = 21.9*d**2*1000        #[kg/m]
                EA = 1.010e8*d**2*1000          #[N]
                d_vol = 1.89*d                  #[m]
            else:
                raise ValueError("getLineProps error: Choose either studless or stud chain type ")
                
            #cost = 2.5*massden   # a ballpark for R4 chain
            #cost = (0.58*MBL/1000/9.81) - 87.6          # [$/m] from old NREL-internal
            #cost = 3.0*massden     # rough value similar to old NREL-internal
            cost = 2.585*massden     # [($/kg)*(kg/m)=($/m)]
            #cost = 0.0
        
        elif type_=="nylon":
            massden = 0.6476*d**2*1000      #[kg/m]
            EA = 1.18e5*d**2*1000           #[N]
            MBL = 139357*d**2*1000          #[N] for wet nylon line, 163950d^2 for dry nylon line
            d_vol = 0.85*d                  #[m]
            cost = (0.42059603*MBL/1000/9.81) + 109.5   # [$/m] from old NREL-internal
        elif type_=="polyester":
            massden = 0.7978*d**2*1000      #[kg/m]
            EA = 1.09e6*d**2*1000           #[N]
            MBL = 170466*d**2*1000          #[N]
            d_vol = 0.86*d                  #[m]
            
            #cost = (0.42059603*MBL/1000/9.81) + 109.5   # [$/m] from old NREL-internal
            #cost = 1.1e-4*MBL               # rough value similar to old NREL-internal
            cost = 0.162*(MBL/9.81/1000)    #[$/m]
            
        elif type_=="polypropylene":
            massden = 0.4526*d**2*1000      #[kg/m]
            EA = 1.06e6*d**2*1000           #[N]
            MBL = 105990*d**2*1000          #[N]
            d_vol = 0.80*d                  #[m]
            cost = 1.0*((0.42059603*MBL/1000/9.81) + 109.5)   # [$/m] from old NREL-internal
        elif type_=="hmpe":
            massden = 0.4526*d**2*1000      #[kg/m]
            EA = 38.17e6*d**2*1000          #[N]
            MBL = 619000*d**2*1000          #[N]
            d_vol = 1.01*d                  #[m]
            cost = (0.01*MBL/1000/9.81)     # [$/m] from old NREL-internal
        elif type_=="wire-fiber" or type_=="fiber":
            massden = 3.6109*d**2*1000      #[kg/m]
            EA = 3.67e7*d**2*1000           #[N]
            MBL = 584175*d**2*1000          #[N]
            d_vol = 0.82*d                  #[m]
            cost = 0.53676471*MBL/1000/9.81             # [$/m] from old NREL-internal
        elif type_=="wire-wire" or type_=="wire" or type_=="IWRC":
            massden = 3.9897*d**2*1000      #[kg/m]
            EA = 4.04e7*d**2*1000           #[N]
            MBL = 633358*d**2*1000          #[N]
            d_vol = 0.80*d                  #[m]
            #cost = MBL * 900./15.0e6
            #cost = (0.33*MBL/1000/9.81) + 139.5         # [$/m] from old NREL-internal
            cost = 5.6e-5*MBL               # rough value similar to old NREL-internal
        else:
            raise ValueError("getLineProps error: Linetype not valid. Choose from given rope types or chain ")


    elif source=="NREL":
        '''
        getLineProps v3.1 used to have old NREL-internal equations here as a placeholder, but they were not trustworthy.
         - The chain equations used data from Vicinay which matched OrcaFlex data. The wire rope equations matched OrcaFlex well,
           the synthetic rope equations did not
           
        The idea is to have NREL's own library of mooring line property equations, but more research needs to be done.
        The 'OrcaFlex-altered' source version is a start and can change name to 'NREL' in the future, but it is
        still 'OrcaFlex-altered' because most of the equations are from OrcaFlex, which is the best we have right now.
        
        Future equations need to be optimization proof = no negative numbers anywhere (need to write an interpolation function)
        Can add new line types as well, such as Aramid or HMPE
        '''
        pass
        
    
    
    
    # Set up a main identifier for the linetype. Useful for things like "chain_bot" or "chain_top"
    if name=="":
        typestring = f"{type_}{dmm:.0f}"
    else:
        typestring = name
    
    
    notes = f"made with getLineProps - source: {source}"
    

    return mp.LineType(typestring, d_vol, massden, EA, MBL=MBL, cost=cost, notes=notes, input_type=type_, input_d=dmm)

# Import dependencies
import math
import numpy as np
import matplotlib.pyplot as plt
#os.chdir('C:\GitHub\MoorPy')
import moorpy as mp
from GetLinePropsSelkie import getLinePropsFunSelkie
import scipy.optimize
from utilities import angleGenerator

def LoadNEMOHV2(direc):
    #Input
    #direc : str : pathway to nemoh data folder
    fNEMOH = open(direc + '/Nemoh.cal', 'r')
    contentNEMOH = fNEMOH.read()
    
    omega_num = int(contentNEMOH.splitlines()[26].split()[0])
    omega_min = float(contentNEMOH.splitlines()[26].split()[1])
    omega_max = float(contentNEMOH.splitlines()[26].split()[2])
    
    omega2 = np.linspace(omega_min, omega_max, omega_num)
    omega = omega2.reshape(omega_num,1,1)
    omega.resize([omega_num,1,1], refcheck=True)
    
    #Hydrostatic stiffness
    k_h = np.loadtxt(direc + "/mesh/KH.dat", float)
    
    #raed in volume
    hydroFile = open(direc + '/mesh/Hydrostatics.dat', 'r')
    hydroFile = hydroFile.read().splitlines()[3:]
    displacement = float(hydroFile[0].split('=')[1])
    awp = float(hydroFile[1].split('=')[1])##
    m = displacement * 1024
    
    contentFE = np.loadtxt(direc + "/results/ExcitationForce.tec",skiprows=8, max_rows=omega_num)
    
    # excitation force amplitude and phase
    famp = np.copy(contentFE[:, 1::2])
    fphi = np.copy(contentFE[:, 2::2])
 
    fCB= open(direc + '/results/CA.dat', 'r')
    contentCB = fCB.read()
    
    #Added mass
    fCA= open(direc + '/results/CM.dat', 'r')
    contentCA = fCA.read()
    omega_cA = np.array([])
    cA  = np.empty((0,6), float)
        
    omega_cB = np.array([])
    cB  = np.empty((0,6), float)
    
    
    inertiaFile = open(direc + '/mesh/Inertia_hull.dat')
    inertiaFile = inertiaFile.read().splitlines()
    Ixx = float(inertiaFile[0].split(' ')[2])
    Iyy = float(inertiaFile[1].split(' ')[3])
    Izz = float(inertiaFile[2].split(' ')[-1])
    
    
    for freqi in range (0, omega_num):
        lineii = freqi * 7
        
        omega_cA = np.append(omega_cA, contentCA.splitlines()[lineii+1].split()[0])
        omega_cB = np.append(omega_cB, contentCB.splitlines()[lineii+1].split()[0])
        
        for linei in range (1, 7):
            
            cA = np.append(cA, np.float32(contentCA.splitlines()[lineii+1+linei].split()))
            cB = np.append(cB, np.float32(contentCB.splitlines()[lineii+1+linei].split()))
     
    cA.resize([omega_num,6,6], refcheck=True)
    cB.resize([omega_num,6,6], refcheck=True)  
    
    Fe=famp*(np.cos(fphi)+1j*np.sin(fphi))
    Fe.resize([omega_num,6,1], refcheck=True)
    
    Hydro = {'K_h' : k_h, 'omega' : omega, 'mA' : cA, 'B' : cB, 'Fe': Fe,
             'displacement' : displacement, 'awp' : awp, 'mass' : m, 'Ixx':Ixx,
             'Iyy':Iyy, 'Izz':Izz
             }

    return Hydro


def rao_calc(Hydro,WaveSpec):
    # RAO Calculation
    imp =-1*Hydro['omega']**2*(Hydro['m']+Hydro['mA'])+ 1j*Hydro['omega']*(Hydro['B']+Hydro['Badd'])+Hydro['K_h']+Hydro['K_m']

    rao= np.array([])
    for freqi in range (0, len(Hydro['omega'])):
        
         imp_temp = (imp[freqi,:,:])                 
         fe_temp = (Hydro['Fe'][freqi,:,:])
         rao = np.append(rao,abs(np.linalg.lstsq(imp_temp.T, fe_temp)[0].T))
    
    rao.resize([len(Hydro['omega']),6], refcheck=True)
    
     # resample RAO to match frequency of generated wave spectrum
    rao = rao * Hydro['DOF']
    rao_ReSamp= np.empty((len(WaveSpec['freq']),6), float)
    rao_WaveS= np.empty((len(WaveSpec['freq']),6), float)
    for DOFi in range (0, 6):
        rao_ReSamp[:,DOFi] = np.interp(WaveSpec['freq'], Hydro['omega'][:,0,0], rao[:,DOFi],left=np.nan, right=np.nan).T
        rao_WaveS[:,DOFi] =rao_ReSamp[:,DOFi]**2*WaveSpec['S']
    
    rao_WaveSS = rao_WaveS[~np.isnan(rao_WaveS[:,0])]
    rao_WaveSS_freq = WaveSpec['freq'][~np.isnan(rao_WaveS[:,0])]
    #plt.plot(WaveSpec['freq'], rao_WaveS[:,0])
    
    Sig_dynamic_motion=  matrix = np.zeros((1,6))
    Max_dynamic_motion=  matrix = np.zeros((1,6))
    for DOFi in range (0, 6):
        N = 1000 #number of waves, need to clauclate this by dividing time period / T_z, need to claulte T_z from Tp or give it as user choice
        # multiples the m0 calc by the selected DOF array in order to ignore DOF that the user hasnt selected
        m0 = Hydro['DOF'][DOFi]*np.trapz(rao_WaveSS[:,DOFi], rao_WaveSS_freq)
        sigma  = math.sqrt(m0)
        Sig_dynamic_motion[0,DOFi] = 2* sigma
        Max_dynamic_motion[0,DOFi] = math.sqrt(2*math.log(N))*sigma


    Motion = {'Sig_dynamic_motion' : Sig_dynamic_motion, 'Max_dynamic_motion' : Max_dynamic_motion}
    RAO = {'omega' : Hydro['omega'], 'rao' : rao,'rao_ReSamp':rao_ReSamp,'rao_WaveS':rao_WaveS}

    return(Motion, RAO)

def wave_number(T, d):
    gravity = 9.80665
    omega = 2*math.pi/T 
    def solve_for_k(k):
        return (np.sqrt(gravity * k * 
                                    np.tanh(k * d)) - omega)     
    return (scipy.optimize.fsolve(solve_for_k, 0))[0]


#Function for the new release. previous function left to allow library to function
def static_forceV2(Body, Env):
    #Input
    #Body : {} : dictionary of parameters on body shape like mass etc
    #Env : {} : dictionary of environment forcing variables
    
    #Output
    #forces : {} : dictionary of static forces
    # defined variables
    rho = 1024
    rho_a = 1.225
    g =   9.80665
    nu = 1.04 * 10**-6
    nu_a = 1.48 * 10**-5 
    wave_amp =  Env['wave_height']/2
    wave_freq = 1/Env['period']
    wave_afreq = 2 *  math.pi *  wave_freq
    
    
    # Wave Circular Frequency vs Reflection coefficient
    Cr =np.array(([0.0012,0.0000],[0.1006,0.0083],[0.2012,0.0183],[0.3006,0.0733],[0.4000,0.2983],[0.5006,0.6283],[0.6000,0.9600],[0.6320,1.0517],[0.7006,0.8283],[0.8000,0.9000],[0.9006,0.9800],[1.0000,1.0000]))     
    # linear interpolation of reflection coefficent reference values
    ref_coeff = np.interp(wave_afreq,Cr[:,0],Cr[:,1])  
    
    # Reynolds number vs steady current drag coefficients
    Cd = np.array(([10155,1.20],[216922,1.20],[254952,1.],[279607,1.15],[299650,1.11],[323610,1.06],[341513,1.00],[354904,0.95],[368821,0.91],[380345,0.86],[392230,0.82],[407610,0.77],[417126,0.72],[430160,0.68],[450479,0.63],[464556,0.58],[486500,0.52],[509480,0.47],[537666,0.40],[571792,0.34],[617513,0.30],[698390,0.29],[814541,0.31],[872931,0.33],[972189,0.36],[1018111,0.37],[1116565,0.40],[1169307,0.41],[1262805,0.44],[1332667,0.45],[1450340,0.47],[1542396,0.49],[1704613,0.51],[1840914,0.53],[2018936,0.55],[2163661,0.57],[2447042,0.59],[2642707,0.61],[3106025,0.63],[3793714,0.65],[4390753,0.66],[5281012,0.68]))
    
    k = wave_number(Env['period'],Env['depth'])
    
    # floating or fixed rectangular box,  mean wave drift force 
    if Body['floaterConfig']['Geometry']['shape'] == 'Box':
        force_wave_drift = 0.5 * rho * g * wave_amp**2 * ref_coeff**2 * Body['floaterConfig']['Geometry']['wet width']
        area_proj = Body['draft'] * Body['floaterConfig']['Geometry']['wet width']
        area_proj_wind = Body['freeboard'] * Body['floaterConfig']['Geometry']['wet width']
        
        rey_num_cur = Env['current_vel']** Body['floaterConfig']['Geometry']['wet width']/nu
        # Reynoldys number for cylinder in wind
        rey_num_wind = Env['wind_vel']** Body['floaterConfig']['Geometry']['wet width']/nu_a  
    elif Body['floaterConfig']['Geometry']['shape'] == 'Cyl':
        diameter = Body['floaterConfig']['Geometry']['radius']*2
        area_proj = Body['draft'] * diameter
        area_proj_wind = Body['freeboard'] * diameter
        

        force_wave_drift = 5/16 * rho * g * wave_amp**2 * Body['floaterConfig']['Geometry']['radius'] * math.pi**2 * (k*Body['floaterConfig']['Geometry']['radius'])**3 
        rey_num_cur = Env['current_vel']*diameter/nu
        # Reynoldys number for cylinder in wind
        rey_num_wind = Env['wind_vel']*diameter/nu_a   
    else:            
        raise Exception("Float shape is incorrect. Please review your selection. Choose from 'Box' or 'Cyl'")
     
    # mean current force
    cur_coeff = np.interp(rey_num_cur,Cd[:,0],Cd[:,1])  
    wind_coeff = np.interp(rey_num_wind,Cd[:,0],Cd[:,1])  
    # Reynoldys number for cylinder in current
   
    force_current_mean = 0.5 * rho * Env['current_vel']**2 * cur_coeff * area_proj    
    
    # mean wind force
    force_wind_mean = 0.5 * rho_a* Env['wind_vel']**2 * wind_coeff * area_proj_wind
          
    if Body['floaterConfig']['Converter']['Type'] == 'WEC':
        force_tec_rotor = 0
    elif Body['floaterConfig']['Converter']['Type'] == 'TEC':
        area_tec_rotor = math.pi*Body['floaterConfig']['Converter']['Rotor Diameter']**2/4
        force_tec_rotor = 0.5 * rho * Env['current_vel']**2 * Body['floaterConfig']['Converter']['Thrust Coeff'] * area_tec_rotor     
        
    else:
        print('Error')
    
    force_static_total = force_wave_drift +  force_current_mean + force_wind_mean + force_tec_rotor
    
    return {'force_static_total' : round(force_static_total, 1), 
              'force_wave_drift' : round(force_wave_drift, 1), 
              'force_current_mean' : round(force_current_mean, 1),
              'force_wind_mean' : round(force_wind_mean, 1),
              'force_tec_rotor' : round(force_tec_rotor, 1)}


    
def anchor_position(radius,num_lines):
    x = []

    alpha = 2*math.pi/num_lines
    
    for k in range(0, num_lines):
        x.append([radius * math.cos(k*alpha), radius * math.sin(k*alpha)])

    return  np.array(x)


def ISSC_Create(wave_Hs,wave_Tp, freq_min, freq_max,freq_num, plot=False):
    wave_fp = 2*np.pi/wave_Tp
    
    freq = np.linspace(freq_min, freq_max, freq_num) * np.pi * 2
    
    S = (5/16)*wave_Hs**2*wave_fp**4*freq**-5*np.exp((-5/4)*(freq/wave_fp)**-4)
    
    WaveSpec = {'freq' : freq, 'S' : S,}
    if plot:
        plt.plot(freq, S)
        
    return WaveSpec

def jonswap(
    tp,
    Hs,
    gamma=3.3,
    freqs=np.arange(0.04, 5.0, 0.02),
    plot = False
):
    """Constructs JONSWAP spectra from peak period and peak direction."""

    # Arrange inputs
    w = freqs
    # Calculate JONSWAP
    wp = 2*np.pi / np.array(tp)
    sig = np.where(w <= wp, 0.07, 0.09)
    r = np.exp(-0.5*((w - wp) / (sig * wp))**2)
    A = 0.2 / (0.065 * gamma ** 0.803 + 0.135)
    S = A * 5/16 * Hs**2 * wp**4 * w ** (-5) * np.exp(-1.25 * (w / wp) ** (-4)) * gamma ** r
    
    if plot:
        plt.plot(freqs, S)
    
    return {'freq' : w, 'S' : S}
def period_test(Tn_limit, M, ma_inf, K_m, K_h):
    Tn = np.diag(2 * np.pi * np.sqrt((M + ma_inf)/(K_m + K_h)))
    if True in list(Tn < Tn_limit):
        result = 0 
    else: 
        result = 1
        
    return result 
def Moor_CreateV2(mooring, num_lines, rank, out_direc = None):
    #Inouts
    #mooring : dict : dictionary containing adjusted input parameters, 
    #including information on mooring properties and body. The following 
    #dictionaries are included in the mooring dict
    #1. static mean forces. 
    #2. environment which includes information on wave properties
    #3. Hydrodynamic forces
    #4. moor configuration
    #num_lines : int : iteratively increases from 1.
    #rank      : int : iterative increases from -1 using an external optimizer loop
    #out_direc : str : path to output directory to save plots
    
    #Outputs
    #resolved system dict : {} : dictionary containing resolved system information
    
    
    angle_legs     = np.arange(num_lines)*np.pi*2/num_lines # line headings list
    total_lines = num_lines * mooring['moorConfig']['lines_per_leg']
    angle = []
    for i in range(num_lines):
        print(i)
        c = angleGenerator(mooring['moorConfig']['lines_per_leg'], angle_legs[i],
                           mooring['moorConfig']['angles_between_lines'])
        angle = np.append(angle, c)
    angle = np.sort(angle)
    # --------------- set up mooring system ---------------------
    
    # Create blank system object
    ms = mp.System()
    
    # Set the depth of the system to the depth of the input value
    ms.depth = mooring['Environment']['depth']
    
    # add a line type
    typeName = mooring['moorConfig']['moorType']['moor_material']
    
    if mooring['moorConfig']['moorType']['Type'] == "Cat":
        grade = mooring['moorConfig']['moorType']['grade']
        ms.lineTypes[typeName] = getLinePropsFunSelkie(rank, typeName,   
            mooring['moorConfig']['moorType']['source'],
            stud = mooring['moorConfig']['moorType']['stud'],
            name=typeName, grade = grade)
    
    else:
        ms.lineTypes[typeName] = getLinePropsFunSelkie(rank, typeName,  
            mooring['moorConfig']['moorType']['source'],
            name=typeName)
    
    #define 

        # fixed values
    g =   9.80665
    depth_fair_seabed =mooring['Environment']['depth']-mooring['moorConfig']['fair_draft']
    
    if mooring['moorConfig']['moorType']['Type'] == "Cat":
            MBL = ms.lineTypes['chain'].MBL
            EA = ms.lineTypes['chain'].EA
            mass_wet = ms.lineTypes['chain'].w
            line_length= depth_fair_seabed*math.sqrt(2*(MBL/(mass_wet*g*depth_fair_seabed))-1)
            #line_length= depth_fair_seabed*math.sqrt(np.abs(2*(MBL/(mass_wet*g*depth_fair_seabed))-1))
            
            alpha = (mooring['moorConfig']['PreTen_Ratio']*MBL)/(mass_wet*g)
            anc_radius = line_length-depth_fair_seabed*math.sqrt(1+(2*alpha/depth_fair_seabed))+alpha*np.arccosh(1+depth_fair_seabed/alpha)
   
    elif mooring['moorConfig']['moorType']['Type'] == "Tau":
            MBL = ms.lineTypes['polyester'].MBL
            EA = ms.lineTypes['polyester'].EA
            mass_wet = ms.lineTypes['polyester'].w
            #taut_angle_legs_anchor = 25 #degrees
            pretension = mooring['moorConfig']['PreTen_Ratio']*MBL

            line_length_str= depth_fair_seabed/np.sin(
                mooring['moorConfig']['moorType']['angle']
                *math.pi/180)
            line_length_unstr = (EA*line_length_str - pretension*line_length_str)/EA
            line_length = line_length_unstr
            anc_radius= mooring['moorConfig']['fair_radius'] + math.sqrt(line_length_str**2-depth_fair_seabed**2)
    else: 
            print('Error, either input moor_type as "Cat" or "Tau"')
    
    
    # Add a free, body at [0,0,0] to the system (including some properties to make it hydrostatically stiff)
    awp = mooring['Hydrodynamic_forces']['awp']
    v = mooring['Hydrodynamic_forces']['displacement']
    m = mooring['moorConfig']['m'][0,0]
    ms.addBody(0, np.zeros(6), m=m, v=v, AWP=awp, f6Ext=np.array([0,0,0,0,0,0]))
    
    fair_radius = mooring['moorConfig']['fair_radius'] #to save space below, variable created
    fair_draft = mooring['moorConfig']['fair_draft'] #to save space below, variable created
    # need to add Pos_Anc and Pos_Fair to the new loops which create the MoorPy connection
    Pos_Anc = np.array([anc_radius*np.cos(angle), anc_radius*np.sin(angle), np.ones(total_lines)*-ms.depth], dtype=float)
    Pos_Fair = np.array([fair_radius*np.cos(angle), fair_radius*np.sin(angle), np.ones(total_lines)*-fair_draft], dtype=float)
   
    # Set the anchor points of the system
    
    anchors = []
    for i in range(len(angle)):
        ms.addPoint(1, np.array([anc_radius*np.cos(angle[i]), anc_radius*np.sin(angle[i]), -ms.depth], dtype=float))
        anchors.append(len(ms.pointList))  #Note to Chris: appending length here. is this correct?
                                            #names the anchor 
    
    # Set the points that are attached to the body to the system
    bodypts = []
    for i in range(len(angle)):
        ms.addPoint(1, np.array([fair_radius*np.cos(angle[i]), fair_radius*np.sin(angle[i]), -fair_draft], dtype=float))
        bodypts.append(len(ms.pointList))
        ms.bodyList[0].attachPoint(ms.pointList[bodypts[i]-1].number, ms.pointList[bodypts[i]-1].r - ms.bodyList[0].r6[:3])
    
    # Add and attach lines to go from the anchor points to the body points
    for i in range(len(angle)):    
        ms.addLine(line_length, typeName)
        line = len(ms.lineList)
        ms.pointList[anchors[i]-1].attachLine(ms.lineList[line-1].number, 0)
        ms.pointList[bodypts[i]-1].attachLine(ms.lineList[line-1].number, 1)
    
    
    
    ms.initialize()                                             # make sure everything's connected
       # equilibrate
    #ms.solveEquilibrium3(plots=1)  
    ms.solveEquilibrium()   
    Max_zeroload_tensions = np.zeros((1,num_lines))
    for Linei in range(0,num_lines):    
        #print(max(ms.lineList[Linei].getLineTens()))
        Max_zeroload_tensions[0,Linei] = max(ms.lineList[Linei].getLineTens())

 
    Kbody_0 = ms.bodyList[0].getStiffness()
    print(f"Body offset position at zero load is {ms.bodyList[0].r6}")
    
    #TO DO convert mean force to 6DOF components
    ms.bodyList[0].f6Ext = np.array([mooring['Mean_Force']['force_static_total'],
                                     0,0,0,0,0])
    ms.solveEquilibrium()    

    Max_meanload_tensions= np.zeros((1,num_lines))
    for Linei in range(0,num_lines):    
        #print(max(ms.lineList[Linei].getLineTens()))
        Max_meanload_tensions[0,Linei] = max(ms.lineList[Linei].getLineTens())


    Kbody_mean_force = ms.bodyList[0].getStiffness()
    
    print(f"Body offset position at mean offset is {np.round(ms.bodyList[0].r6,2)}")
    Mean_offset = ms.bodyList[0].r6 * mooring['moorConfig']['DOF']
    
    Stiff = {}
    Stiff["k0"] = [Kbody_0]
    Stiff["kmean"] = [Kbody_mean_force] 
    
    return {'ms' : ms, 'Kbody_0' : Kbody_0, 'Kbody_mean_force' : Kbody_mean_force, 
    'Mean_offset' : Mean_offset, 'Max_zeroload_tensions' : Max_zeroload_tensions,
    'Max_meanload_tensions' : Max_meanload_tensions, 'line_length' : line_length,
    'anc_radius' : anc_radius, 'Stiff' : Stiff}

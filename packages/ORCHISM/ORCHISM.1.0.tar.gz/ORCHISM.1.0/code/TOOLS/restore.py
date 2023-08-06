#*******************************************************************************
# MODULE	: RESTORE
# AUTHOR	: C. BACOUR
# CREATION	: 01/2009
# LAST MODIF    :
# COMPILER	: PYTHON
#
"""
Restore some information from previous runs
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

from orchis_config import Config
import numpy as np

#from TOOLS import io, funcio
import io, funcio

# ==============================================================================
# Restore some Vars characteristics
# ------------------------------------------------------------------------------
def paras(fic_res, Site, Vars, Opti, logfile):
    


    # -- opti_res.nc file --

    buf = io.readnc(fic_res)
    vars = buf[0]
    dims = buf[2]

    
    # Number of Parameters to optimize
    np = 0
    i=0
    while np == 0:
        if dims[i]['name'] == 'n': np = dims[i]['size']
        i=i+1
        
    # xpost
    for i in range(len(Vars.vars['opti_varname'])):
        
        ind = [-1]
        name = Vars.vars['opti_varname'][i]
        
        value = vars[name]['value']
        
        value_m = np.ma.masked_array(value, Opti.xmask[name])
        Opti.x[name] = np.array( value_m.filled(Config.missval[0]) )

    # Vars
    for name in Vars.vars['opti_varname']:
            Vars.vars[name]['value'] = np.reshape(Opti.x[name],(Vars.vars[name]['value']).shape )

            print name, Vars.vars[name]['value']
    

# END paras
# ==============================================================================


# ==============================================================================
# Restore some Data & Opti characteristics
# ------------------------------------------------------------------------------
def data(fic_res, fic_sim,
         Site, Data, opti_varname, Opti, logfile):
    

    # -- flux_posterior.nc file --
    # posterior simulations
    Data.sim = funcio.get_data(fic_sim,
                               logfile,
                               obs_name = Data.obsname,
                               tempo_res = Data.tempo_res, 
                               indices = Data.indices, 
                               tdaily = [Data.tdaily_d, Data.tdaily_f],
                               ndays = Site.njours, 
                               diurnal_length = Data.diurnal_length ,
                               diurnal_start = Data.diurnal_start, 
                               smooth_fapar = Data.smooth_fapar_sim,
                               smooth_flux_daily = Data.smooth_flux_daily,
                               fapar_normalize = Data.fapar_normalize,
                               fapar_normalize_minmax = [Data.fapar_normalize_min_pc, Data.fapar_normalize_max_pc]
                               )[0]

    print 'Lecture Data.sim successfull'


    # -- opti_res.nc file --

    buf = io.readnc(fic_res)
    vars = buf[0]
    dims = buf[2]

    
    # Number of Parameters to optimize
    np = 0
    i=0
    while np == 0:
        if dims[i]['name'] == 'n': np = dims[i]['size']
        i=i+1
        
    # xpost
    for i in range(len(opti_varname)):
        
        ind = [-1]
        name = opti_varname[i]
        
        value = vars[name]['value']
        
        value_m = np.ma.masked_array(value, Opti.xmask[name])
        Opti.x[name] = np.array( value_m.filled(Config.missval[0]) )


    # Jacobien
    Data.Jacobian = vars['Jacobian']['value']
    

    # need to reshape if Jacobian was generated
    # with a version of ORCHIS that was not accounting for undefined variables

    if np != Opti.n:

        for i in range(len(opti_varname)):
            name = opti_varname[i]
            if i == 0:
                mask=Opti.xmask[name]
            else:
                mask = np.ma.concatenate((mask,Opti.xmask[name]))
            
        #Jaco = Data.Jacobian[:]

        Opti.mask = mask
        ind = np.ma.masked_array(MA.arange(len(mask)), mask)
        ind = ind.compressed()

        Data.Jacobian = np.take(Data.Jacobian, ind)
    
    

# END data
# ==============================================================================

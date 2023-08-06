#!/usr/bin/env python
#*******************************************************************************
# MODULE	: VARIOUS
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 11/2007
# LAST MODIF    : 07/2012
# COMPILER	: PYTHON
#
"""
Various mathematical tools
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import sys
from orchis_config import Config
import numpy as np
#from TOOLS import *

# ==============================================================================
# Flatten list
# ------------------------------------------------------------------------------
def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
# ------------------------------------------------------------------------------

# ==============================================================================
# Determine the Root Mean Square Error between 2 time series
# ------------------------------------------------------------------------------
def rmse(data1, data2):

    
    if data1.shape != data2.shape: sys.exit('VARIOUS.RMSE : the dimensions of DATA2 do not match')

    d1 = np.ma.masked_where(data1 <= Config.missval[0], data1)
    d1 = np.ma.masked_where(data1 >= Config.missval[1], d1)
    
    d2 = np.ma.masked_where(data2 <= Config.missval[0], data2)
    d2 = np.ma.masked_where(data2 >= Config.missval[1], d2)

    ans = np.ma.sum((d1[:].ravel()-d2[:].ravel())**2)
    nel = (d1[:].ravel()-d2[:].ravel()).count()
    ans = np.ma.sqrt(  ans/ nel)
        
    return ans
# END rmse
# ==============================================================================


# ==============================================================================
# Smooth the input data according to a gaussian running filter
# ------------------------------------------------------------------------------
def smooth_gaussian(data_in, filter_in):

    
    width = len(filter_in)-1

    length = len(data_in)
    data_smooth = np.zeros(length, np.float64)
    
    for j in range(length):
        
        data_jdeb = max(0, j-width/2)
        data_jfin = min(j+width/2 +1, length)

        dataOK = data_in[data_jdeb:data_jfin]
        dataOK = np.ma.masked_where(dataOK <= Config.missval[0]
                                 or dataOK == Config.missval[1],dataOK )
        
        wind_jdeb = max(0, width/2-j)
        wind_jfin = min(width +1, length-j+width/2)
        filter = filter_in[wind_jdeb:wind_jfin]
        
        buf = np.ma.multiply(dataOK, filter)
        buf = np.ma.sum(buf)/MA.sum(filter)
       
        buf = np.array(np.ma.filled(buf, Config.missval[0]), np.float64)
        np.put(data_smooth,j,buf)

        
        #wind_jdeb = max(0, width/2-j)
        #wind_jfin = min(width +1, length-j+width/2)
        #filter = filter_in[wind_jdeb:wind_jfin]
        
        #buf = np.multiply(data_in[data_jdeb:data_jfin], filter)
        #buf = np.sum(buf)/np.sum(filter)


        
        # !!! Visualisation !!!
        #from pylab import *
        #xxx=np.array(range(len(obs['fAPARt'])))
        #plot(xxx,data_in,xxx,data_smooth)
        #show()
        #raw_input('pause')
        
    return data_smooth
# END smooth_gaussian
#
# - if fAPAR at the time step of ORCHIDEE => a voir
# indices of fAPAR in the window
#jdeb = max(0, j-width/2)
#jfin = min(j+width/2 +1, nts)
#ind_fapar = np.ma.masked_inside(jours_sim,jdeb,jfin)
#ind_fapar = np.ma.masked_where( ind_fapar.mask == True)
#print 'j',j,'ind:', ind_fapar                            
            
# ==============================================================================



# ==============================================================================
# Smooth the input data according to a square running filter
# ------------------------------------------------------------------------------
def smooth_square(data_in, width):

    
    length = len(data_in)
    data_smooth = np.zeros(length, np.float64)
    
    for j in range(length):
        
        data_jdeb = max(0, j-width/2)
        data_jfin = min(j+width/2 +1, length)

        dataOK = data_in[data_jdeb:data_jfin]
        dataOK = np.ma.masked_where(dataOK <= Config.missval[0], dataOK)
        dataOK = np.ma.masked_where(dataOK == Config.missval[1], dataOK)
        #dataOK = np.ma.masked_where(dataOK <= Config.missval[0]           ### NUMPY
        #                         or dataOK == Config.missval[1],dataOK )
        
        filter = np.ones(len(dataOK), np.float64)

        buf = np.ma.multiply(dataOK, filter)
        buf = np.ma.sum(buf)/(dataOK.count())
       
        buf = np.array(np.ma.filled(buf, Config.missval[0]), np.float64)
        np.put(data_smooth,j,buf)
        
    return data_smooth
# END smooth_square
# ==============================================================================



# ==============================================================================
# Return the value of an array corresponding to the value of the X% percentile
#
# ------------------------------------------------------------------------------
def get_percentile(array, pc, bins = None):

    data = np.array(array, np.float64)
    
    # bins definition
    if bins == None:
        ##nbins = 101
        nbins = max(int(len(data.ravel())/3),201)
        mini = np.minimum.reduce(data.ravel())
        maxi = np.maximum.reduce(data.ravel())
        binsize = (maxi-mini)/(nbins-1)
        bins = np.arange(mini,maxi+binsize,binsize)        
    else:
        binsize = bins[1]-bins[0]
    
        
    # histogram
    h = np.searchsorted(np.sort(data), bins)
    h = np.concatenate([h, [len(data)]])
    h = h[1:]-h[:-1]

    #import pylab
    #pylab.plot(range(len(data)), data)
    #pylab.show()

    # case where all values in array are similar
    if len(h) == 0:
        return -9999

    # cumulative histogram (%)
    hcum = np.cumsum(h)
    hcum = hcum*100/np.maximum.reduce(hcum)
    
    # Value of data corresponding to the percentile pc
    ind_pc = np.searchsorted(hcum,pc)
    x = np.array(range(nbins+1), np.float64)*binsize+mini

    x_pc = x[ind_pc]

    dif = np.fabs(data-x_pc)
    ind = np.nonzero( (dif == np.minimum.reduce(dif)).ravel() )

    #print data[ind[0][0]]
    return data[ind[0][0]]
# END get_percentile
# ==============================================================================


# ==============================================================================
# Normalize OBS values between min and max
#
# ------------------------------------------------------------------------------
def normalize(data, vmin, vmax, logfile):

   
    # Deal with missing values
    mask   = np.ma.masked_where(data <= Config.missval[0], data)
    datan = np.ma.masked_where(data >= Config.missval[1], mask)

    # Normalization
    if vmax != vmin: datan = (datan-vmin)/(vmax-vmin)

    # Mask normalized values out of [0;1] (<=> mask values out of [vmin;vmax])
    datan = np.ma.masked_less(datan,0)
    datan = np.ma.masked_greater(datan,1)

    if vmax == vmin:
        print ' ### FUNCIO.NORMALIZE | Problem : min == max ###'
        logfile.write(' ### FUNCIO.NORMALIZE | Problem : min == max ### \n')
        print "min, max", vmin, vmax
        raw_input('pause')
        sys.exit()

    
    # Return value
    datan = datan.filled(Config.missval[0])
    return datan

# END normalize
# ==============================================================================



# ==============================================================================
# Determine the min & max values of the data, corresponding to the upper and
# lower percentile of the range of variation of the data
#
# ------------------------------------------------------------------------------
def detminmax(data,  vmin, vmax, percentile = False):


  
    # Deal with missing values
    mask   = np.ma.masked_where(data <= Config.missval[0], data)
    datan = np.ma.masked_where(data >= Config.missval[1], mask)

    # Determine the min and max
    if vmin == 0 or percentile == False:
        vmin = np.ma.minimum.reduce(datan.ravel())
    else:
        vmin = get_percentile(datan.ravel().compressed(), vmin)
        
    if vmax == 100 or percentile == False:
        vmax = np.ma.maximum.reduce(datan.ravel())
    else:
        vmax = get_percentile(datan.ravel().compressed(), vmax)

    

    # Return value
    return vmin, vmax

# END normalize
# ==============================================================================



# ==============================================================================
# Sort out the list of optimization parameters according to a predifined order
# provided in the template
#
# ------------------------------------------------------------------------------
## def triname(names, template, template_diurnal = None):

##     name = []
##     if template_diurnal == None:
##         for pname in template:
##             if pname in names: name.append(pname)
    
##     else:
##         names_all=[]
##         for pname in template:
##             names_all.append(pname)
##             if pname in template_diurnal : names_all.append(pname+'_diurnal')

##         for pname in names_all:
##             if pname in names: name.append(pname)
##     return name

## def triname(names, template):
##     name = []
##     for pname in template:
##         try:
##             test = names.index(pname)
##         except:
##             test = -1
##         if test != -1: name.append(pname)
##     return name


def triname(names, template):
    name = []
    for pname in template:
        try:
            test = names.index(pname)
        except:
            test = -1
        if test != -1: name.append(names[test])
    return name
# ==============================================================================


# ================================================================================
# Pick out the variables in the multisite Vars dictionnary to update the Vars_site
# dictionnnary for each site
#
# --------------------------------------------------------------------------------
def vars_to_site(isite, name, Vars, Site):
    
    import numpy as np
    import copy

    # 1. if PFT and region dependent
    if 'indice_region' in Vars.vars[name]['dim_name'] and 'indice_pft' in Vars.vars[name]['dim_name']:
        imap = Vars.vars[name]['map'] #determine which map this parameter is using
        ireg = Site.loc[imap][isite]
        #print Vars.vars[name]['value']
        #print ireg
        #print Vars.vars['PFT']['indexes'][imap][ireg][isite]
        vars_site = np.take(Vars.vars[name]['value'][ireg], (Vars.vars['PFT']['indexes'][imap][ireg][isite]).tolist(), axis=0)

    # 2. If PFT and site dependent
    elif 'points_terre' in Vars.vars[name]['dim_name'] and 'indice_pft' in Vars.vars[name]['dim_name']:
        vars_site = copy.deepcopy(Vars.vars[name]['value'][isite])

    # 3. if only region-dependent
    elif 'indice_region' in Vars.vars[name]['dim_name']:
        imap = Vars.vars[name]['map'] #determine which map this parameter is using
        ireg = Site.loc[imap][isite] # determine which region the site belongs to
        for ireg2 in range(len(Site.map['occupied_regions'][imap])):
            if Site.map['occupied_regions'][imap][ireg2]==ireg: break
        vars_site = copy.deepcopy(Vars.vars[name]['value'][ireg2])

    # 4. if site-dependent
    elif 'points_terre' in Vars.vars[name]['dim_name']:
        vars_site = copy.deepcopy(Vars.vars[name]['value'][isite])
                
    # 5. if only PFT-dependent
    elif 'indice_pft' in Vars.vars[name]['dim_name']:
        vars_site = np.take(Vars.vars[name]['value'], (Vars.vars['PFT_global']['indexes'][isite]).tolist(), axis=0)

    # 6. if globally generic       
    else:
        vars_site = copy.deepcopy(Vars.vars[name]['value'])

    return vars_site

# ===================================================================================================

#!/usr/bin/env python
#*******************************************************************************
# MODULE	: BFGS
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 09/2007
# LAST MODIF    : 07/2012
# COMPILER	: PYTHON
#
"""
BFGS-related functions
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import os
from orchis_config import Config
from time import localtime, strftime
import numpy as np

#from TOOLS import io
import io

# ==============================================================================
# Write the input NetCDF file for BFGS
#
# ------------------------------------------------------------------------------
def write_bfgs_in(Opti, logfile):


    #import numpy as np

        
    # -- Define the dimensions of the NetCDF file
    
    
    dims = [{'name': 'parameter', 'size':1}]
    dims.append({'name': 'n', 'size':Opti.n})
    dims.append({'name': 'dim_wa', 'size': Opti.BFGS['size_wa']})
    dims.append({'name': 'dim_iwa', 'size': Opti.BFGS['size_iwa']})
    dims.append({'name': 'dim_isave', 'size': Opti.BFGS['size_isave']})
    dims.append({'name': 'dim_dsave', 'size': Opti.BFGS['size_dsave']})
    dims.append({'name': 'dim_lsave', 'size': Opti.BFGS['size_lsave']})

    
    # -- Define the global attributes of the NetCDF file
    gattr = [{'name': 'date', 'value':strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())}]
        
    # -- Define BFGS parameters
    paraBFGS = {}
    
    #- Constants
    
    paraBFGS['factr'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                         'dim_size': 1, 'value': Opti.BFGS['factr'], \
                         'attr_name':['longname'], 'attr_value':['Tolerance in the termination test']}

    paraBFGS['pgtol'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                         'dim_size': 1, 'value': Opti.BFGS['pgtol'], \
                         'attr_name':['longname'], 'attr_value':['Tolerance in the termination test']}

    paraBFGS['m'] = {'datatype':'i','ndims':1, 'dim_name':('parameter',), \
                     'dim_size': 1, 'value': Opti.BFGS['m'], \
                     'attr_name':['longname'], 'attr_value':['Number of corrections in the memory matrix']}
    
    paraBFGS['iprint'] = {'datatype': 'i', 'ndims':1, 'dim_name':('parameter',), \
                          'dim_size': 1, 'value': Opti.BFGS['iprint'], \
                          'attr_name':['longname'], 'attr_value':['Control the frequency and type of outputs']}

    # the value for task is written as an attribute as it is a string
    paraBFGS['task'] = {'datatype':'c', 'ndims':1, 'dim_name':('parameter',), \
                        'dim_size': 1, 'value': '-', \
                        'attr_name':['longname','value'], 'attr_value':['Define the BFGS task to perform',Opti.BFGS['task']]}

    #- Optimization parameters
    # Parameter values
    paraBFGS['x'] = {'datatype': 'd', 'ndims':1, 'dim_name':('n',), \
                     'dim_size': Opti.n, 'value': Opti.chi['all'], \
                     'attr_name':['longname'], 'attr_value':['Values of the optimization parameters']}

    # lower bounds
    paraBFGS['l'] = {'datatype': 'd', 'ndims':1, 'dim_name':('n',), \
                     'dim_size': len(Opti.chi_lb['all']), 'value': Opti.chi_lb['all'], \
                     'attr_name':['longname'], 'attr_value':['Lower bound of the optimization parameters']}

    # upper bounds
    paraBFGS['u'] = {'datatype': 'd', 'ndims':1, 'dim_name':('n',), \
                     'dim_size': len(Opti.chi_ub['all']), 'value': Opti.chi_ub['all'], \
                     'attr_name':['longname'], 'attr_value':['Upper bound of the optimization parameters']}

    # Type of bounds
    paraBFGS['nbd'] = {'datatype': 'i', 'ndims':1, 'dim_name':('n',), \
                       'dim_size': len(Opti.BFGS['nbd']), 'value': Opti.BFGS['nbd'], \
                       'attr_name':['longname'], 'attr_value':['Type of bounds']}

    # Misfit function
    paraBFGS['f'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                     'dim_size': 1, 'value': Opti.MF, \
                     'attr_name':['longname'], 'attr_value':['Value of the misfit function']}

    # Misfit function
    paraBFGS['g'] = {'datatype': 'd', 'ndims':1, 'dim_name':('n',), \
                     'dim_size': Opti.n, 'value': Opti.gradMF, \
                     'attr_name':['longname'], 'attr_value':['Value of the gradient of misfit function']}

    #- Some BFGS working variables
    paraBFGS['wa'] = {'datatype': 'd', 'ndims':1, 'dim_name':('dim_wa',), \
                      'dim_size': Opti.BFGS['size_wa'], 'value': Opti.BFGS['wa'], \
                      'attr_name':['longname'], 'attr_value':['BFGS workspace']}
    
    paraBFGS['iwa'] = {'datatype': 'i', 'ndims':1, 'dim_name':('dim_iwa',), \
                       'dim_size': Opti.BFGS['size_iwa'], 'value': Opti.BFGS['iwa'], \
                       'attr_name':['longname'], 'attr_value':['BFGS workspace']}

    paraBFGS['isave'] = {'datatype': 'i', 'ndims':1, 'dim_name':('dim_isave',), \
                         'dim_size': Opti.BFGS['size_isave'], 'value': Opti.BFGS['isave'], \
                         'attr_name':['longname'], 'attr_value':['Some BFGS info on the optimization']}

    paraBFGS['dsave'] = {'datatype': 'd', 'ndims':1, 'dim_name':('dim_dsave',), \
                         'dim_size': Opti.BFGS['size_dsave'], 'value': Opti.BFGS['dsave'], \
                         'attr_name':['longname'], 'attr_value':['Some BFGS info on the optimization']}
    
    paraBFGS['lsave'] = {'datatype': 'i', 'ndims':1, 'dim_name':('dim_lsave',), \
                         'dim_size': Opti.BFGS['size_lsave'], 'value': Opti.BFGS['lsave'], \
                         'attr_name':['longname'], 'attr_value':['Some BFGS info on the bounds at exit']}

    # the value for csave is written as an attribute as it is a string
    paraBFGS['csave'] = {'datatype':'c', 'ndims':1, 'dim_name':('parameter',), \
                         'dim_size': 1, 'value': '-', \
                         'attr_name':['longname','value'], 'attr_value':['BFGS character working array',Opti.BFGS['csave']]}


    # -- Write the file
    # global attributes + dimensions
    #print 'BFGS : ecriture attributs et dimensions'
    io.writenc(os.path.join(Config.PATH_MAIN_TMP,Opti.BFGS['input']),gattr = gattr, dims = dims)

    # variables
    var_order = ['factr', 'pgtol', 'm', 'iprint', 'task', \
                 'x', 'l', 'u', 'nbd', 'f', 'g', \
                 'wa', 'iwa','isave', 'dsave', 'lsave', 'csave' ]

    #io.writenc(BFGS['input'], vars = paraBFGS , append = 1, var_order = var_order)

    for name in var_order:
        print 'Ecriture', name
        io.writenc(os.path.join(Config.PATH_MAIN_TMP,Opti.BFGS['input']), vars = {name:paraBFGS[name]} , append = 1)
    
    
        
# END write_bfgs_in
# ==============================================================================





# ==============================================================================
# Read the output NetCDF file from BFGS
#
# ------------------------------------------------------------------------------
def read_bfgs_out(opti_varname, Opti, logfile):

    
    var_order = ['factr', 'pgtol', 'm', 'iprint', 'task', \
                 'x', 'l', 'u', 'nbd', 'f', 'g', \
                 'wa', 'iwa','isave', 'dsave', 'lsave', 'csave' ]
    
    # - Read the NetCDF File
    [vars, gattr, dims] = io.readnc(os.path.join(Config.PATH_MAIN_TMP,Opti.BFGS['output']))


    # - Modify the BFGS structure
    for name in var_order:           
        if name == 'task' or name == 'csave':
            ind = vars[name]['attr_name'].index('value')
            Opti.BFGS[name] = vars[name]['attr_value'][ind]
        else:
            Opti.BFGS[name] = vars[name]['value']

    # - Modify the Opti structure
    ind = [-1]

    #print 'BFGS READ'
    for i in range(len(opti_varname)):
        name = opti_varname[i]
        n = Opti.xmask[name].count()

        if n>0:
            ind = np.arange(ind[len(ind)-1]+1, ind[len(ind)-1]+n+0.1)
            ind = ind.astype(np.int32).tolist()

            idxOK = np.ma.masked_array(range(len(Opti.xmask[name])),Opti.xmask[name].mask).compressed()
            np.put(Opti.chi[name], idxOK, np.take(vars['x']['value'], ind) )
        else:
            Opti.chi[name] = np.array(Config.missval[0], np.float64)


    # - Task history
    
    Opti.BFGS['task_hist'] = [Opti.BFGS['task_hist'][0] + ';'+ Opti.BFGS['task']]
  

# END read_bfgs_out
# ==============================================================================



# ==============================================================================
# Write informations
#
# ------------------------------------------------------------------------------
def write_infos(Opti, logfile, case = None ):
    
    logfile.write('\n')

    if case == 'input':
        print '   ####   BFGS : inputs   ###'
        logfile.write('   ####   BFGS : inputs   ###\n')
    if case == 'output':
        print '   ####   BFGS : outputs   ###'
        logfile.write('   ####   BFGS : outputs   ###\n')

    x = []
    ub = []
    lb = []
    for name in Opti.name :
        x.extend(Opti.chi[name].ravel().tolist())
        ub.extend(Opti.chi_ub[name].ravel().tolist())
        lb.extend(Opti.chi_lb[name].ravel().tolist())
        
    print '      + task : '+Opti.BFGS['task']
    print '      + x : '+str(x)
    print '      + ub : '+str(ub)
    print '      + lb : '+str(lb)
    print '      + f : '+str(Opti.MF)
    print '      + g : '+str(Opti.gradMF)
    print '      + projected gradient : '+str(Opti.BFGS['dsave'][12])
    print '      + previous f : '+str(Opti.BFGS['dsave'][1])
    print '      + maximum relative step length imposed in line search : ' + str(Opti.BFGS['dsave'][11])
    print '      + relative step length imposed in line search : ' + str(Opti.BFGS['dsave'][13])

        
    logfile.write('      + task : '+Opti.BFGS['task'] +'\n')
    logfile.write('      + x : '+str(x) +'\n')
    logfile.write('      + ub : '+str(ub) +'\n')
    logfile.write('      + lb : '+str(lb) +'\n')
    logfile.write('      + f : '+str(Opti.MF) +'\n')
    logfile.write('      + g : '+str(Opti.gradMF) +'\n')
    logfile.write('      + projected gradient : '+str(Opti.BFGS['dsave'][12]) +'\n')
    logfile.write('      + previous f : '+str(Opti.BFGS['dsave'][1]) +'\n')
    logfile.write('      + maximum relative step length imposed in line search : ' + str(Opti.BFGS['dsave'][11]) + '\n')
    logfile.write('      + relative step length imposed in line search : ' + str(Opti.BFGS['dsave'][13]) +'\n')

    if case == 'output':
        print
        print
        print '  ## BFGS - dsave(12) : maximum relative step length imposed in line search :'
        print '      ',Opti.BFGS['dsave'][11]
        print '  ## BFGS - dsave(14) : relative step length imposed in line search :'
        print '      ',Opti.BFGS['dsave'][13]
        print
        print

        logfile.write( '\n  ## BFGS - dsave(12) : maximum relative step length imposed in line search :'+str(Opti.BFGS['dsave'][11])+'\n')
        logfile.write( '\n  ## BFGS - dsave(14) : relative step length imposed in line search :'+str(Opti.BFGS['dsave'][13])+'\n')

    
# END write_infos
# ==============================================================================


# --- Modify the Opti class containing informations to pass to the optimization
# --- algorithm
    #Opti.BFGS = Opti.BFGS
    
    ## nparas = 0
##     for i in  range(len(vars['opti_varname'])):
##         name = vars['opti_varname'][i]
##         nparas = nparas+len(vars[name]['value'].ravel())

    
##     Opti.lb = np.zeros(nparas, np.float64)
##     Opti.ub = np.zeros(nparas, np.float64)
##     ind = [-1]
##     for i in  range(len(vars['opti_varname'])):
##         name = vars['opti_varname'][i]
        
##         lb = vars[name]['min']
##         ub = vars[name]['max']
##         n = len(vars[name]['value'].ravel())
        
##         ind = np.arange(ind[len(ind)-1]+1, ind[len(ind)-1]+n+0.1).tolist()
##         np.put(Opti.lb,ind, np.resize(lb,(n,)))
##         np.put(Opti.ub,ind, np.resize(ub,(n,)))
# END initopti
# ==============================================================================

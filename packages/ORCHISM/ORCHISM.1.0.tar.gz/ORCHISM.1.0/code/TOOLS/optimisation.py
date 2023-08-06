#*******************************************************************************
# MODULE	: OPTIMISATION
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 08/2007
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
Optimization-related functions
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import copy, os, sys, random
from math import log, atan
from orchis_config import Config
import numpy as np

#from TOOLS import various, initialize, prior, funcio, orchidee
import various, initialize, prior, funcio, orchidee

# ==============================================================================
# Initialize the Opti class containing all data that are passed to the
# optimization algorithm
# ------------------------------------------------------------------------------
def initopti(Vars, Site, Opti, nobs = None, dataname = None, cas = None, test_gradMF_vs_eps = False):

    
    # --- Initialization
    if cas == 'init':

        # - variables to optimize
        Opti.hist_x = {}
        Opti.x = {}
        Opti.xname = []
        Opti.sitename = []
        Opti.indsite = []
        Opti.xprior = {}
        Opti.B = {}
        Opti.Bpost_diag = {}
        Opti.lb = {}
        Opti.ub = {}
        Opti.eps = {}
        Opti.xmask = {}

        #transformed variables
        Opti.chi = {}
        Opti.chi_prior = {}
        Opti.chi_lb = {}
        Opti.chi_ub = {}
        Opti.chi_eps = {}
        
        Opti.n = 0
        Opti.ns = np.zeros((Site.npts), np.int32)
        Opti.sigma = {}
        Opti.max = {}
        Opti.min = {}
        
        Opti.name = Vars.vars['opti_varname']

        # - variables to optimize per region - used in the Finite Difference approach
        #   to perturb the initial value of the parameter for the computation of the gradient
#        Vars.vars_reg = {}
        Opti.indice_reg = {}

        initopti_x(Vars,Opti, case = 'init')
        
        for name in Vars.vars['opti_varname']:

            Opti.xmask[name] = np.ma.zeros(len(Opti.x[name])) # mask used for undefined variables

            #- Check for undefined variables
            if Config.missval[0] in Opti.xprior[name]:
                idx = list(np.nonzero(( Opti.x[name] == Config.missval[0]).ravel()))
                Opti.xmask[name][idx] = np.ma.masked

            Opti.B[name] = (Vars.B[name]).ravel()
            Opti.Bpost_diag[name] = np.ones(Vars.Bpost[name].shape)*Config.missval[0]
                
            Opti.chi[name]  = copy.copy(Opti.x[name])
            Opti.chi_prior[name]  = copy.copy(Opti.xprior[name])
            Opti.chi_lb[name] = copy.copy(Opti.lb[name])
            Opti.chi_ub[name] = copy.copy(Opti.ub[name])

            # Build convenient epsilon,sigma, min and max array
            if len(Vars.vars[name]['dim_name'])<3:
                Opti.eps[name] = np.ones(Vars.vars[name]['sigma'].shape)*Vars.vars[name]['eps']
                Opti.chi_eps[name] = np.ones(Vars.vars[name]['sigma'].shape)*Vars.vars[name]['eps']
                Opti.sigma[name] = Vars.vars[name]['sigma']
                Opti.min[name] = Vars.vars[name]['min_opti']
                Opti.max[name] = Vars.vars[name]['max_opti']
            else:
                icnt = 0
                for ireg in Vars.vars[name]['3rd_loop']:
                    tmp1 =  np.ones(Vars.vars[name]['sigma'][ireg].shape)*Vars.vars[name]['eps']
                    tmp2 =  Vars.vars[name]['sigma'][ireg]
                    tmp3 = Vars.vars[name]['min_opti'][ireg]
                    tmp4 = Vars.vars[name]['max_opti'][ireg]
                    if icnt == 0 :
                        Opti.eps[name] = tmp1
                        Opti.chi_eps[name] = tmp1
                        Opti.sigma[name] = tmp2
                        Opti.min[name] = tmp3
                        Opti.max[name] = tmp4
                    else:
                        Opti.eps[name]  = np.concatenate((Opti.eps[name], tmp1))
                        Opti.chi_eps[name]  = np.concatenate((Opti.chi_eps[name], tmp1))
                        Opti.sigma[name]  = np.concatenate((Opti.sigma[name], tmp2))
                        Opti.min[name]  = np.concatenate((Opti.min[name], tmp3))
                        Opti.max[name]  = np.concatenate((Opti.max[name], tmp4))
                    icnt = icnt +1


            Opti.hist_x[name] = []

            #- Build the array with name for each parameter component and related site(s)
            
            if len(Vars.vars[name]['dim_name'])<3:
                longname = various.flatten(Vars.vars[name]['longname'])
                # !! won't work if the time variation is not fix !!
                site_par = Vars.vars[name]['site_par']            #
                #                                                 #
                for idx in range(len(Opti.xmask[name])): 
                    if type(Opti.xmask[name][idx]) != type(np.ma.masked):
                        Opti.xname.extend([longname[idx]])
                        Opti.sitename.extend([site_par[idx]])
                    #print name, longname[idx]

            else:
                offset = 0
                for ireg in Vars.vars[name]['3rd_loop']:
                    longname = various.flatten(Vars.vars[name]['longname'][ireg])
                    # !! won't work if the time variation is not fix !!
                    site_par = Vars.vars[name]['site_par'][ireg]      #
                    #                                                 #
                    for idx in range(len(Vars.vars[name]['value'][ireg])): 
                        if type(Opti.xmask[name][offset+idx]) != type(np.ma.masked):
                            Opti.xname.extend([longname[idx]])
                            Opti.sitename.extend([site_par[idx]])
                    offset = offset + len(Vars.vars[name]['value'][ireg])

        # Count the total number of parameter component
        Opti.n = len(Opti.xname)

        # Count the number of parameter for each site, and locate in Opti.xname
        for isite in range(Site.npts):
            ns = 0
            ind = []
            for ipar in range(Opti.n):
                if Site.name[isite] in Opti.sitename[ipar]:
                    ind.append(ipar)
                    ns = ns+1
            Opti.indsite.extend([ind])
            Opti.ns[isite] = ns

        #-  A posteriori error covariance and correlation matrices
        Opti.Bpost = np.zeros((Opti.n,Opti.n), np.float64)
        Opti.Bpost_site = {}
       
        for isite in range(Site.npts):
            Opti.Bpost_site[isite] = np.zeros((Opti.ns[isite],Opti.ns[isite]), np.float64)

        #- Initialize MF and gradMF
        Opti.MF = np.zeros(1, np.float64)
        Opti.gradMF = np.zeros(Opti.n, np.float64)

        Opti.gradMFobs = {}
        for isite in range(Site.npts):
            for name in dataname[isite]:
                name_site = name+'_'+Site.name[isite]
                Opti.gradMFobs[name_site] = np.zeros(Opti.n, np.float64)
        Opti.gradMFpar = np.zeros(Opti.n, np.float64)


        #- history of the misfit function & gradient values
        Opti.hist_MFpar = []
        Opti.hist_MF = []
        Opti.hist_MFobs = {}
        Opti.hist_gradMF = {}
        for isite in range(Site.npts):
            for name in dataname[isite]:
                name_site = name+'_'+Site.name[isite]
                Opti.hist_MFobs[name_site] = []
                Opti.hist_gradMF['MFobs_'+name_site] = []
        Opti.hist_MFobs['total'] = []
        
        Opti.hist_gradMF['MFobs_total'] = []
        Opti.hist_gradMF['MFpar'] = []
        Opti.hist_gradMF['MF'] = []

        #- history for the gradient of the misfit function regarding to eps
        if test_gradMF_vs_eps == True:
            Opti.hist_gradMF_eps = {}
            Opti.hist_gradMF_eps['MF'] = {}
            Opti.hist_gradMF_eps['MFpar'] = {}
            Opti.hist_gradMF_eps['MFobs_total'] = {}
            for isite in range(Site.npts):
                for name in dataname[isite]:
                    name_site = name+'_'+Site.name[isite]
                    Opti.hist_gradMF_eps['MFobs_'+name_site] = {}
                                
            for name in Vars.vars['opti_varname']:
                Opti.hist_gradMF_eps['MF'][name] = []
                Opti.hist_gradMF_eps['MFpar'][name] = []
                Opti.hist_gradMF_eps['MFobs_total'][name] = []
                for isite in range(Site.npts):
                    for oname in dataname[isite]:
                        name_site = oname+'_'+Site.name[isite]
                        Opti.hist_gradMF_eps['MFobs_'+name_site][name] = []

            
    #--- Values of the parameters
    if cas == 'xonly':
        initopti_x(Vars,Opti)
                                       
    #--- Elements containing all the values of the parameters to pass to the optimization routine
    if cas == 'all':

        icnt = 0

        for name in Vars.vars['opti_varname']:

            if Opti.xmask[name].count() > 0:

                b_x          = np.array( np.ma.masked_array(Opti.x[name], Opti.xmask[name].mask).compressed() )
                b_xprior     = np.array( np.ma.masked_array(Opti.xprior[name], Opti.xmask[name].mask).compressed() )
                b_chi_prior  = np.array( np.ma.masked_array(Opti.chi_prior[name], Opti.xmask[name].mask).compressed() )
                b_B          = np.array( np.ma.masked_array(Opti.B[name], Opti.xmask[name].mask).compressed() )
                b_chi        = np.array( np.ma.masked_array(Opti.chi[name], Opti.xmask[name].mask).compressed() )

                b_lb     = np.array( np.ma.masked_array(Opti.lb[name], Opti.xmask[name].mask).compressed() )
                b_ub     = np.array( np.ma.masked_array(Opti.ub[name], Opti.xmask[name].mask).compressed() )
                b_chi_lb = np.array( np.ma.masked_array(Opti.chi_lb[name], Opti.xmask[name].mask).compressed() )
                b_chi_ub = np.array( np.ma.masked_array(Opti.chi_ub[name], Opti.xmask[name].mask).compressed() )

                b_eps     = np.array( np.ma.masked_array(Opti.eps[name], Opti.xmask[name].mask).compressed() )
                b_chi_eps = np.array( np.ma.masked_array(Opti.chi_eps[name], Opti.xmask[name].mask).compressed() )

                if icnt == 0:
                             
                    Opti.x['all']      = b_x
                    Opti.xprior['all'] = b_xprior
                    Opti.lb['all']     = b_lb
                    Opti.ub['all']     = b_ub
                    Opti.B['all']      = b_B
                    Opti.chi['all']       = b_chi
                    Opti.chi_prior['all'] = b_chi_prior
                    Opti.chi_lb['all']    = b_chi_lb
                    Opti.chi_ub['all']    = b_chi_ub

                    Opti.eps['all']        = b_eps
                    Opti.chi_eps['all']    = b_chi_eps

                else:
                    
                    Opti.x['all']      = np.concatenate((Opti.x['all'], b_x))
                    Opti.xprior['all'] = np.concatenate((Opti.xprior['all'],b_xprior))
                    Opti.chi_prior['all'] = np.concatenate((Opti.chi_prior['all'],b_chi_prior))
                    Opti.B['all']      = np.concatenate((Opti.B['all'],b_B))
                    Opti.chi['all']      = np.concatenate((Opti.chi['all'],b_chi))
                    
                    Opti.lb['all']     = np.concatenate((Opti.lb['all'],b_lb))
                    Opti.ub['all']     = np.concatenate((Opti.ub['all'],b_ub))
                    Opti.chi_lb['all'] = np.concatenate((Opti.chi_lb['all'],b_chi_lb))
                    Opti.chi_ub['all'] = np.concatenate((Opti.chi_ub['all'],b_chi_ub))

                    Opti.eps['all']     = np.concatenate((Opti.eps['all'], b_eps))
                    Opti.chi_eps['all'] = np.concatenate((Opti.chi_eps['all'], b_chi_eps))
                    
                icnt += 1

    #--- Elements containing all the values of the parameters 
    if cas == 'xall': # ajout CB
        initopti_x(Vars,Opti)        

        icnt = 0
        for name in Vars.vars['opti_varname']:

            if Opti.xmask[name].count() > 0:
                b_x      = np.array( np.ma.masked_array(Opti.x[name], Opti.xmask[name].mask).compressed() )
                b_chi     = np.array( np.ma.masked_array(Opti.chi[name], Opti.xmask[name].mask).compressed() )              
                            
                if icnt == 0:                             
                    Opti.x['all']      = b_x
                    Opti.chi['all']     = b_chi
                else:
                    
                    Opti.x['all']      = np.concatenate((Opti.x['all'], b_x))
                    Opti.chi['all']      = np.concatenate((Opti.chi['all'],b_chi))
                                        
                icnt += 1

          
# END initopti
# ==============================================================================


# ==============================================================================
# Initialization of the Opti.x class
# ==============================================================================
def initopti_x(Vars, Opti, case = None):


    # - initialize a dictionnary allowing to map the values of Opti.x ontto a map
    #   Vars.vars[name]['value'] for the computation of the gradient by finite difference
    #   x_ind4map is a list of 2 elements : map number + indice of the element for each map
    if case == 'init':
        Opti.x_ind4map = {}

    # - Loop on the parameters
    for name in Vars.vars['opti_varname']:
        
 #      print name
        
        # Standard case : 2D at maximum
        if len(Vars.vars[name]['dim_name']) < 3 :

            # - x
            Opti.x[name]      = (Vars.vars[name]['value']).ravel()

            # -xprior
            if case == 'init':
                Opti.xprior[name]    = (Vars.vars[name]['prior']).ravel()
                Opti.x_ind4map[name] = None #range(len(Opti.xprior[name]))

                # -- Boundaries
                Opti.lb[name] = (Vars.vars[name]['min_opti']).ravel()
                Opti.ub[name] = (Vars.vars[name]['max_opti']).ravel()

        else:

            # If the dimension is 3, we have a dictionnary of 2D arrays (PFT*time) for each region.
            # After selecting the right map, the parameters values in each region are concatenated (y direction).
            # It is workable because the number of rows (time dimension) is always the same.
            if len(Vars.vars[name]['dim_name']) ==3:

#               print 'CAS = 3'
                
                icnt = 0            
                
                for ireg in Vars.vars[name]['3rd_loop']:

                    # - x
                    tmp = (Vars.vars[name]['value'][ireg]).ravel()
                    if icnt == 0:
                        Opti.x[name]      = tmp
                    else:
                        Opti.x[name]      = np.concatenate((Opti.x[name], tmp))

                    # - xprior
                    if case == 'init':
                        tmp = (Vars.vars[name]['prior'][ireg]).ravel()
                        tmplb = (Vars.vars[name]['min_opti'][ireg]).ravel()
                        tmpub = (Vars.vars[name]['max_opti'][ireg]).ravel()
                        
                        if icnt == 0:
                            Opti.xprior[name]  = tmp
                            Opti.x_ind4map[name] = {}
                            Opti.x_ind4map[name][0]  = [ireg]*len(tmp)
                            Opti.x_ind4map[name][1]  = range(len(tmp))

                            # -- Boundaries
                            Opti.lb[name] = tmplb
                            Opti.ub[name] = tmpub
                            
                        else:
                            Opti.xprior[name]  = np.concatenate((Opti.xprior[name], tmp))
                            (Opti.x_ind4map[name][0]).extend([ireg]*len(tmp))
                            (Opti.x_ind4map[name][1]).extend(range(len(tmp)))
                            
                            # -- Boundaries
                            Opti.lb[name] = np.concatenate((Opti.lb[name],tmplb))
                            Opti.ub[name] = np.concatenate((Opti.ub[name],tmpub))
                            
                    icnt+=1
                        
            # Same with dimension 2 when region-dependent
            else:
                sys.exit('Improper dimensions')
                
# END initopti_x
# ==============================================================================



# ==============================================================================
# Variable transformation 
# ------------------------------------------------------------------------------
def transfovar(Vars, Opti, mode = None, xonly = None):



    # Physical to transformed values
    if mode == 'forward':
        
        if xonly == None:
            
            for name in Vars.vars['opti_varname']:                     
                if Vars.vars[name]['transform'] == 'linear':
                    Opti.chi[name]  = np.divide(Opti.x[name]-Opti.xprior[name],Opti.sigma[name])
                    Opti.chi_lb[name] = np.divide(Opti.lb[name]-Opti.xprior[name],Opti.sigma[name])
                    Opti.chi_ub[name] = np.divide(Opti.ub[name]-Opti.xprior[name],Opti.sigma[name])
                    Opti.chi_eps[name] = np.divide(Opti.eps[name], Opti.sigma[name])

                    print 'transfovar chi_eps ',name, Opti.chi_eps[name]

                if Vars.vars[name]['transform'] == 'norm':
                    Opti.chi[name]  = (Opti.x[name]-Opti.lb[name])/(Opti.ub[name]-Opti.lb[name])
                    Opti.chi_prior[name]  = (Opti.xprior[name]-Opti.lb[name])/(Opti.ub[name]-Opti.lb[name])
                    Opti.chi_lb[name] = np.zeros(len(Opti.x[name]), np.float64)
                    Opti.chi_ub[name] = np.ones(len(Opti.x[name]), np.float64)

                    Opti.chi_eps[name] = np.divide(Opti.eps[name], (Opti.max[name]-Opti.min[name]))                    

        else:

            for name in Vars.vars['opti_varname']:
                if Vars.vars[name]['transform'] == '':
                    Opti.chi[name]  = Opti.x[name]

                if Vars.vars[name]['transform'] == 'linear':
                    Opti.chi[name]  = np.divide(Opti.x[name]-Opti.xprior[name],Opti.sigma[name])                    

                if Vars.vars[name]['transform'] == 'norm':
                    Opti.chi[name]      = (Opti.x[name]-Opti.lb[name])/(Opti.ub[name]-Opti.lb[name])


    # Transformed to physical values
    if mode == 'reverse':
        
        for name in Vars.vars['opti_varname']:

            if Vars.vars[name]['transform'] == '':
                Opti.x[name]      = Opti.chi[name]
                
            if Vars.vars[name]['transform'] == 'linear':
                Opti.x[name]      = np.multiply(Opti.chi[name],Opti.sigma[name])+Opti.xprior[name]
                
            if Vars.vars[name]['transform'] == 'norm':
                Opti.x[name]      = Opti.lb[name] + Opti.chi[name]*(Opti.ub[name]-Opti.lb[name])

            if Opti.xmask[name].count() < len(Opti.xmask[name]):
                buf = np.ma.array(Opti.x[name])
                np.ma.putmask(buf,Opti.xmask[name].mask, Config.missval[0])
                Opti.x[name] = np.array(buf)

# END transfovar
# ==============================================================================



# ==============================================================================
# Adjust the value of the observation uncertainties
# ------------------------------------------------------------------------------
def adjust_test(Site, Data, Opti, Vars, logfile):


    # --- Adjust sigma for daily and diurnal cycles so that they have the
    #     same weight in the misfit function for a given observation
    if Data.adjust_daily_diurnal == True \
       and Data.tempo_res == 'daily_diurnal' \
       and Opti.nloop == Opti.nloop_adjust_daily_diurnal:

        adjust_sigma_obs(Site, Data, Opti, logfile, case = 'daily_diurnal')                          

        # - Return to initial optimization conditions
        print '*** ATTENTION, je modifie BFGS_start => on recommence'
        logfile.write('\n*** ATTENTION, je modifie BFGS_start => on recommence\n')
        initialize.reboot(Opti, Vars)


        Data.adjust_daily_diurnal = False

        
    # --- According to their partial Chi2
    if Data.adjust_chi2_obs == True \
       and Opti.nloop == Opti.nloop_adjust_chi2:
        
        adjust_sigma_obs(Site, Data, Opti, logfile, case = 'chi2')
        
        # - Return to initial optimization conditions
        print '*** ATTENTION, je modifie BFGS_start => on recommence'
        logfile.write('\n*** ATTENTION, je modifie BFGS_start => on recommence\n')
        initialize.reboot(Opti, Vars)

        Data.adjust_chi2_obs = False

    
    # --- According to their respective weight in the misfit function
    if Data.adjust_contrib_MF_obs == True:
        if Opti.nloop == 0:
            for name in Data.obsname_opti:
                Data.vars[isite][name]['coef_contrib'] = np.ones(1, np.float64)
                
        if Opti.nloop == Opti.nloop_modif_contrib_obs:
            adjust_sigma_obs(Site, Data, Opti, logfile, case = 'adjust_contrib_MF_obs')
            
            # - Return to initial optimization conditions
            print '*** ATTENTION, je modifie BFGS_start => on recommence'
            logfile.write('\n*** ATTENTION, je modifie BFGS_start => on recommence\n')
            initialize.reboot(Opti, Vars)

            Data.adjust_contrib_MF_obs = False
        
# END adjust_test
# ==============================================================================



# ==============================================================================
# Adjust the value of the observation uncertainties
# ------------------------------------------------------------------------------
def adjust_sigma_obs(Site, Data, Opti, logfile, case = None):

       
    # --- Adjust the partial Chi2 of each observation
    if case =='chi2':

        print
        print ' -----------------------------------------------------------------------'
        print ' + OPTIMISATION : adjust the partial Chi2 of each observation at loop #', Opti.nloop
        print '                  compute  new values for sigma_obs and Data.R'
        print ' -----------------------------------------------------------------------'

        logfile.write('\n ----------------------------------------------------------------------- \n')
        logfile.write(' + OPTIMISATION : adjust the partial Chi2 of each observation at loop #' +str(Opti.nloop) + '\n')
        logfile.write('                  compute  new values for sigma_obs and Data.R \n')
        logfile.write(' ----------------------------------------------------------------------- \n')
        
        
        # Compute the partial chi2
        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                Yobs = Data.obs[isite][name]
                obs_mask = np.ma.masked_where(Yobs <= Config.missval[0], Yobs)
                Yobs = np.ma.masked_where(Yobs >= Config.missval[1], obs_mask)
                nobsi = Yobs.count()
                chi2 = 2*Opti.MFobs[isite][name]/nobsi

                # Modify sigma as follow:
                print name,Data.vars[isite][name]['sigma'], '->',
                logfile.write(name + ' ' + str(Data.vars[isite][name]['sigma']) + ' -> ')
            
                Data.vars[isite][name]['sigma'] = Data.vars[isite][name]['sigma']*np.sqrt(chi2)
                
                print Data.vars[isite][name]['sigma'], '  | correction = SQRT(Chi2) = ',np.sqrt(chi2)
                logfile.write(str(Data.vars[isite][name]['sigma']) +  '  | correction = SQRT(Chi2) = '+str(np.sqrt(chi2))+'\n')
                           
        # And finally modify Data.R
        prior.detmatcov_obs(Data, logfile, init = False)

        
        # Test
        print '   Check that the partial Chi2 are now computed according to what was expected...'
        logfile.write('   Check that the partial Chi2 are now computed according to what was expected... \n')
        
        sumMF = 0
        sumNobs = 0
        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                
                # Set the data name to distinguish data from each site :
                # 'data name for the site' = 'data name'_'site number'
                name_site = name+'_'+Site.name[isite]
                
                Yobs = Data.obs[isite][name]
                Ysim = Data.sim_ref[isite][name]
                
                obs_mask = np.ma.masked_where(Yobs <= Config.missval[0], Yobs)
                Yobs = np.ma.masked_where(Yobs >= Config.missval[1], obs_mask)
                sim_mask = np.ma.masked_where(Ysim <= Config.missval[0], Ysim)
                sim = np.ma.masked_where(Ysim >= Config.missval[1], sim_mask)
                
                MF = np.sum(np.ma.divide((Yobs - Ysim)**2,Data.R[name_site]).compressed())
                sumMF = sumMF+MF
                sumNobs = sumNobs + Yobs.count()
                chi2_new = 2*MF/Yobs.count()
                print '   - Chi2_'+name + ' = ',chi2_new
                logfile.write('   - Chi2_'+name  + ' = ' + str(chi2_new) + '\n')
            
        print '   - Chi2_total / nobs_total = ', 2*sumMF/sumNobs
        print
        logfile.write('   - Chi2_total / nobs_total = ' +str(2*sumMF/sumNobs) + '\n')


    
    # --- Apply a correction on sigma obs so that the respective weight of
    #     a given obs in the misfit function is Data.vars[name]['coef_contrib']
    if case == 'adjust_contrib_MF_obs':

        print
        print ' ---------------------------------------------------------------------------------------------'
        print ' + OPTIMISATION  : Estimation of the correction coefficient for MFobs contribution at nloop # ', Opti.nloop
        print ' -----------------------------------------------------------------------------------------------'

        logfile.write('\n --------------------------------------------------------------------------------------------- \n')
        logfile.write(' + OPTIMISATION  : Estimation of the correction coefficient for MFobs contribution at nloop # ' + str(Opti.nloop) + '\n')
        logfile.write(' ----------------------------------------------------------------------------------------------- \n')

        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:

                # Set the data name to distinguish data from each site :
                # 'data name for the site' = 'data name'_'site number'
                name_site = name+'_'+Site.name[isite]
            
                MFobs = Opti.MFobs[name_site]

                Data.vars[isite][name]['coef_contrib'] = np.array(Data.vars[isite][name]['contrib_MF_obs'] * Opti.MFobs['total']/MFobs, np.float64)

                print '   - '+name_site+ ' : correction of sigma by a factor ', np.sqrt(Data.vars[isite][name]['coef_contrib'])
                print '      ',Data.vars[isite][name]['sigma'], '->',
                logfile.write('   - '+name_site+ ' : correction of sigma by a factor ' + str(np.sqrt(Data.vars[isite][name]['coef_contrib'])) +'\n')
                logfile.write('      ' + str(Data.vars[isite][name]['sigma']) + ' -> \n')
            
                Data.vars[isite][name]['sigma'] = Data.vars[isite][name]['sigma'] / np.sqrt(Data.vars[isite][name]['coef_contrib'])
            
                print '  ',Data.vars[isite][name]['sigma']
                logfile.write('  ' +str(Data.vars[isite][name]['sigma']) +'\n')
                        
        # Recompute Data.R
        prior.detmatcov_obs(Data, logfile, init = False)

           
    print



    # --- Adjust sigma between daily data & diurnal cycles so the corresponding data
    #     have the weight in the misfit function
    #     
    if case == 'daily_diurnal':
        print
        print ' -----------------------------------------------------------------------------'
        print ' + OPTIMISATION : Adjust sigma between daily and diurnal data at nloop # ', Opti.nloop
        print ' -----------------------------------------------------------------------------'
        
        logfile.write('\n ----------------------------------------------------------------------------- \n')
        logfile.write(' + OPTIMISATION : Adjust sigma between daily and diurnal data at nloop # ' +str(Opti.nloop) + '\n')
        logfile.write(' ----------------------------------------------------------------------------- \n')

        for isite in range(Site.npts):
            
            for name in Data.obsname[isite]:
                if name != 'fAPARt':
                    
                    # Set the data name to distinguish data from each site :
                    # 'data name for the site' = 'data name'_'site number'
                    name_site = name+'_'+Site.name[isite]
                    
                    coef_diurnal = Opti.MFobs[name_site] / Opti.MFobs[name_site+'_diurnal']
                    coef_daily = 1

                    print '   - '+name_site+ ' : correction of sigma by a factor ', np.sqrt(coef_daily)
                    print '   - '+name_site+ '_diurnal : correction of sigma by a factor ', np.sqrt(coef_diurnal)
                    logfile.write('   - '+name_site+ ' : correction of sigma by a factor ' +str(np.sqrt(coef_daily)) + '\n')
                    logfile.write('   - '+name_site+ '_diurnal : correction of sigma by a factor ' + str(np.sqrt(coef_diurnal)) + '\n') 


                    Data.vars[name]['sigma'] = Data.vars[name]['sigma'] / np.sqrt(coef_daily) 
                    Data.vars[name+'_diurnal']['sigma'] = Data.vars[name+'_diurnal']['sigma'] / np.sqrt(coef_diurnal) 
                    
                    print

                
        # Recompute Data.R
        prior.detmatcov_obs(Data, logfile, init = False)
        

        # Test
        print '   Check that the relative contribution of daily & diurnal parts are the same...'
        logfile.write('   Check that the relative contribution of daily & diurnal parts are the same... \n')

        for isite in range(Site.npts):

            for name in Data.obsname[isite]:
                if name != 'fAPARt':

                    # Set the data name to distinguish data from each site :
                    # 'data name for the site' = 'data name'_'site number'
                    name_site = name+'_'+Site.name[isite]
                    
                    ext = ['','_diurnal']
                    MF = []
                    for elem in ext:
                        fname = name_site+elem
                        Yobs = Data.obs[fname]
                        Ysim = Data.sim_ref[fname]
                        obs_mask = np.ma.masked_where(Yobs <= Config.missval[0], Yobs)
                        Yobs = np.ma.masked_where(Yobs >= Config.missval[1], obs_mask)
                        sim_mask = np.ma.masked_where(Ysim <= Config.missval[0], Ysim)
                        sim = np.ma.masked_where(Ysim >= Config.missval[1], sim_mask)
                    
                        MF.append( np.sum(np.ma.divide((Yobs - Ysim)**2,Data.R[fname]).compressed()) )

                    print '    - MF_ '+name_site,MF
                    logfile.write('    - MF_ '+name_site +str(MF) + '\n')
                    
        logfile.write('\n')
    print




    
# END adjust_sigma_obs
# ==============================================================================





# ==============================================================================
# Return the misfit function and its derivative
#
#
# At the end of the optimization process, a convergence test is applied to determine
# to which extent the misfit function for xj is a minimum:
# The convergence on the misfit function around the minimum is performed by perturbing
# each parameter value by +-2*eps and studying its impact on MF
#
# ------------------------------------------------------------------------------
def main(Vars, Vars_site, Site, Data, Opti, test_convergence, logfile, check = None):

    # Writing level
    # -----------------
    # 1 in this module
    if check == None: check == 0


    # ----------------------------------
    # - Structures for saving results --
    # ----------------------------------
    
    # Misfit Function
    Opti.gradMF = np.zeros(Opti.n, np.float64)
    for isite in range(Site.npts):
        for name in Data.obsname_opti[isite]:
            name_site = name+'_'+Site.name[isite]        
            Opti.gradMFobs[name_site] = np.zeros(Opti.n, np.float64)
            
    Opti.gradMFobs['total'] = np.zeros(Opti.n, np.float64)
    Opti.gradMFpar = np.zeros(Opti.n, np.float64)

    # Jacobian
    Data.Jacobian = np.zeros( (Opti.n, Data.nobs), np.float64)
    Data.Jacobian_site = {}
    for isite in range(Site.npts):
        Data.Jacobian_site[isite] = np.zeros( (Opti.ns[isite], Data.nobs_site[isite]), np.float64)
    
    # ------------------------------------------------------------------------
    #  Compute the misfit function with initial parameters, for all the sites
    # ------------------------------------------------------------------------
    if check >=1:
        print '\n  + OPTIMISATION.FMISFIT : Computation of the misfit function...'
        logfile.write('  + OPTIMISATION.FMISFIT : Computation of the misfit function... \n')
  
    Fmisfit = fmisfit_calc(Vars, Vars_site, Site, Data, Opti, logfile, check = check)
    Data.sim_ref = copy.deepcopy(Data.sim)
    
    #- Write current simulations in opti_sim.nc
    if Opti.save_sim_iter == True:
        funcio.write_fluxes(os.path.join(Config.PATH_MAIN_TMP,'opti_sim'+str(Opti.nloop)+'.nc'), Data, Site, datacase = 'sim', mode = 'w')

    #- Allocate the result class
    Opti.MF = Fmisfit.MF
    Opti.MFobs = Fmisfit.MFobs
    Opti.MFpar = Fmisfit.MFpar

    
    #- correction factor for eps for So_capa_dry and So_capa_wet
    coef_eps_std = 1
    coef_eps_capa = 1.e6
       
    #- Results history 
    if test_convergence == False:

        Opti.hist_MFpar.append(Opti.MFpar)
        Opti.hist_MF.append(Opti.MF)

        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                name_site = name+'_'+Site.name[isite]    
                Opti.hist_MFobs[name_site].append(Opti.MFobs[name_site])
        Opti.hist_MFobs['total'].append(Opti.MFobs['total'])


    # --------------------------------------------
    #  Stop here if we were just scanning Fmisfit
    # --------------------------------------------
    if Opti.scan_fmisfit_prior == True:
        return   


    
    # -----------------------------------------------
    #  Compute the gradient of the misfit function
    #  Compute the Jacobian matrix of the model 
    # -----------------------------------------------
    print
    if test_convergence == False: 
        
        if check >=1:
            print '  + OPTIMISATION.FMISFIT : Computation of the misfit function derivative...'
            logfile.write('  + OPTIMISATION.FMISFIT : Computation of the misfit function derivative...\n')


        ipar = 0
        ipar_s = {}
        for isite in range(Site.npts):
            ipar_s[isite]={}
            for obsname in Data.obsname_opti[isite]:ipar_s[isite][obsname]=0

        # - Loop on the parameters
        
        for name in Vars.vars['opti_varname']: 

            #print name

            # correction coef for So_capa_xxx
            coef_eps = 1
            if name in ['So_capa_wet','So_capa_dry'] : coef_eps = coef_eps_capa

            print
            print '\n  + Derivee de Fmisfit pour ', name
            print
            logfile.write('\n  + Derivee de Fmisfit pour '+ name + '\n\n')
            
            
            # - indices of the non-masked elements : should crash if the mask is badly done
            ind = np.ma.masked_array(np.ma.arange(len(Opti.x[name].ravel())), Opti.xmask[name].mask)
            
            #print name

            # -
            for i in range(len(Opti.xmask[name])):
            
                #print i

                # - skip if undefined element
                if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue

                print '\n  Component ', Opti.xname[ipar]
                logfile.write('\n  Component '+ Opti.xname[ipar] + '\n')

                # ----------------------------------------------------------------------------------------
                # Select which sites are concerned by the perturbation of the parameter component
                # (in order to avoid running ORCHIDEE pointlessly and waste calculation time) :
                #
                # Parameter PFT,region : only those in the corresponding region with the corresponding PFT
                # Parameter PFT        : only those with the corresponding PFT
                # Parameter Region     : only those in the corresponding region
                # Parameter Site       : only the corresponding site
                # Parameter Global     : all the sites
                # ----------------------------------------------------------------------------------------
                
                if 'indice_region' in Vars.vars[name]['dim_name'] and 'indice_pft' in Vars.vars[name]['dim_name']:
                    concerned_sites = []
                    imap = Vars.vars[name]['map']
                    ireg = Opti.x_ind4map[name][0][i]
                    ipft = Opti.x_ind4map[name][1][i]
                    name_pft = Vars.vars['PFT']['value'][imap][ireg][ipft]
                    #print 'map ',imap, 'region ',ireg, 'ipft ',ipft, 'pft ',name_pft
                    for isite in Site.site_ind[imap][ireg]:
                        #print 'site ',isite, 'pfts ',Site.indice_pft[isite]
                        if name_pft in Site.indice_pft[isite]:concerned_sites.append(isite)
                        
                elif 'points_terre' in Vars.vars[name]['dim_name'] and 'indice_pft' in Vars.vars[name]['dim_name']:
                    for isite in range(Site.npts):
                        if i in Vars.vars['PFT_site']['indexes'][isite]:
                            concerned_sites = [isite]
                            break

                elif 'indice_pft' in Vars.vars[name]['dim_name']:
                    concerned_sites = []
                    name_pft = Vars.vars['PFT_global']['value'][i]
                    #print 'pft ',name_pft
                    for isite in range(Site.npts):
                        if name_pft in Site.indice_pft[isite]:concerned_sites.append(isite)

                elif 'indice_region' in Vars.vars[name]['dim_name']:
                    imap = Vars.vars[name]['map']
                    ireg = Site.map['occupied_regions'][imap][i]
                    concerned_sites = copy.copy(Site.site_ind[imap][ireg])
                    #print 'map ',imap, 'region ',ireg
                    
                elif 'points_terre' in Vars.vars[name]['dim_name']:
                    concerned_sites = [i]
                    
                #print concerned_sites
                # -----------

                value_tl = None
                dim_tl   = None
                    
                # --Tangent Linear Model : initialization --
                # --------------------------------------------
                if Vars.vars[name]['deriv'] == 'tl':

                    # Create the value_tl variable indicating which parameter index has to be TLed.
                    value_tl = np.zeros(Opti.x[name].shape, np.int32)
                    np.put(value_tl,ind[i],1)

                    dim_tl = copy.copy(Vars.vars[name]['dim_name'])


                # -- Finite differences : initialization --
                # ------------------------------------------
                if Vars.vars[name]['deriv'] == 'finite_differences':

                    # - copy the original parameter values
                    valOri = copy.deepcopy(Vars.vars[name]['value'])

                    if 'indice_region' in Vars.vars[name]['dim_name'] and 'indice_pft' in Vars.vars[name]['dim_name']:
                        ireg = (Opti.x_ind4map[name][0])[i]
                        indice = (Opti.x_ind4map[name][1])[i]
                        buf = np.take(Vars.vars[name]['value'][ireg].ravel(), (indice,), axis=0)
                        np.put(Vars.vars[name]['value'][ireg],indice,buf + Vars.vars[name]['eps'])
                    else:
                        buf = np.take(Vars.vars[name]['value'].ravel(), (ind[i],), axis=0)
                        np.put(Vars.vars[name]['value'],ind[i],buf + Vars.vars[name]['eps'])

                    # --- Propagate the perturbation of Vars to Vars_site
		    for isite in concerned_sites:
                        Vars_site[isite].vars[name]['value'] = various.vars_to_site(isite, name, Vars, Site)


                # -- Misfit function and gradients --
                # -----------------------------------
                Fmisfit = fmisfit_calc(Vars, Vars_site, Site, Data, Opti, logfile, 
                                       varname = name, value_tl = value_tl, ipar = ipar, deriv = Vars.vars[name]['deriv'],
                                       calc_gradient = True,  coef_eps = coef_eps, dim_tl = dim_tl, indice = i, select_sites = concerned_sites,
                                       check = check)

                #  Finite differences: restore the original parameter values 
                if Vars.vars[name]['deriv'] == 'finite_differences':  
                    Vars.vars[name]['value'] = copy.deepcopy(valOri)
		    for isite in concerned_sites:
                        Vars_site[isite].vars[name]['value'] = various.vars_to_site(isite, name, Vars, Site)


                # -- Observations --
                # -------------------
                for isite in concerned_sites:
                    for obsname in Data.obsname_opti[isite]:
                        
                        name_site = obsname+'_'+Site.name[isite]
                        np.put(Opti.gradMFobs[name_site], ipar, Fmisfit.gradMFobs[name_site])
                        print '       - gradient for '+name_site,Fmisfit.gradMFobs[name_site]#,' / ',Opti.MFobs[name_site],Fmisfit.MFobs[name_site]
                        logfile.write('       - gradient for '+name_site + ' : '+str(Fmisfit.gradMFobs[name_site]) + '\n')#' / '+str(Fmisfit.MFobs[name_site])+'\n')                

                np.put(Opti.gradMFobs['total'], ipar, Fmisfit.gradMFobs['total'])


                # -- Parameters --
                # ----------------
                np.put(Opti.gradMFpar, ipar, Fmisfit.gradMFpar[ipar])

 
                # -- Jacobian --
                # --------------
                # Compute the Jacobian matrix of ORCHIDEE for each observation field
                i0 = 0
                
                for isite in range(Site.npts):

                    i1 = 0

                    for obsname in Data.obsname_opti[isite]:
                        
                        nts = len(Data.obs[isite][obsname].ravel())
                        name_site = obsname+'_'+Site.name[isite]

                        ## The Jacobian for this site is null if the perturbation does not affect this site !
                        if isite in concerned_sites:
                            Data.Jacobian[ipar, i0:i0+nts] = Fmisfit.Jacobian[name_site]
                            
                            # Fill the "site-Jacobian" for each site
                            if Site.name[isite] not in Opti.sitename[ipar]: sys.exit('Inconsistency between concerned_sites and Opti.sitename !!')
                            Data.Jacobian_site[isite][ipar_s[isite][obsname], i1:i1+nts] = Fmisfit.Jacobian[name_site]
                            ipar_s[isite][obsname]+=1
                            i1 = i1+nts

                        else:
                            Data.Jacobian[ipar, i0:i0+nts] = np.zeros(nts , np.float64)


                        i0 = i0+nts
                        

                # - Total --
                # -----------
                if Opti.Fmisfit_space == 'obs-par' :  Opti.gradMF[ipar] = Opti.gradMFobs['total'][ipar] + Opti.gradMFpar[ipar]
                if Opti.Fmisfit_space == 'obs'     :  Opti.gradMF[ipar] = Opti.gradMFobs['total'][ipar] 
                if Opti.Fmisfit_space == 'par'     :  Opti.gradMF[ipar] = Opti.gradMFpar[ipar]
                
                print '       - gradient for MF  ',Opti.gradMF[ipar]#,' / ',Fmisfit.MF,Opti.MF
                logfile.write('       - gradient MF :' + str(Opti.gradMF[ipar])+'\n\n')# + ' / ' + str(Fmisfit.MF) +' , '+ str(Opti.MF) +'\n\n')
                    
                ipar+=1
                             
                
        print
        print ' + fmisfit :'
        print '    - MF :', Opti.MF
        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                name_site = name+'_'+Site.name[isite]  
                print '    + MF_'+name_site+' :', Opti.MFobs[name_site]
        ###    print '    + Chi_'+name_site+' :', 2*Opti.MFobs[name_site]/len(Data.obs[name_site])
        print '    - MFpar :', Opti.MFpar
        print '    - gradMF :', Opti.gradMF


        logfile.write('\n + fmisfit :\n')
        logfile.write('    - MF : ' + str(Opti.MF) + '\n')
        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                name_site = name+'_'+Site.name[isite]  
                logfile.write('    - MF_'+name_site+' : ' + str(Opti.MFobs[name_site]) + '\n')
        logfile.write('    - MFpar : ' + str(Opti.MFpar) + '\n')
        logfile.write('    - gradMF : ' + str(Opti.gradMF) + '\n')
                

        # -- Restore original values for Opti.x and Opti.chi --
        # ----------------------------------------------------
        initopti(Vars, Site, Opti, cas  = 'xonly')
        transfovar(Vars, Opti, mode = 'forward', xonly = 'y')
        initopti(Vars, Site, Opti, cas  = 'xall')

        # -- Results history --
        # ---------------------
        for name in Vars.vars['opti_varname']:
            Opti.hist_x[name].extend(Opti.x[name])
            
        #- Gradient
        Opti.hist_gradMF['MFpar'].append(Opti.gradMFpar)
        Opti.hist_gradMF['MF'].append(Opti.gradMF)
        Opti.hist_gradMF['MFobs_total'].append(Opti.gradMFobs['total'])
        
        for isite in range(Site.npts):
            for oname in Data.obsname_opti[isite]:
                name_site = oname+'_'+Site.name[isite]  
                Opti.hist_gradMF['MFobs_'+name_site].append(Opti.gradMFobs[name_site])

    # end of computation of the misfit function gradient

        
    # -----------------------------------------------
    #  Sensitivity test around the minimum of MF
    # -----------------------------------------------

    if test_convergence == True: 
        
        #-- Variation coefficients for the parameters
        #  variation of the parameters around the posterior
        #  value by the amount of Opti.pcvar% of their variation range
        coefs = np.arange(-(Opti.nlevels-1)/2, (Opti.nlevels-1)/2+0.001,1)

                        
        #-- Structure for saving results
        Opti.sensiMF = np.zeros((Opti.n,Opti.nlevels), np.float64)
        Opti.sensiMFobs = {}
        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                name_site = name+'_'+Site.name[isite]                            
                Opti.sensiMFobs[name_site] = np.zeros((Opti.n,Opti.nlevels), np.float64)
        Opti.sensiMFobs['total'] = np.zeros((Opti.n,Opti.nlevels), np.float64)
        Opti.sensiMFpar = np.zeros((Opti.n,Opti.nlevels), np.float64)

        
        #-- Computation
        icnt = 0

        print '# Sensitivity of the misfit function '
        logfile.write(' \n# Sensitivity of the misfit function \n')

        for name in Vars.vars['opti_varname']:
            print '   - ' +name, ': ' ,Opti.x[name]
            logfile.write('   - ' +name+ ': ' + str(Opti.x[name]) + '\n')


            
        for name in Vars.vars['opti_varname']:

            print
            print '\n + Sensitivity of ',name
            logfile.write('\n + Sensitivity of ' + name + '\n')
                
                
            # - indices of the non-masked elements
            ind = np.ma.masked_array(np.ma.arange(len(Vars.vars[name]['value'].ravel())), Opti.xmask[name].mask)

            for i in range(len(Opti.xmask[name])):

                if type(Opti.xmask[name][i]) == type(np.ma.masked):  continue
                   
                vmin =  np.take(Opti.lb[name].ravel(), (ind[i],), axis=0)[0]
                vmax =  np.take(Opti.ub[name].ravel(), (ind[i],), axis=0)[0]
                step = np.array((vmax-vmin)/(Opti.nlevels-1), np.float64) * Opti.pcvar/100.
                
                value = np.take(Vars.vars[name]['value'].ravel(), (ind[i],), axis=0)[0]
                sensi_value = np.arange(value-int(Opti.nlevels/2)*step, value+int(Opti.nlevels/2)*step+0.001, step)
                # restrict the simulation interval to the definition domain
                ###sensi_value = np.clip(sensi_value,Vars.vars[name]['min'],Vars.vars[name]['max'])
                vmin = np.take(Vars.vars[name]['min_opti'].ravel(), (ind[i],), axis=0)[0]
                vmax = np.take(Vars.vars[name]['max_opti'].ravel(), (ind[i],), axis=0)[0]
                sensi_value = np.clip(sensi_value,vmin,vmax)
                
                for istep in range(Opti.nlevels):
                    
                    # - copy the original parameter values
                    valOri = np.array(Vars.vars[name]['value'], np.float64)
                    
                    # - compute F for the current parameter perturbation
                    np.put(Vars.vars[name]['value'],ind[i],sensi_value[istep])
                    
                    Fmisfit = fmisfit_calc(Vars, Vars_site, Site, Data, Opti, logfile,
                                           varname = name, ipar = ipar, deriv = 'finite_differences',
                                           calc_gradient = True, coef_eps = coef_eps, check = check)
                    
                    # - restore the original values
                    Vars.vars[name]['value'] = valOri          
                    
                    # - Variation of MF for the parameter part
                    Opti.sensiMFpar[icnt][istep] = np.put(Opti.gradMFpar, ipar, Fmisfit.gradMFpar[ipar])
                    
                    # - Variation of MF for the observation part
                    Opti.Fmisfit = {}

                    for isite in range(Site.npts):
                        for oname in Data.obsname_opti[isite]:
                            name_site = oname+'_'+Site.name[isite]                        
                            Opti.sensiMFobs[name_site][icnt][istep] =  (Fmisfit.MFobs[name_site]-Opti.MFobs[name_site])[0]                          
                    Opti.sensiMFobs['total'][icnt][istep] = (Fmisfit.MFobs['total']-Opti.MFobs['total'])[0]
                    
                    # -Variation of MF total
                    Opti.sensiMF[icnt][istep]= (Fmisfit.MF-Opti.MF)[0]
                        
                
                icnt+=1
       


        #- total
        
        if Opti.Fmisfit_space == 'obs-par' :  Opti.sensiMF = Opti.sensiMFobs['total'] + Opti.sensiMFpar
        if Opti.Fmisfit_space == 'obs'     :  Opti.sensiMF = Opti.sensiMFobs['total'] 
        if Opti.Fmisfit_space == 'par'     :  Opti.sensiMF = Opti.sensiMFpar
          
    
        
        
        # --- Restore original values for Opti.x and Opti.chi ---
        # ------------------------------------------------------
        initopti(Vars, Site, Opti, cas  = 'xonly')
        transfovar(Vars, Opti, mode = 'forward', xonly = 'y')
        initopti(Vars, Site, Opti, cas = 'xall')

    # end of computation of the sensitivity around the minimum

    
# END fmisfit
# ==============================================================================




# ==============================================================================
# Return the misfit function and its derivative
#
#   Run an ORCHIDEE simulation from the current parameter values => SIM
#   Determine the misfit function between OBS and SIM
# ------------------------------------------------------------------------------
def fmisfit_calc( Vars, Vars_site, Site, Data, Opti, logfile,
                  varname       = None,
                  ipar          = None,
                  deriv         = None,
                  value_tl      = None,
                  calc_gradient = False,
                  coef_eps      = 1,
                  dim_tl        = None,
                  indice        = None,
                  select_sites  = None,
                  check         = None):
    

  
    # Writing level
    # -----------------
    # 3 in this module
    if check == None: check = 0

    #
    if select_sites != None:
        concerned_sites = select_sites
    else :
        concerned_sites = range(Site.npts)
    
    # -----------------
    #  Launch ORCHIDEE 
    # -----------------
    varname_tl = None
    if deriv == 'tl': varname_tl = varname

    for isite in concerned_sites:

        # --- Adapt the TL variable for each site if needed
        if deriv == 'tl' and dim_tl != None :

            if 'indice_pft' in dim_tl:

                if 'indice_region' in dim_tl:
                    
                #print 'in tl : indice_pft et indice_region'
                    imap = Vars.vars[varname]['map']
                    ireg = Opti.x_ind4map[varname][0][indice]
                    max = len(Site.indice_pft[isite])
                    value_tl_used = np.zeros(max, np.int32)
                    
                    ipft = Opti.x_ind4map[varname][1][indice]
                    name_pft = Vars.vars['PFT']['value'][imap][ireg][ipft]
                    
                    temp = np.array(Site.indice_pft[isite], np.int32)
                    mask = np.ma.masked_equal(temp, name_pft).mask
                    temp = np.nonzero(mask)
                    np.put(value_tl_used,temp[0],1)

                elif 'points_terre' in dim_tl:
                    max = len(Site.indice_pft[isite])
                    value_tl_used = np.zeros(max, np.int32)

                    if isite != Opti.x_ind4map[varname][0][indice]:
                        print 'ERROR in the indexes!! ',isite,Opti.x_ind4map[varname][0][indice]
                        sys.exit()
                    ipft = Opti.x_ind4map[varname][1][indice]
                    np.put(value_tl_used,ipft,1)

                else:
                #print 'in tl : indice_pft global'
                    max = len(Site.indice_pft[isite])
                    value_tl_used = np.zeros(max, np.int32)
                    
                    name_pft = Vars.vars['PFT_global']['value'][indice]
                    
                    temp = np.array(Site.indice_pft[isite], np.int32)
                    mask = np.ma.masked_equal(temp, name_pft).mask
                    temp = np.nonzero(mask)
                    np.put(value_tl_used,temp[0],1)
                    
            else :

                value_tl_used = np.array((1), np.int32)
                
        else:
            value_tl_used = None

        #print '******** tl data *********'
        #print Site.name[isite]
        #print varname_tl
        #print dim_tl
        #print value_tl_used
        #print '**************************'

        os.chdir(Config.PATH_EXEC_SITE[isite])
        print Site.name[isite]
        orchidee.launch(isite, Vars_site[isite], Site, Data, logfile, check = check, varname_tl = varname, value_tl = value_tl_used)
            

    os.chdir(Config.PATH_MAIN_TMP)
    
    # ------------------------------------
    #  Determine the parameters component
    # ------------------------------------
    # get Opti.x from Vars.vars['value']
    initopti(Vars, Site, Opti, cas = 'xonly') 
    # variable transformation : get current Opti.chi
    transfovar(Vars, Opti, mode = 'forward', xonly = 'y' )
    # Opti.x['all'] and Opti.chi['all']
    initopti(Vars, Site, Opti, cas = 'xall')

    print "FMISFIT : x", Opti.x['all']
    print "FMISFIT : chi", Opti.chi['all']
    
    # -----------------------------
    #  Compute the misfit function
    # -----------------------------

    
    # --- Observation part ---
    # ------------------------

    # output structures
    MFobs = {}
    MFobs['total'] = np.zeros((1), np.float64)
    
    if calc_gradient == True:
        gradMFobs = {}
        gradMFobs['total'] = np.zeros(1, np.float64)
        Jacobian = {}

    for isite in range(Site.npts):
            
        for name in Data.obsname_opti[isite]:
        
            # Set the data name to distinguish data from each site :
            # 'data name for the site' = 'data name'_'site number'
            name_site = name+'_'+Site.name[isite]


            Yobs     = Data.obs[isite][name]
            Ysim     = Data.sim[isite][name]
            if deriv == 'finite_differences' and Opti.method_gradJ_fd == 2 and calc_gradient == True :
                Ysim = Data.sim_ref[isite][name] 
                                    
            # - Deal with the missing values
            obs_mask = np.ma.masked_where(Yobs <= Config.missval[0], Yobs)
            Yobs = np.ma.masked_where(Yobs >= Config.missval[1], obs_mask)
        
            sim_mask = np.ma.masked_where(Ysim <= Config.missval[0], Ysim)
            Ysim = np.ma.masked_where(Ysim >= Config.missval[1], sim_mask)

            Yres = Ysim - Yobs
            nobs = len(Ysim)

            # - Weighted least square
            MFobs[name_site] = 0.5*np.sum((Yres**2)/Data.R[name_site])
            MFobs[name_site] = np.array((MFobs[name_site],), np.float64)
        
            # - Total                        
            MFobs['total'] = MFobs['total']+MFobs[name_site]

            if check >=3 : print '   . MFobs['+name_site+']='+str(MFobs[name_site])
            
            if MFobs['total'] <= 0:
                print '# STOP # PYS_ORCHIS : OPTIMIZATION. Problem : MFobs_total = 0'
                logfile.write('# STOP # PYS_ORCHIS : OPTIMIZATION. Problem : MFobs_total = 0 \n')
                sys.exit('# STOP # PYS_ORCHIS : OPTIMIZATION. Problem : MFobs_total= 0')
            
            # -- Gradient of the misfit function
            #    (dM/dx)^t.R^(-1).(M(x)-y) by defaut
            #    particular case for Finite Differences (method 1): (J(x+eps)-J(x)) / eps
            if calc_gradient == True: 
                
                gradMFobs[name_site] = np.zeros(1, np.float64)

                if isite in concerned_sites:
                    if deriv == "tl":
                        Sim_tl = Data.sim[isite][name+'_tl']
                    else:
                        Sim_tl = (Data.sim[isite][name] - Data.sim_ref[isite][name])/(Opti.eps['all'][ipar]*coef_eps)
                                    
                else:
                    # The sensitivity must be zero is the site is unconcerned by this parameter
                    Sim_tl = np.zeros(Data.sim[isite][name].shape, np.float64)

                Jacobian[name_site] = Sim_tl

                tl_mask = np.ma.masked_where(Sim_tl <= Config.missval[0], Sim_tl)
                Sim_tl = np.ma.masked_where(Sim_tl >= Config.missval[1], tl_mask)

                if isite in concerned_sites:
                    if deriv == "finite_differences" and Opti.method_gradJ_fd == 1:
                        gradMFobs[name_site] = (MFobs[name_site]-Opti.MFobs[name_site])/(Opti.chi_eps['all'][ipar]*coef_eps)
                    else:
                        mf = np.ma.divide(Yres,Data.R[name_site])
                        gradMFobs[name_site] = np.ma.multiply(mf ,Sim_tl).compressed()
                        gradMFobs[name_site] = np.sum(gradMFobs[name_site])*Opti.eps['all'][ipar]/Opti.chi_eps['all'][ipar]

                    if gradMFobs[name_site] == 0. :
                        print
                        print '# WARNING !! site '+name_site+' insensitive its component of '+varname+'...'
                        print
                
                else:
                    gradMFobs[name_site] = 0.


                gradMFobs['total'] = gradMFobs['total']+gradMFobs[name_site]


    # --- Parameter part ---
    # ----------------------

    # output structures
    if calc_gradient == False:
        MFpar = np.zeros((1), np.float64)
    elif calc_gradient == True:
        gradMFpar = np.zeros((Opti.n), np.float64)

    # Actual value of the parameters for the current simulation / used to compute gradient
    x_val = np.zeros(Opti.n)
    icnt = 0
    for name in  Vars.vars['opti_varname']:
        if Opti.xmask[name].count() > 0:
            for i in range(Opti.xmask[name].count()):
                if Vars.vars[name]['deriv'] == 'tl': 
                    x_val[icnt] = Opti.chi['all'][icnt]
                elif Vars.vars[name]['deriv'] == 'finite_differences': 
                    #print "fmisfist_calc / ", name
                    #print "   Vars : ", Vars.vars[name]['value']
                    #print "   Opti.chi['all'][icnt]",Opti.chi['all'][icnt]
                    #print "   Opti.chi_eps['all'][icnt]",Opti.chi_eps['all'][icnt]
                    x_val[icnt] = Opti.chi['all'][icnt]-Opti.chi_eps['all'][icnt]
                icnt=icnt+1

    #-- Value of the misfit function
    #   Misfit for each parameter (=> not accounting for potential covariances)
    # The computation depends on the parameter transformation that is applied
    if calc_gradient == False:
        icnt = 0
        for name in  Vars.vars['opti_varname']:

            # --- No transformation ---
            if  Vars.vars[name]['transform'] == '':
                if Opti.xmask[name].count() > 0:
                    for i in range(Opti.xmask[name].count()):
                        #  skip if undefined element
                        if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue
                        MFpar = MFpar + 0.5*np.divide((Opti.chi['all'][icnt]-Opti.chi_prior['all'][icnt])**2, Opti.B['all'][icnt])       
                        icnt = icnt + 1

            # --- Linear transformation ---
            if Vars.vars[name]['transform'] == 'linear':
                if Opti.xmask[name].count() > 0:
                    for i in range(Opti.xmask[name].count()):
                        #  skip if undefined element
                        if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue
                        MFpar = MFpar + 0.5*(Opti.chi['all'][icnt])**2
                        icnt = icnt + 1

            # --- Norm transformation ---
            if  Vars.vars[name]['transform'] == 'norm':
                if Opti.xmask[name].count() > 0:
                    for i in range(Opti.xmask[name].count()):
                        #  skip if undefined element
                        if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue
                        sigT2 = (Opti.B['all'][icnt])/(Opti.ub['all'][icnt]-Opti.lb['all'][icnt])**2
                        MFpar = MFpar + 0.5*np.divide((Opti.chi['all'][icnt]-Opti.chi_prior['all'][icnt])**2, sigT2)
                        icnt = icnt + 1

        if check >=3:
            print '   - MFpar = '+str(MFpar)
            logfile.write('   - MFpar = '+str(MFpar)+'\n')


        
    #-- Gradient of the misfit function
    elif  calc_gradient == True:
        icnt = 0
        for name in  Vars.vars['opti_varname']:

            # --- No transformation ---
            if  Vars.vars[name]['transform'] == '':
                if Opti.xmask[name].count() > 0:
                    for i in range(Opti.xmask[name].count()):
                        #  skip if undefined element
                        if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue
                        gradMFpar[icnt] =  np.divide((x_val[icnt]-Opti.chi_prior['all'][icnt]), Opti.B['all'][icnt])                    
                        icnt = icnt + 1

            # --- Linear transformation ---
            if Vars.vars[name]['transform'] == 'linear':
                if Opti.xmask[name].count() > 0:
                    for i in range(Opti.xmask[name].count()):
                        #  skip if undefined element
                        if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue
                        gradMFpar[icnt] =  x_val[icnt]
                        icnt = icnt + 1

            # --- Norm transformation ---
            if  Vars.vars[name]['transform'] == 'norm':
                if Opti.xmask[name].count() > 0:
                    for i in range(Opti.xmask[name].count()):
                        #  skip if undefined element
                        if type(Opti.xmask[name][i]) == type(np.ma.masked):   continue
                        sigT2 = (Opti.B['all'][icnt])/(Opti.ub['all'][icnt]-Opti.lb['all'][icnt])**2
                        gradMFpar[icnt] = np.divide((x_val[icnt]-Opti.chi_prior['all'][icnt]), sigT2)                        
                        icnt = icnt + 1



    # --- Total Misfit Total --- 
    # --------------------------
    if  calc_gradient == False:
        if Opti.Fmisfit_space == 'obs-par' :  MF = MFobs['total'] + MFpar
        if Opti.Fmisfit_space == 'obs'     :  MF = MFobs['total'] 
        if Opti.Fmisfit_space == 'par'     :  MF = MFpar


    # --------------
    #  Return class 
    # --------------
    if calc_gradient == False:
        gradMFobs = None
        gradMFpar = None
        Jacobian  = None
    elif calc_gradient == True:
        MF    = None
        MFobs = None
        MFpar = None
        
    class Fmisfit:
        def __init__(self, MF, MFobs, MFpar, gradMFobs, gradMFpar, Jacobian):
            self.MF = MF
            self.MFobs = MFobs
            self.MFpar = MFpar
            self.gradMFobs = gradMFobs
            self.gradMFpar = gradMFpar
            self.Jacobian  = Jacobian    
                                
    Res = Fmisfit(MF, MFobs, MFpar, gradMFobs, gradMFpar, Jacobian)

        
    return Res


# END calcul_fmisfit
# ==============================================================================








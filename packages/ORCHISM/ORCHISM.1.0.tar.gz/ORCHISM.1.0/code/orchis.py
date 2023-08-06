#!/usr/bin/env python
#*******************************************************************************
# MODULE	: ORCHIS
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 06/2010
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
ORCHidee Inversion System Multisite: Main program
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

# if the option "batch" is activated, the files are first copied in the
# scratch directory of the machine where the batch is executed, then
# they are copied in the current directory after execution

import sys,os
path_TOOLS = os.path.join(os.path.dirname(os.readlink(sys.argv[0])),'TOOLS')
sys.path.append(path_TOOLS)
from orchis_config import *
from TOOLS import * 
import numpy as np
import time
import copy
from math import sqrt

# python version
print "PYTHON version:",sys.version_info 

# ==============================================================================
#  MAIN PROGRAM
# ==============================================================================
# Remarque NIVEAUX D'ECRITURE
# 0 : rien
# 1 : suivi OPTIMISATION
# 2 : suivi LAUNCH
# 3 : valeurs intermediaires des parametres optimises


# ==============================================================================
#  OPTIONS & ARGUMENTS
# ==============================================================================

parser = OptionParser()

# --- Definition ---
parser.add_option("--file",dest="file",metavar="FILE",                           # Fichier de definition de l'assimilation
                  help="Name of the file that defines the sole assimilation to perform")

parser.add_option("--exe",dest="exe",metavar="EXE",                              # Nom de l'executable ORCHIDEE
                  help="Name of the ORCHIDEE executable file")

parser.add_option("--exe_tl",dest="exe_tl",metavar="EXE_TL",                     # Activation du mode Tangent Lineaire d'ORCHIDEE
                  help="Name of the Tangent Linear model of ORCHIDEE ")

parser.add_option("-b","--batch",action="store_true",dest="batch",               # Activation du mode d'execution en batch
                  default=False, help="Execution of ORCHIS in batch mode")

parser.add_option("--orch_version",dest="orch_version",metavar="ORCH_VERSION",   # Activation du mode Tangent Lineaire d'ORCHIDEE
                  help="Version of ORCHIDEE_CFG (AR5 by default / CAMELIA ")

(options, args) = parser.parse_args()


# --- Gestion ---

# Only one assimilation run
if options.file != None:
    [file,ext]=os.path.splitext(options.file)
    if len(glob.glob(file+'.py')) ==0 :
        sys.exit('# STOP. The file that define the assimilation characteristics does not exist : \n   ...'+file+'.py')
    file_def_assim = file

# Change the name of the ORCHIDEE exec file
if options.exe != None:
    print "\n\n\n\n\n# The name of the ORCHIDEE exec file as changed from ",
    print Config.exe_orchidee, " to ",
    Config.exe_orchidee = options.exe
    Config.cmde_orchidee = Config.cmde_orchidee.split('/')[0]+'/'+options.exe

    print options.exe


if options.exe_tl != None:

    print "# The Tangent Linear of ORCHIDEE is going to be used : ",

    Config.exe_orchidee_tl = options.exe_tl
    Config.cmde_orchidee_tl = Config.cmde_orchidee_tl.split('/')[0]+'/'+options.exe_tl
    print options.exe_tl


    # if no option_exe defined => same as exe_tl
    if options.exe == None:
        print "# The name of the ORCHIDEE exec file as changed from ",
        print Config.exe_orchidee, " to ",
        Config.exe_orchidee = options.exe_tl
        Config.cmde_orchidee = Config.cmde_orchidee.split('/')[0]+'/'+options.exe_tl
        print options.exe_tl


Config.orch_version = 'AR5'
if options.orch_version != None:
    if options.orch_version in ['AR5', 'CAMELIA']:
        Config.orch_version = options.orch_version
        
print "# The version of ORCHIDEE_CFG being used is :", Config.orch_version
        

# --- Add current path to the search path              ---
# --- in order to import the assimilation config files ---
sys.path.append(Config.PATH_MAIN)                             



# ==============================================================================
#  INITIALIZATION
# ==============================================================================


# ------------------------------------------------------------------------------
# --- Import the assimilation characteristics of the current assimilation run --
# ------------------------------------------------------------------------------
exec('from '+ file_def_assim +' import *')

# --------------------------------------------------------------
# --- Initialize the characteristics for Vars, Data and Opti ---
# --------------------------------------------------------------
#- Initialize all the sites infos according 
#- to the various definitions files
initialize.sites(Site, Paras, Data)

#- Define the various pathes & commands
logfile = initialize.install(Site, options, file_def_assim)

#- Initialize the characteristics for Vars, Data and Opti
initialize.paras(Site, Paras)
initialize.data(Data, Site, logfile) #Site.nannees, Site.npts)
initialize.files(Data)
initialize.opti(Opti)

# - Initialize the defaut BFGS parameters
# default values
if 'BFGS' not in dir(Opti):
    Opti.BFGS = copy.deepcopy(Config.BFGS)
#- user defined values
else:
    Opti.BFGS_user = []
    for key in Config.BFGS.keys():
        if key[0] != '_' and key not in Opti.BFGS:
            exec("Opti.BFGS['"+key+"']=Config.BFGS['"+key+"']")
            Opti.BFGS_user.extend(key)



# -- Write down in which regions the sites are located
# -- (one text file per map)
funcio.write_sites_regions(Config.ORCHIS_OUT_SITES_REGIONS, Site, logfile)


# -- Change the current directory
os.chdir(Config.PATH_MAIN_TMP)


# ==============================================================================
#  GET OBSERVATIONS AND DEFINE PRIOR STATE
# ==============================================================================
             
# ----------------------------------
# --- Get the observed variables ---
# ----------------------------------


Data.obs={}
for isite in range(Site.npts):

    Data.obs[isite] = funcio.get_data(Data.fic[isite]['obs'],
                                      isite,
                                      logfile,
                                      tdaily = [Data.tdaily_d, Data.tdaily_f],
                                      tdaytime = Data.tdaytime,
                                      tnighttime = Data.tnighttime,
                                      ndays = Site.time[isite]['njours'],
                                      nyears = Site.time[isite]['nannees'],
                                      diurnal_length = Data.diurnal[isite]['length'] ,
                                      diurnal_start = Data.diurnal[isite]['start'],
                                      vars_info = Data.vars[isite],
                                      detect_gapf = Data.detect_gapf,
                                      case = 'obs')
    
    print "Lecture obs pour site ",isite," : OK"


# -------------------------------------------------------------
# --- Determine prior values on parameters and observations ---
# -------------------------------------------------------------

# --- prior values on the optimization parameter
[Vars, Vars_site] = prior.detprior_paras(Paras, Site, logfile)

# --- prior values of the fluxes ---
# ----------------------------------
print '# Definition of the a priori fluxes'
logfile.write('# Definition of the a priori fluxes\n')

Data.sim={}
Data.nobs = 0  # Number of observations
Data.nobs_site = {}

for isite in range(Site.npts):

    Data.nobs_site[isite] = 0

    # --- prior ORCHIDEE simulation ---
    print ' '
    print '.....for the site of '+Site.name[isite]+' :'
    logfile.write('.....for the site of :'+Site.name[isite]+' :\n\n')
    os.chdir(Config.PATH_EXEC_SITE[isite])
    orchidee.launch(isite, Vars_site[isite], Site, Data, logfile, check = 2, file_flux_out = Config.ORCHIS_OUT_FLUX_PRIOR_site[isite])
    Data.prior = copy.copy(Data.sim)
    
    # --- Need to normalize obs if necessary ---
    for name in Data.obsname_opti[isite]:
        if 'normalize' in Data.vars[isite][name]['processing_obs']:
            Data.obs[isite][name] = funcio.normalize_data(Data.obs[isite][name], Data.vars[isite],logfile,
                                                          name = name, case = 'obs',
                                                          tempo_res = Data.vars[isite][name]['processing_obs'], 
                                                          indices_obs = Data.vars[isite][name]['indices_obs'],
                                                          indices_sim = Data.vars[isite][name]['indices_sim'])
           
    # --- indices of the observations kept for optimization ---
    prior.indices(Data, isite)

    # --- finalize the processing structure for writting fluxes  ---
    prior.processing(Data, isite)

    # -- Total number of observations --
    for name in Data.obsname_opti[isite]:
        Data.nobs = Data.nobs + np.product(Data.obs[isite][name].shape)
        Data.nobs_site[isite] = Data.nobs_site[isite] + np.product(Data.obs[isite][name].shape)

    print 'Nobs at site '+Site.name[isite]+' = '+str(Data.nobs_site[isite])

    # --- Check the consistency between obs and sims
    for vname in Data.obsname_opti[isite]:
        if Data.sim[isite][vname].shape != Data.obs[isite][vname].shape:
            logfile.write('shape sim : ' + str(Data.sim[isite][vname].shape)+'\n')
            logfile.write('shape obs : ' + str(Data.obs[isite][vname].shape)+'\n')
            sys.exit('# STOP. ORCHIS : the shape of the OBS and SIM do not match')
            #raw_input('# STOP. ORCHIS : the shape of the OBS and SIM do not match for '+vname)


    # --- Partitioning between nighttime & daytime measurements ---
    # Note: no need if assimilating daily data    
    # ## if Data.test_flux == True and Data.correct_error_night == True and Data.tempo_res != 'daily' :
    print '# Correction of nighttime measurements'
    logfile.write('# Correction of nighttime measurements \n')
    prior.det_nightandday(Data, Site, isite, logfile)
        
        
    # --- Determine the RMSE between prior simulations and data ---
    print
    print '# RMSE between measurements and prior ORCHIDEE simulations:'
    logfile.write('\n# RMSE between measurements and prior ORCHIDEE simulations:\n')
    funcio_site.write_rmse_data(isite,Config.ORCHIS_OUT_RMSE_PRIOR_site[isite], Data, logfile)

    # --- Save observations that are actually optimized ---
    print '# Write observations & prior simulations for this site in ',Config.ORCHIS_OUT_OPTI_OBSNSIM_site[isite]
    logfile.write('# Write observations & prior simulations for this site in '+Config.ORCHIS_OUT_OPTI_OBSNSIM_site[isite]+'\n')

    # Observations for each site
    funcio_site.write_fluxes(isite, Config.ORCHIS_OUT_OPTI_OBSNSIM_site[isite], Data, Site, datacase = 'obs', mode = 'w')
    # Prior simulations for each site
    funcio_site.write_fluxes(isite, Config.ORCHIS_OUT_OPTI_OBSNSIM_site[isite], Data, Site, datacase = 'sim_prior', mode = 'a')

print "Nobs = ",Data.nobs

# --- Write variables for all the sites in a single file ---
print '# Write observations & prior simulations, gathered for all the sites in',Config.ORCHIS_OUT_OPTI_OBSNSIM
logfile.write('# Write observations & prior simulations, gathered for all the sites in '+Config.ORCHIS_OUT_OPTI_OBSNSIM+'\n')
# Observations
funcio.write_fluxes(Config.ORCHIS_OUT_OPTI_OBSNSIM, Data, Site, datacase = 'obs', mode = 'w')
# Prior simulations
funcio.write_fluxes(Config.ORCHIS_OUT_OPTI_OBSNSIM, Data, Site, datacase = 'sim_prior', mode = 'a')



# --------------------------------------------------------
# --- Stop here if the test on RMSE prior is activated ---
# --------------------------------------------------------
if Data.test_rmse_prior == True:

    print
        
    # - write some info first

    for isite in range(Site.npts):

        print '*** Site : '+Site.name[isite] +' ***'
        logfile.write('\n\n  +++ '+Site.name[isite] +' +++\n')
        for vname in Data.obsname_opti[isite]:
            
            print ' + '+vname+' : '
            logfile.write(' + '+vname+' +++\n')
        
            if 'daily' in Data.vars[isite][vname]['processing_sim']:
                print '   - Assimilation of DAILY data accounting for measurements between ',[Data.tdaily_d,Data.tdaily_f]
                logfile.write('\n\  - Assimilation of DAILY data accounting for measurements between '+str([Data.tdaily_d,Data.tdaily_f])+'\n')
                
                if 'smooth' in Data.vars[isite][vname]['processing_sim']:
                    print '   - SMOOTHING of daily data activated'
                    logfile.write('\n\  - SMOOTHING of daily data activated')
                    
                    
            if 'diurnal' in Data.vars[isite][vname]['processing_sim']:
                print '   - Assimilation of DIURNAL data '
                logfile.write('\n\  - Assimilation of DIURNAL data')
            

            if 'day_vs_night' in Data.vars[isite][vname]['processing_sim']:
                print '   - Separation of daytime and nighttime data '
                logfile.write('\n\  - Separation of daytime and nighttime data ')

        
        
    # - if batch mode : copy the results
    if options.batch == True:
        io.batch_cp(Site,logfile)
        
    sys.exit()



# --- Change the current directory ---
os.chdir(Config.PATH_MAIN_TMP)

    
# -----------------------------------------------
# --- Determine the error covariance matrices ---
# -----------------------------------------------
    
# background error covariance matrix on parameters  
prior.detmatcov_paras(Site, Vars, logfile)

# observation error covariance matrix
prior.detmatcov_obs(Site, Data, logfile, init = True, modif_sigma = True, detect_gapf = Data.detect_gapf)          

# ==============================================================================================
# SCAN THE VALUE OF THE MISFIT FUNCTION AROUND XPRIOR
# ==============================================================================================
# |


# A mettre a jour


## if Opti.scan_fmisfit_prior == True:       
##     # - call scan_fmisfit
##     optimisation.scan_fmisfit(Vars, Site, Data, Opti, logfile, filename = Config.ORCHIS_OUT_SCAN_FMISFIT_PRIOR)
##     # - Sortie
##     logfile.write('End of scanning Fmisfit')
##     sys.exit('End of scanning Fmisfit')
# |
# ==============================================================================================



# # ==============================================================================================
# # COMPUTE THE GRADIENT OF THE MISFIT FUNCTION AS A FUNCTION OF EPS FOR EACH PARAMETER
# # ==============================================================================================
# # |


# # A mettre a jour


# if Paras.test_gradMF_vs_eps == True:       
    
#     # - need some initialization for history data
#     optimisation.initopti(Vars, Site, Opti, nobs = Data.nobs, dataname = Data.obsname_opti, cas = 'init', test_gradMF_vs_eps = True)
#     optimisation.transfovar(Vars, Opti, mode = 'forward')
#     # - get the Opti.x['all'] structure required by BFGS
#     optimisation.initopti(Vars, Site, Opti, dataname = Data.obsname_opti, cas = 'all')
#     # - call the routine that compute the variation of the misfit function gradient as a function of eps, for
#     #   each parameter at a time
#     check_opti.gradfmisfit_vs_eps(Vars, Vars_site, Site, Data, Opti, Paras.eps_val, logfile, check = 2)
    
#     # - Write the output file
#     funcio.write_gradMF_vs_eps(Config.ORCHIS_OUT_GRADMF_VS_EPS,
#                                Opti,
#                                Site,
#                                Data,
#                                var_name = Vars.vars['opti_varname'],
#                                eps_val = Paras.eps_val)
    
#     # - Sortie
#     logfile.write('End of Gradient Fmisfit = f(eps)')
#     sys.exit('End of Gradient Fmisfit = f(eps)')
# # |
# # ==============================================================================================



    
# ==============================================================================================
# OPTIMIZATION
# ==============================================================================================


# - Actual number of iterations
Opti.nloop = 0

# - Convergence test on the inverse solution is not activated 
test_convergence = False



# ----------------------------
# --- Some initializations ---
# ----------------------------

# - structure containing all info to pass to the optimization algorithm
optimisation.initopti(Vars, Site, Opti, nobs = Data.nobs, dataname = Data.obsname_opti, cas = 'init')

# - forward transformation of the variables
optimisation.transfovar(Vars, Opti, mode = 'forward')


# -----------------------------------------------------------
# --- Write some information at the end of initialization ---
# -----------------------------------------------------------
ficinfo = Config.PATH_MAIN_EXEC+'/opti_info.txt'

initialize.info(Site,Vars, Data, Opti, logfile, ficinfo)

# # ------------------------
# # --- Sensitivity test ---
# # ------------------------

# # To be updated
# if Opti.test_sensitivity_Fmisfit_prior == True:
        
#     print 
#     print '# Test the sensitivity of the misfit function around the prior values:'
#     logfile.write('\n# Test the sensitivity of the misfit function around the prior values: \n')
    
#     test_convergence = True

#     # - get the Opti.x['all'] structure required by BFGS
#     optimisation.initopti(Vars, Site, Opti, dataname = Data.obsname_opti, cas = 'all')
#     # - Compute
#     optimisation.main(Vars, Vars_site, Site, Data, Opti, Config, test_convergence, logfile, check = 2)
    
#     # - Write results
#     funcio.write_sensiMF(Config.ORCHIS_OUT_SENSI_MF_PRIOR, Vars, Data, Opti)



       
# ------------------
# --- Iterations ---
# ------------------
if Opti.nloop_max == 0: sys.exit()

while Opti.nloop < Opti.nloop_max and test_convergence == False:

        
    print '\n\n============================================================'
    print '==============         iteration no '+str(Opti.nloop) + '         ==============\n'
    print
    logfile.write('\n\n\n\n============================================================\n')
    logfile.write('==============         iteration no '+str(Opti.nloop) + '         ==============\n')

    
    # -----------------------------------------------------------
    # ---            Optimization algorithms                  ---

    # - get the Opti.x['all'] structure required by BFGS

    print 'INITOPTI IN '
    optimisation.initopti(Vars, Site, Opti, dataname = Data.obsname_opti, cas = 'all')

    # === BFGS method ===
    if Opti.method == 'bfgs':

        # - Computation of the misfit function and its gradient
        if Opti.BFGS['task'][0:2] == 'FG':            
            print '\n# Computation of MF and its gradient'
            logfile.write('\n# Computation of MF and its gradient\n\n')

            optimisation.main(Vars, Vars_site, Site, Data, Opti, test_convergence, logfile, check = None)
            
            # Ajout SK 
            ##########################################################################
            ## At first iteration, calculate the Rprior matrix
            ## by propagating the prior error on parameters
        
            if Opti.nloop == 0 and Opti.propagate_Bprior == True:
                Data.Jacobian_prior = copy.deepcopy(Data.Jacobian)
                #prior.propagate_Bprior(Vars, Data, Opti, logfile)
            
            ##########################################################################

            Opti.nloop+=1
            
        # - Initialize BFGS #2
        if Opti.nloop == 0:  initialize.bfgs(Opti)

        # - Create the BFGS input NetCDF file
        bfgs.write_bfgs_in(Opti, logfile)
        bfgs.write_infos(Opti, logfile, case = 'input')
            
        # - Call BGFS                                                
        fic_in = "'"+Opti.BFGS['input']+"'"
        fic_out = "'"+Opti.BFGS['output']+"'"       
        os.system(Config.cmde_bfgs + ' '+ fic_in +' '+fic_out) # + ' > bfgs.log'+str(Opti.nloop))
        
        # -  Read BFGS outputs and modify the value of the optimization parameters
        bfgs.read_bfgs_out(Vars.vars['opti_varname'],Opti,logfile)
        bfgs.write_infos(Opti, logfile, case = 'output')                    

        # - Inverse transformation of the variables 
        optimisation.transfovar(Vars, Opti, mode = 'reverse')
        print 'INITOPTI OUT'

        optimisation.initopti(Vars, Site, Opti, cas = 'all') # optionnel


        # - Allocate the modified parameter values to Vars...
	for name in Vars.vars['opti_varname'] :            

            # 1. if PFT and region dependent, or Site and PFT
            if len(Vars.vars[name]['dim_name']) == 3:
                # reshape Vars
                i=0
                for ireg in Vars.vars[name]['3rd_loop']:
                    max = len(Vars.vars[name]['value'][ireg])
                    Vars.vars[name]['value'][ireg]=Opti.x[name][i:i+max]
                    i=i+max

            # 2. all other cases :
            else:
                Vars.vars[name]['value'] = np.reshape(Opti.x[name],(Vars.vars[name]['value']).shape )
                    
	    
            # ...and Vars_site
            for isite in range(Site.npts):
                Vars_site[isite].vars[name]['value'] = copy.copy(various.vars_to_site(isite, name, Vars, Site))


##################################################################################################################################


        # - Stopping criteria 
        if Opti.BFGS['task'][0:4] == 'CONV':  test_convergence = True
        if Opti.BFGS['task'][0:4] == 'ABNO':  test_convergence = True
        if Opti.BFGS['task'][0:5] == 'ERROR': test_convergence = True

            
    # === end BFGS ===

        # === Iterative Tarantola Approach ===

##     if Opti.method == 'iter_tarantola':

##         # - Computation of the misfit function and its gradient
##         print '\n# Computation of MF and its gradient'
##         logfile.write('\n# Computation of MF and its gradient\n\n')
##         optimisation.main(Vars, Vars_site, Site, Data, Opti, test_convergence, logfile, check = 2)
##         Opti.nloop+=1
        
##         # - Call the Tarantola routine
##         tarantola.detpost_paras(Data,
##                                 Opti,
##                                 file_matcov_out = Config.ORCHIS_OUT_ERPOST_MATCOVVAR,
##                                 file_matcor_out = Config.ORCHIS_OUT_ERPOST_MATCORVAR,
##                                 case = 'Opti_iter',
##                                 opti_varname = Vars.vars['opti_varname'])
        
##         # - Inverse transformation of the variables 
##         optimisation.initopti(Vars, Site, Opti, cas = 'all') # optionnel

##         ##print 'Opti.xT :',Opti.xT['Vcmax_opt'],Opti.xT['LAI_MAX'],Opti.xT['Q10']
##         ##print 'Opti.xT[all]',Opti.xT['all']
##         ##print 'Opti.x[all]',Opti.x['all']
        
##         # - Informations
##         print ' # Values of the optimized parameter set :'
##         print Opti.x['all']
##         print
##         logfile.write(' # Values of the optimized parameter set \n'+str(Opti.x['all'])+'\n\n')

        
##         # - Allocate the modified parameter values to Vars
##         for name in Vars.vars['opti_varname']:
##             Vars.vars[name]['value'] = np.reshape(Opti.x[name],(Vars.vars[name]['value']).shape )

    # === end Iterative Tarantola Approach ===
    # -----------------------------------------------------------

        
    # ---------------------------------------------------
    # --- Correction of the observation uncertainties ---
    if Opti.scan_fmisfit_prior == False \
       and test_convergence == False:
        optimisation.adjust_test(Site, Data, Opti, Vars, logfile)                           
    # ---------------------------------------------------


        
    # ----------------------------------------------------------
    # --- Continue assimilation if Opti.MF(i) > Opti.MF(i-1) ---
    if Opti.nloop == Opti.nloop_max:
        
        if len(Opti.hist_MF) >= 2:               
            ###if Opti.hist_MF[-1] > Opti.hist_MF[-2]:
            if Opti.hist_MF[-1]/Opti.hist_MF[-2] > 1+1e-5:
                Opti.nloop_max = Opti.nloop_max+1
                print '\n\n Opti.MF(i) > Opti.MF(i-1) => increase Opti.nloop_max (->'+str(Opti.nloop_max)+')'
                print '\n   ratio = '+str(Opti.hist_MF[-1]/Opti.hist_MF[-2])+')'
                logfile.write('\n\n Opti.MF(i) > Opti.MF(i-1) => increase Opti.nloop_max (->'+str(Opti.nloop_max)+')\n')
                logfile.write('     ratio = '+str(Opti.hist_MF[-1]/Opti.hist_MF[-2])+'\n')
    # ----------------------------------------------------------
        

    # -------------------------------------------------------
    # --- Save the optimisation results at each iteration ---
    if Opti.nloop > 0:
        funcio.write_optires(Config.ORCHIS_OUT_OPTI_RES,
                             Site,
                             Opti,
                             Vars,
                             Data,
                             test_convergence = test_convergence)

        for isite in range(Site.npts):
            funcio_site.write_optires(isite,
                                      Config.ORCHIS_OUT_OPTI_RES_site[isite],
                                      Site,
                                      Opti,
                                      Vars,
                                      Vars_site[isite],
                                      Data,
                                      Site.indice_pft[isite],
                                      test_convergence = test_convergence)
            
    print '============================================================='
    logfile.write('=============================================================\n')


        
    # -------------------------------------------------------
    
    ###DEBUG
    ###funcio.write_optires(Config.ORCHIS_OUT_OPTI_RES, Opti, Data, Site.indice_pft, test_convergence = test_convergence)
    ###sys.exit()
    
        
        
# === End iteration loop ===


print
if Opti.method == 'bfgs':
    
    print '# End of optimization with the message: ' + Opti.BFGS['task']
    logfile.write('\n# End of optimization with the message: ' + Opti.BFGS['task'] + '\n')
    
    # - Need to reallocate properly the values of the optimized parameters in
    # - the history variables and to recompute the Jacobian of the model
    
    Opti.nloop+=1

    optimisation.main(Vars, Vars_site, Site, Data, Opti, False, logfile, check = 2)
    optimisation.transfovar(Vars, Opti, mode = 'reverse')
    optimisation.initopti(Vars, Site, Opti, cas = 'all') # optionnel
    
else:
    print '# End of optimization' 
    logfile.write('\n# End of optimization \n')

    
for name in Vars.vars['opti_varname']:
    for isite in range(Site.npts):
        Vars_site[isite].vars[name]['value'] = various.vars_to_site(isite, name, Vars, Site)
        

# ---------------------------------------------------------
# --- Determine the posterior uncertainty on parameters ---
# ---------------------------------------------------------

# Based on the FORTRAN tool TARANTOLA_REF (Peylin & Carouge)
print
print '# Determination of the posterior uncertainty on parameters (TARANTOLA_REF):'
logfile.write('\n# Determination of the posterior uncertainty on parameters (TARANTOLA_REF): \n')

# --- Change the current directory ---
os.chdir(Config.PATH_MAIN_TMP)

test_tarantola = tarantola.detpost_paras(Data,
                                         Site,
                                         Opti,
                                         logfile,
                                         file_matcov_out = Config.ORCHIS_OUT_ERPOST_MATCOVVAR,
                                         file_matcor_out = Config.ORCHIS_OUT_ERPOST_MATCORVAR,
                                         case = 'Bpost')


# -----------------------------------------------------------
# --- Determine the posterior uncertainty on observations ---
# -----------------------------------------------------------
if Opti.calculate_Rpost == True:
    tarantola.detpost_Robs(Data, Opti, logfile, test_tarantola)

# ----------------------
# --- Save Results   ---
# ----------------------
print
print '# Saving the results in '+Config.PATH_MAIN_EXEC
logfile.write('\n# Saving the results in '+Config.PATH_MAIN_EXEC+'\n')

# - ORCHIDEE parameters (default & optimized)
print '  + optimized parameters'
logfile.write('  + optimized parameters\n')

for isite in range(Site.npts):
    funcio_site.write_paras(Config.ORCHIS_OUT_OPTI_VAR_site[isite], Vars_site[isite])

funcio.write_paras(Config.ORCHIS_OUT_OPTI_VAR, Site, Vars, Opti)

# - Optimization variables
print '  + optimization results'
logfile.write('  + optimization results\n')
funcio.write_optires(Config.ORCHIS_OUT_OPTI_RES,
                     Site,
                     Opti,
                     Vars,
                     Data,
                     test_convergence = True)

for isite in range(Site.npts):
    funcio_site.write_optires(isite,
                              Config.ORCHIS_OUT_OPTI_RES_site[isite],
                              Site,
                              Opti,
                              Vars,
                              Vars_site[isite],
                              Data,
                              Site.indice_pft[isite],
                              test_convergence = True)
    

# - Optimized fluxes
print '  + optimized fluxes'
logfile.write('  + optimized fluxes\n')

for isite in range(Site.npts):
    os.chdir(Config.PATH_EXEC_SITE[isite])
    orchidee.launch(isite,
                    Vars_site[isite],
                    Site,
                    Data,
                    logfile,
                    file_flux_out = Config.ORCHIS_OUT_FLUX_POSTERIOR_site[isite])

# - posterior simulations
funcio.write_fluxes(Config.ORCHIS_OUT_OPTI_OBSNSIM,
                    Data,
                    Site,
                    datacase = 'sim_post',
                    mode = 'a')


for isite in range(Site.npts):
    funcio_site.write_fluxes(isite,
                             Config.ORCHIS_OUT_OPTI_OBSNSIM_site[isite],
                             Data,
                             Site,
                             datacase = 'sim_post',
                             mode = 'a')
    
# -----------------------------------------------------------------
# --- Determine the RMSE between posterior simulations and data ---
# -----------------------------------------------------------------
print
print '# RMSE between measurements and posterior ORCHIDEE simulations:'
logfile.write('\n# RMSE between measurements and posterior ORCHIDEE simulations: \n')
for isite in range(Site.npts):

    print
    print Site.name[isite]
    logfile.write('\n'+Site.name[isite]+'\n')

    funcio_site.write_rmse_data(isite,
                                Config.ORCHIS_OUT_RMSE_POSTERIOR_site[isite],
                                Data,
                                logfile)
    
# ==============================================================================================
#  SENSITIVITY TEST 
# ==============================================================================================

if Opti.test_sensitivity_Fmisfit_post == True:
    
    print 
    print '# Test the sensitivity of the misfit function around the minimum:'
    logfile.write('\n# Test the sensitivity of the misfit function around the minimum: \n')
    
    # - Compute
    optimisation.main(Vars, Site, Data, Opti, True, logfile, check = 2)
    
    # - Write results
    funcio.write_sensiMF(Config.ORCHIS_OUT_SENSI_MF_POST, Vars, Data, Opti)



# ==============================================================================================
#  SCAN THE MISFIT FUNCTION AROUND THE MINIMUM 
# ==============================================================================================
if Opti.scan_fmisfit_post == True:
    print
    Opti.scan_local = True
    # - call scan_fmisfit
    check_opti.scan_fmisfit(Vars,
                            Site,
                            Data,
                            Opti,
                            logfile,
                            filename = Config.ORCHIS_OUT_SCAN_FMISFIT_POST)
    # - Sortie
    logfile.write('# End of scanning Fmisfit')
    sys.exit('# End of scanning Fmisfit')
    


# ==============================================================================================
#  IF BATCH MODE ACTIVATED : COPY THE RESULTS 
# ==============================================================================================

if options.batch == True:
    io.batch_cp(Site,logfile)
        

# -------------------------
# --- Close the logfile ---
# -------------------------
logfile.close()


# --------------------------------------
# --- Get back to the main directory ---
# --------------------------------------
os.chdir(Config.PATH_MAIN)



# ==============================================================================================

# END PROGRAM MAIN

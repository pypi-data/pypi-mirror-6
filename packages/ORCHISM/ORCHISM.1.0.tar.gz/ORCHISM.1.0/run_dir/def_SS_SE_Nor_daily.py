#*******************************************************************************
# CONFIGURATION FILE
#
# SITE : Test Hesse
#
# 08/2010
#*******************************************************************************

import numpy as np

# ==============================================================================
#  Site characteristics 
#
# ------------------------------------------------------------------------------
class Site:

    main_path = '/your/working/directory/ORCHISM/'

    # -- Max number of region sets
    nmaps = 3

    # -- Path to region definitions files
    path_maps = main_path+'inputs/maps/'

    # -- Path to configuration files
    path_config = main_path+'inputs/config/daily/'

    # -- Path to site list
    fic_site = main_path+'inputs/sites_list.txt'

    # -- Sites
    site_names = ['SE-Nor']
    
    site = {}
    for elem in site_names: site[elem] = {}

    # -- Name of the output directory for the current assimilations
    #    if no name is provided, the default path will be:
    #    + null if the chaining file contains only one file to treat
    #    + a string containing the local date
    PATH_EXEC = 'SS_SE-Nor_daily'   

    
# END Site
# ==============================================================================    

# ==============================================================================
# Define the measurements on which assimilation is performed as well as
# the error structures on the observations
#------------------------------------------------------------------------
class Data:  

    #main_path = '/home/satellites7/skuppel/carbones_test/'
    
    # -- Files of data definition for each site
    
    path_defsite = Site.main_path+'inputs/defsites/daily/'

    case = [elem.split('-')[0]+'_'+elem.split('-')[1] for elem in Site.site_names]
  
    [tdaily_d,tdaily_f] = [0,24]
     
    # Take in into account gapfilling as an additional source of uncertainty
    detect_gapf = True
    coef_gapf = 0.5   
   
    # Calculate RMSE prior / obs, then stop
    test_rmse_prior = False

    # -- If = True, we use the RMSE of prior simulation to set the a priori error on observations for R
    auto_sigma_obs = True

    # -- Correction coefficient between rmse_prior and sigma_obs (if auto_sigma_obs = True)
    corr_sigma_obs={}
    corr_sigma_obs['NEEt'] = 1.
    corr_sigma_obs['Qle'] = 1.

    # END Data
# ==============================================================================



# ==============================================================================
# Parameters that are optimized
#
# If no a priori values are provided for a parameter, they will be infered from
# ORCHIDEE default values
# ------------------------------------------------------------------------------
class Paras:
       
    # -- Parameters to optimize: dimensions
    vars = {}

    # indice_region :
    # if = 0 : no region dependency
    # if > 0 : region-dependent, based on the map number (-1 because indexes start at 0...) given by the value of indice_region
    
    vars['Vcmax_opt']          = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #PFT
    vars['Gsslope']            = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Tphoto_opt_c']       = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Tphoto_min_c']       = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Tphoto_max_c']       = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }

    # ---------------------------------------
    #vars['Kpheno_crit']        = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #PFT
    #vars['Senescence_temp_c']  = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #PFT
    vars['LAI_MAX']            = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #PFT
    vars['SLA']                = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Leafagecrit']        = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Klaihappy']          = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['Tau_leafinit']       = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['Thetaleaf']          = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['Clumping']           = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['LAI_init']           = {'dims' : {'indice_pft':1, 'points_terre':1, 'indice_region': 0, 'variation_temp': 'variation_fix'} }

    # ---------------------------------------
    vars['Q10']                = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #(--> geo)
    vars['KsoilC']             = {'dims' : {'indice_pft':0, 'points_terre':1, 'indice_region': 0, 'variation_temp': 'variation_fix'}} #site
    vars['Maint_resp_c']       = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Maint_resp_slope_c'] = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Frac_growthresp']    = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }

    # ---------------------------------------
    #vars['Humcste']            = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['Dpu_cste']           = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #(--> geo)

    # ---------------------------------------
    vars['Fstressh']           = {'dims' : {'indice_pft':1, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'}} #

    # ---------------------------------------
    #vars['Moistcont_a']        = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Moistcont_b']        = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Moistcont_c']        = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['Moistcont_min']      = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }

    # ---------------------------------------
    #vars['Hcrit_litter']       = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    vars['Z_decomp']           = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }

    # ---------------------------------------
    vars['Kalbedo_veg']        = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['Z0_over_height']     = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['So_capa_dry']        = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }
    #vars['So_capa_wet']        = {'dims' : {'indice_pft':0, 'points_terre':0, 'indice_region': 3, 'variation_temp': 'variation_fix'} }

    
    for vname in vars.keys(): vars[vname]['transform'] = 'linear'
    #for vname in vars.keys(): vars[vname]['deriv'] = 'tl'
    ##'finite_differences'
    for vname in vars.keys(): vars[vname]['deriv'] = 'finite_differences'
    #vars['Kpheno_crit']['deriv'] = 'finite_differences'
    #vars['Senescence_temp_c']['deriv'] = 'finite_differences'
    #vars['LAI_MAX']['deriv'] = 'finite_differences'
    #vars['LAI_MAX']['eps'] = 1.e-2

    #vars['Kpheno_crit']['eps'] = 0.06

    #sigma_pc = 40.
    
# END Paras
# ==============================================================================    



# ==============================================================================
#  Optimization characteristics
#
# ------------------------------------------------------------------------------
class Opti:


    # -- Maximum number of iteration loops for the optimization algorithm
    nloop_max = 15

    # -- Propagate Bprior in observation space
    propagate_Bprior = True

# END Opti
# ==============================================================================    

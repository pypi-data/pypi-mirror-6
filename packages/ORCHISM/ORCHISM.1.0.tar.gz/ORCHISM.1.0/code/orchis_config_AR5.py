#!/usr/bin/env python
#*******************************************************************************
# MODULE	: ORCHIS_CONFIG_AR5
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 07/2007
# LAST MODIF    : 10/2012
# COMPILER	: PYTHON
# 
"""
Default configuration parameters for the assimilation system of ORCHIDEE
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

# ==============================================================================================
class Config:
# ==============================================================================================
    import os
    import sys
    
    # ==============================================================================
    #  Default values of some input/output files and directories
    # ------------------------------------------------------------------------------

    # --- Path of the default ORCHIDEE configuration
    pathCONFIG = '/home/satellites2/skuppel/carbones_test/inputs/config/'
    
    # --- Site definition : ASCII file defining site characteristics
    fic_site_def = '/home/data02/cbacour/ORCHIDEE/config/site_def.txt'
    
    
    # --- Forcing file (used mainly to get the default 
    FORCING_FILE = '/your/working/directory/ORCHISM/inputs/forcing/dummy_forcing.nc'
    # --- Execution directory
    PATH_MAIN = os.getcwd()
       
    
    # --- Level of output info
    check = 1

    # --- default name for the ORCHIS output files
    
    # template name for the output file(s) containing the region index for each site
    ORCHIS_OUT_SITES_REGIONS = 'opti_sites_regions_.txt'
    # name of the output file containing all optimization results 
    ORCHIS_OUT_OPTI_RES = 'opti_res.nc'
    # name of the output file containing the optimized parameters
    ORCHIS_OUT_OPTI_VAR = 'opti_vars.nc'
    # name of the output file containing ORCHIDEE simulations performed with the prior values on the parameters
    ORCHIS_OUT_FLUX_PRIOR = 'opti_flux_prior.nc'
    # name of the output file containing the optimized fluxes
    ORCHIS_OUT_FLUX_POSTERIOR = 'opti_flux_posterior.nc'
    # name of the output file containing the observations & simulations actually optimized
    ORCHIS_OUT_OPTI_OBSNSIM = 'opti_obsnsim.nc'
    # name of the output file containing values of the RMSE between  measurements and PRIOR simulations
    ORCHIS_OUT_RMSE_PRIOR = 'opti_rmse_prior.txt'
    # name of the output file containing values of the RMSE between measurements and POSTERIOR simulations
    ORCHIS_OUT_RMSE_POSTERIOR = 'opti_rmse_posterior.txt'
    # name of the output file containing the results on the scanning of Fmisfit around the prior simulations
    ORCHIS_OUT_SCAN_FMISFIT_PRIOR = 'opti_scan_fmisfit_prior.nc'
    # name of the output file containing the results on the scanning of Fmisfit around the posterior simulations
    ORCHIS_OUT_SCAN_FMISFIT_POST  = 'opti_scan_fmisfit_post.nc'
    # name of the output file containing the results on the sensitivity of MF around the minimum
    ORCHIS_OUT_SENSI_MF_PRIOR = 'opti_sensi_fmisfit_prior.txt'
    # name of the output file containing the results on the sensitivity of MF around the minimum
    ORCHIS_OUT_SENSI_MF_POST = 'opti_sensi_fmisfit_post.txt'
    # name of the output file containing the posterior covariance matrix on the parameters
    ORCHIS_OUT_ERPOST_MATCOVVAR = 'opti_erpost_matcovvar.txt'
    # name of the output file containing the posterior correlation matrix on the parameters
    ORCHIS_OUT_ERPOST_MATCORVAR = 'opti_erpost_matcorvar.txt'
    # name of the output file containing the results on the posterior uncertainties on the variables
    ORCHIS_OUT_ERPOST_VAR = 'opti_erpost_var.nc'
    # name of the output file containing the sensitivity of the misfit function gradient to variations of eps
    ORCHIS_OUT_GRADMF_VS_EPS = 'opti_gradmf_vs_eps.txt'

    fic_out = ['ORCHIS_OUT_SITES_REGIONS','ORCHIS_OUT_OPTI_RES','ORCHIS_OUT_OPTI_VAR',\
               'ORCHIS_OUT_FLUX_PRIOR','ORCHIS_OUT_FLUX_POSTERIOR', 'ORCHIS_OUT_OPTI_OBSNSIM',\
               'ORCHIS_OUT_RMSE_PRIOR', 'ORCHIS_OUT_RMSE_POSTERIOR', 'ORCHIS_OUT_SENSI_MF_PRIOR', 'ORCHIS_OUT_SENSI_MF_POST',\
               'ORCHIS_OUT_SCAN_FMISFIT_PRIOR', 'ORCHIS_OUT_SCAN_FMISFIT_POST', \
               'ORCHIS_OUT_ERPOST_MATCOVVAR','ORCHIS_OUT_ERPOST_MATCORVAR','ORCHIS_OUT_ERPOST_VAR','ORCHIS_OUT_GRADMF_VS_EPS']

    # --- Missing value
    missval = [-9999.,1e20]
    
    
    # ---  Smoothing filters
    # Gaussian filter characteristics for fAPAR
    smooth_gauss_filter =  [2.4935221e-001,  2.8551171e-001,  3.2465247e-001,  3.6660430e-001,  4.1111229e-001,
                           4.5783336e-001,  5.0633562e-001,  5.5610088e-001,  6.0653066e-001,  6.5695557e-001,
                           7.0664828e-001,  7.5483960e-001,  8.0073740e-001,  8.4354765e-001,  8.8249690e-001,
                           9.1685536e-001,  9.4595947e-001,  9.6923323e-001,  9.8620712e-001,  9.9653380e-001,
                           1.0000000e+000,
                           9.9653380e-001,  9.8620712e-001,  9.6923323e-001,  9.4595947e-001,  9.1685536e-001,
                           8.8249690e-001,  8.4354765e-001,  8.0073740e-001,  7.5483960e-001,  7.0664828e-001,
                           6.5695557e-001,  6.0653066e-001,  5.5610088e-001,  5.0633562e-001,  4.5783336e-001,
                           4.1111229e-001,  3.6660430e-001,  3.2465247e-001,  2.8551171e-001,  2.4935221e-001]

    # Square filter for daily_fluxes
    smooth_len_square_filter = 15 

    # --- Name of ORCHIS logfile
    orchis_logfile = 'orchis.log'

    # ==============================================================================




    # ==============================================================================
    #  ORCHIDEE, BFGS, TARANTOLA, command line
    # ------------------------------------------------------------------------------
    # --- On which machine is ORCHIDEE running ? ---
    import socket 
    machine = socket.gethostname()
    
    if machine[0:7] == 'asterix':
        sys.exit('# STOP. ORCHIS and ORCHIDEE are not designed to work on a 32bits architecture')
    
    if machine[0:6] == 'obelix':
        #if int(machine[6]) !=3 :
        exe_orchidee    = 'orchidee_ol'
        exe_orchidee_tl = 'orchidee_tl'
        exe_bfgs        = 'orchidee_bfgs'
        exe_tarantola   = 'tarantola'
    else :
        sys.exit('# Unknown host. STOP')

    #exe_orchidee = PATH_EXEC + exe_orchidee
    
    # --- Environment variables ---
    # os.system uses /bin/sh
    #  - for bash/sh/ksh: ulimit -s unlimited
    #  - for csh: limit stacksize unlimited
    cdumpsize = 'ulimit -c 33000'      #'limit coredumpsize 33000'
    stacksize = 'ulimit -s unlimited ' #'limit stacksize unlimited'
    
    cmde_orchidee = '; '.join([cdumpsize,stacksize, './'+exe_orchidee])
    cmde_orchidee_tl  = '; '.join([cdumpsize,stacksize, './'+exe_orchidee_tl])
    cmde_bfgs = '; '.join([cdumpsize,stacksize, './'+exe_bfgs])
    cmde_tarantola = '; '.join([cdumpsize,stacksize, './'+exe_tarantola])

    # --- Determine if the machine is LITTLE or BIG ENDIAN ---
    endian = sys.byteorder # 'little' or 'big'


    # --- template for ORCHIDEE output files
    orch_flux_out = 'flux_out.nc'
    orch_sech_out = 'sech_out.nc'
    orch_sech_out2 = None #'sech_out2.nc'
    orch_stom_out = 'stom_out.nc'
    
    # ==============================================================================
    
    

    # ==============================================================================
    # Definition of the month periods for computation of diurnal cycles
    # ------------------------------------------------------------------------------
    month_name = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    month_length = [31,28,31,30,31,30,31,31,30,31,30,31]


    # ==============================================================================
    #  Default values of some BFGS parameters
    # ------------------------------------------------------------------------------
    BFGS = {}

    BFGS['m'] = 17         # Number of corrections in the memory matrix
    
    BFGS['factr'] = 1.e7   # Tolerance in the termination test (suppress test with factr=0)
                           #  1.e12 for low accuracy; 1.e7 for moderate accuracy; 1.e1 for extremely high accuracy
    BFGS['pgtol'] =    0   # Tolerance in the termination test (suppress test with pgtol=0)

    BFGS['iprint'] = -1    # Control the frequency and type of outputs
    BFGS['task'] = 'START'
    BFGS['csave'] = ''
        
    BFGS['size_isave'] = 44
    BFGS['size_dsave'] = 29
    BFGS['size_lsave'] = 4

    #- Stoppping criterion based on the norm of gradMF
    #   stop when the MEAnp.of the DIFFERENCE of 2 successive estimations
    #   of the norm of gradMF is below a defined THRESHOLD, accounting
    #   for X last estimations of norm(gradMF) in a defined window
    ###BFGS['window_normgradMF'] = 10       # length of the history used to determine the end of BFGS
    ###BFGS['threshold_normgradMF'] = 0.001 # threshold
    
    # Input and output files
    BFGS['input'] = 'bfgs_in.nc'
    BFGS['output'] = 'bfgs_out.nc'
       
    # ==============================================================================
    

    # ==============================================================================
    #  Default values of some TARANTOLA routine
    # ------------------------------------------------------------------------------
    TARANTOLA = {}

    #-- Files
    # Name of the input text file
    TARANTOLA['input_file_dat'] = 'tarant_in.dat'
    # Name of the input binary file
    TARANTOLA['input_file_bin'] = 'tarant_in.bin'
    # Name of the output binary file
    TARANTOLA['output_file_bin'] = 'tarant_out.bin' 
    # Name of the temporary binary file
    TARANTOLA['tempo_file_bin'] = 'tarant_tmp.bin'

    # Name of the log file
    TARANTOLA['log_file'] = 'tarant.log'
        

# ==============================================================================================



# ==============================================================================================
class Paras_def:
#  Parameters characteristics
# ==============================================================================================

    # ---  Name of the optimizable parameters in order
    parnames_template = [
        'Vcmax_opt', 'Fstressh', 'Humcste','Gsslope', 'Tphoto_opt_c',   'Tphoto_min_c', 'Tphoto_max_c', 
        'Kpheno_crit', 'Senescence_temp_c',   'LAI_MAX',   'SLA', 'Leafagecrit', 
        'Klaihappy', 'Tau_leafinit', 'Thetaleaf', 'Clumping', 'LAI_init',  
        'Z0_over_height', 'Kalbedo_soil', 'Kalbedo_veg',
        'So_capa_dry', 'So_capa_wet', 
        'Q10', 'Moistcont_a', 'Moistcont_b', 'Moistcont_c', 'Moistcont_min',  'KsoilC',
        'Z_decomp','Hcrit_litter',
        'Maint_resp_c', 'Maint_resp_slope_c', 'Frac_growthresp', 
        'Dpu_cste'
        ]


    # --- Name of the a priori input file if there is some prior information
    fic_val_prior = None


    vars = {}
    for name in parnames_template: vars[name] = {}
    
    # --- Range of variation & default uncertainties

    #vars['Vcmax_opt']['min']   = 24.
    #vars['Vcmax_opt']['max']   = 130
    #ORCHIDEE value = (/0., 65., 65., 35., 45., 55., 35., 45., 35., 70., 70., 70., 70./)
    # min = value/2 ; max = value * 2
    vars['Vcmax_opt']['min']   = [0., 32., 32., 17., 22., 27., 17., 22., 17., 35., 35., 35., 35.]
    vars['Vcmax_opt']['max']   = [0., 130., 130., 70., 90., 110., 70., 90., 70., 140., 140., 140., 140.]
    
    #vars['Fstressh']['min']   = 0.8
    #vars['Fstressh']['max']   = 8.
    #ORCHIDEE value = (/ 0., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6. /)
    vars['Fstressh']['min']   = [0., 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]
    vars['Fstressh']['max']   = [0., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.]
        
    #vars['Humcste']['min']   = 0.55
    #vars['Humcste']['max']   = 6.5
    #ORCHIDEE value = (/5., .8, .8, 1., .8, .8, 1., 1., .8, 4., 4., 4., 4./)
    # min = value /4 ; max ~ value * 2 ou *4
    vars['Humcste']['min']   = [1.25, .2, .2, .25, .2, .2, .25, .25, .2, 1., 1., 1., 1.]
    vars['Humcste']['max']   = [10., 3, 3, 4., 3., 3., 4., 4., 3., 10., 10., 10., 10.]    
    
    #vars['Gsslope']['min']   = 0.
    #vars['Gsslope']['max']   = 12.
    #ORCHIDEE value = (/0., 9., 9., 9., 9., 9., 9., 9., 9., 9., 3., 9., 3./)
    # min = value / 3 ; max ~ value * 2/3
    vars['Gsslope']['min']   = [0., 3., 3., 3., 3., 3., 3., 3., 3., 3., 1., 3., 1.]
    vars['Gsslope']['max']   = [0., 15., 15., 15., 15., 15., 15., 15., 15., 15., 9., 15., 9.]
    
    
    #vars['Tphoto_opt_c']['min']   = 17.5
    #vars['Tphoto_opt_c']['max']   = 48.
    #ORCHIDEE value = (/ 0., 37., 37., 25., 32., 26., 25., 25., 25., 27.25, 36., 30., 36./)
    # min = value-20 ; max = value+20
    vars['Tphoto_opt_c']['min']   = [0., 17., 17., 5., 12., 6., 5., 5., 5., 7.25, 16., 10., 16.]
    vars['Tphoto_opt_c']['max']   = [0., 57., 57., 45., 52., 46., 45., 45., 45., 47.25, 56., 50., 56.]
    
    #vars['Tphoto_max_c']['min']   = 27.
    #vars['Tphoto_max_c']['max']   = 71.
    #ORCHIDEE value = (/ 0., 55., 55., 38., 48., 38., 38., 38., 38., 41.125, 55., 45., 55./)
    # min = value-20 ; max = value+20
    vars['Tphoto_max_c']['min']   = [0., 35., 35., 18., 28., 18., 18., 18., 18., 21.125, 35., 25., 35.]
    vars['Tphoto_max_c']['max']   = [0., 75., 75., 58., 68., 58., 58., 58., 58., 61.125, 75., 65., 75.]
    
    
    #vars['Tphoto_min_c']['min']   = -7.
    #vars['Tphoto_min_c']['max']   = 17.
    #ORCHIDEE value = (/0.,2.,2.,-4.,-3.,-2.,-4.,-4.,-4.,-3.25,13.,-5.,13./)
    # min = value - 5 ; max = value + 5
    vars['Tphoto_min_c']['min']   = [0., -3., -3., -9., -8., -7., -9., -9., -9., -8.25, 8., -10., 8.]
    vars['Tphoto_min_c']['max']   = [0., 7., 7., 1., 2., 3., 1., 1., 1., 2.25, 18., 0., 18.]
    
    
    #vars['Kpheno_crit']['min']   = 0.5
    #vars['Kpheno_crit']['max']   = 4.
    #ORCHIDEE value =
    vars['Kpheno_crit']['min']   = [0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    #vars['Kpheno_crit']['max']   = [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    vars['Kpheno_crit']['max']   = [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    
    
    #vars['Senescence_temp_c']['min']   = -3.
    #vars['Senescence_temp_c']['max']   = 30.
    #ORCHIDEE value = (/ 0., undef, undef, undef, undef, 12., undef, 7.,  2.,  -1.375,  5., 5., 10. /)
    #min = value - 10 ; max = value +10
    vars['Senescence_temp_c']['min']   = [0., -9999., -9999., -9999., -9999., 2., -9999., -3.,  -8.,  -11.375,  -5., -5., 0.]
    vars['Senescence_temp_c']['max']   = [0., -9999., -9999., -9999., -9999., 22., -9999., 17.,  12.,  9.375,  15., 15., 20.]
    

    #vars['LAI_MAX']['min']   = 0.1
    #vars['LAI_MAX']['max']   = 9.
    #ORCHIDEE value = (/   0.,  7.,  7.,  5.,  5.,  5., 4.5, 4.5, 3.0, 2.5, 2.5,  5.,  5. /)
    vars['LAI_MAX']['min']   = [0.,  4.,  4.,  3., 3., 3., 2.5, 2.5, 1.5, 1.5, 1.5,  3.,  3.]
    vars['LAI_MAX']['max']   = [0.,  10., 10., 7., 7., 7., 6.5, 6.5, 4.5, 3.5, 3.5,  7.,  7.]
    

    #vars['SLA']['min']   = 0.001
    #vars['SLA']['max']   = 0.04
    #ORCHIDEE value = (0, 0.015, 0.026, 0.009, 0.02, 0.026, 0.009, 0.026, 0.019, 0.026, 0.026, 0.026, 0.026)
    # min = min / 2 ; max = value * 2
    vars['SLA']['min']   = [0, 0.007, 0.013, 0.004, 0.01, 0.013, 0.004, 0.013, 0.009, 0.013, 0.013, 0.013, 0.013]
    vars['SLA']['max']   = [0, 0.03, 0.05, 0.02, 0.04, 0.05, 0.02, 0.05, 0.04, 0.05, 0.05, 0.05, 0.05]
    
    
    #vars['Leafagecrit']['min']   = 70.
    #vars['Leafagecrit']['max']   = 950.
    #ORCHIDEE value = (/   0., 730., 180., 910., 730., 180., 910., 180., 180., 120., 120., 90., 90. /)  
    vars['Leafagecrit']['min']   =  [0., 530., 80., 710., 530., 80., 710., 80., 80., 20., 20., 10., 10.]
    vars['Leafagecrit']['max']   =  [0., 930., 280., 1110., 930., 280., 1110., 280., 280., 220., 220., 200., 200.]
    

    #vars['Klaihappy']['min']   = 0.35
    #vars['Klaihappy']['max']   = 0.7
    vars['Klaihappy']['min']   = [0., 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35]
    vars['Klaihappy']['max']   = [0., 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
    
    
    #vars['Tau_leafinit']['min']   = 5.
    #vars['Tau_leafinit']['max']   = 30.
    vars['Tau_leafinit']['min']   = [0., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5.]
    vars['Tau_leafinit']['max']   = [0., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30.]
    
    
    #vars['Thetaleaf']['min']   = 30
    #vars['Thetaleaf']['max']   = 75
    vars['Thetaleaf']['min']   = [0., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30.]
    vars['Thetaleaf']['max']   = [0., 75., 75., 75., 75., 75., 75., 75., 75., 75., 75., 75., 75.]
    
    
    #vars['Clumping']['min']   = 0.6
    #vars['Clumping']['max']   = 1.
    #ORCHIDEE value = (/1., 0.63, 0.7, 0.62, 0.63, 0.7, 0.62, 0.7, 0.68, 0.74, 0.74, 0.73, 0.73/)
    vars['Clumping']['min']   = [0., 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
    vars['Clumping']['max']   = [0., 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


    #vars['LAI_init']['min']   = 0.
    #vars['LAI_init']['max']   = 9.
    # min = 0.1 ; max = MAX(LAI_max)
    vars['LAI_init']['min']   = [0., 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]  
    vars['LAI_init']['max']   = [0.,  10., 10., 7., 7., 7., 6.5, 6.5, 4.5, 3.5, 3.5,  7.,  7.]

    #vars['Maint_resp_slope_c']['min']   = 0.001
    #vars['Maint_resp_slope_c']['max']   = 0.5
    #ORCHIDEE value = (/ 0., .12, .12, .16, .16, .16, .16, .16, .16, .16, .12, .16, .12 /)
    # min = value/3 ; max = value*3
    vars['Maint_resp_slope_c']['min']   = [0., .04, .04, .05, .05, .05, .05, .05, .05, .05, .04, .05, .04]
    vars['Maint_resp_slope_c']['max']   = [0., .36, .36, .48, .48, .48, .48, .48, .48, .48, .36, .48, .36]
 
    #vars['Frac_growthresp']['min']   = 0.1
    #vars['Frac_growthresp']['max']   = 0.5
    #ORCHIDEE value = (/ 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28 /)
    vars['Frac_growthresp']['min']   = [0., 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    vars['Frac_growthresp']['max']   = [0., 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

    
    vars['Z0_over_height']['min']   = [0.02]
    vars['Z0_over_height']['max']   = [0.1]
    
    vars['Kalbedo_soil']['min']   = [0.8]
    vars['Kalbedo_soil']['max']   = [1.2]
    
    vars['Kalbedo_veg']['min']   = [0.8]
    vars['Kalbedo_veg']['max']   = [1.2]
    
    vars['So_capa_wet']['min']   = [1.5]  # *1e6
    vars['So_capa_wet']['max']   = [4.5]  # *1e6
        
    vars['So_capa_dry']['min']   = [0.9]  # *1e6
    vars['So_capa_dry']['max']   = [2.7]  # *1e6
        
    vars['Q10']['min']   = [1.]
    vars['Q10']['max']   = [3.]
    
    vars['Moistcont_a']['min']   = [-2.]
    vars['Moistcont_a']['max']   = [0.]

    vars['Moistcont_b']['min']   = [1.8]
    vars['Moistcont_b']['max']   = [6.]

    vars['Moistcont_c']['min']   = [-1.]
    vars['Moistcont_c']['max']   = [0.5]

    vars['Moistcont_min']['min']   = [0.1]    #0.125
    vars['Moistcont_min']['max']   = [0.6]    #0.375

    vars['KsoilC']['min']   = [0.25]
    vars['KsoilC']['max']   = [4.]
    
    vars['Maint_resp_c']['min']   = [0.1]
    vars['Maint_resp_c']['max']   = [2.]

    vars['Z_decomp']['min']   = [0.05]
    vars['Z_decomp']['max']   = [5.]

    vars['Hcrit_litter']['min']   = [0.01]
    vars['Hcrit_litter']['max']   = [0.5]
   
    vars['Dpu_cste']['min']   = [0.1]
    vars['Dpu_cste']['max']   = [6.]



    # --- Uncertainties
    #     By default, sigma equal to sigma_pc % times the range of variation
    #     for each parameter
    sigma_pc = 40 #25


    # --- In case no PFT dimension is specified for some physical parameters,
    #     one optimize a multiplicative variable, applied to all PFTs
    varname_pft = ['Gsslope', 'LAI_MAX', 'SLA', 'Leafage', 'Frespc']

    #  Parameter dependency with PFT
    vars['Vcmax_opt']['pft']          = 'y'
    vars['Fstressh']['pft']           = 'y'
    vars['Humcste']['pft']            = 'y'
    vars['Gsslope']['pft']            = 'y'
    vars['Tphoto_opt_c']['pft']       = 'y'
    vars['Tphoto_min_c']['pft']       = 'y'
    vars['Tphoto_max_c']['pft']       = 'y'
    vars['Kpheno_crit']['pft']        = 'y'
    vars['Senescence_temp_c']['pft']  = 'y'
    vars['LAI_MAX']['pft']            = 'y'
    vars['SLA']['pft']                = 'y'
    vars['Leafagecrit']['pft']        = 'y'
    vars['Klaihappy']['pft']          = 'y'
    vars['Tau_leafinit']['pft']       = 'y'
    vars['Thetaleaf']['pft']          = 'y'
    vars['Clumping']['pft']           = 'y'
    vars['LAI_init']['pft']           = 'y'
    vars['Z0_over_height']['pft']     = 'n'
    vars['Kalbedo_soil']['pft']       = 'n'
    vars['Kalbedo_veg']['pft']        = 'n'
    vars['So_capa_wet']['pft']        = 'n'
    vars['So_capa_dry']['pft']        = 'n'
    vars['Q10']['pft']                = 'n'
    vars['Moistcont_a']['pft']        = 'n'
    vars['Moistcont_b']['pft']        = 'n'
    vars['Moistcont_c']['pft']        = 'n'
    vars['Moistcont_min']['pft']      = 'n'
    vars['KsoilC']['pft']             = 'n'
    vars['Maint_resp_c']['pft']       = 'n'
    vars['Maint_resp_slope_c']['pft'] = 'y'
    vars['Frac_growthresp']['pft']    = 'y'
    vars['Dpu_cste']['pft']           = 'n'
    vars['Z_decomp']['pft']           = 'n'
    vars['Hcrit_litter']['pft']       = 'n'
    

    #  Bounds & sigma for these multiplicative parameters
    for vname in varname_pft:
        vars['K'+vname] = {}
        vars['K'+vname]['min']   = 0.5
        vars['K'+vname]['max']   = 2
        vars['K'+vname]['sigma'] = 1
        vars['K'+vname]['pft'] = 'n'


    # Parameter dependency with the site
    for name in parnames_template:
        vars[name]['site']          = 'n'

    vars['KsoilC']['site']             = 'y'

    # Parameter dependency with the region
    for name in parnames_template:
        vars[name]['region']          = 'y'

    vars['KsoilC']['region']             = 'n'



    # --- eps for each parameters, used for finite difference computations of the
    #     ORCHIDEE Jacobian and the gradient of the misfit function
    
    for vname in vars.keys(): vars[vname]['eps'] = 1.e-5
    vars['Kpheno_crit']['eps' ]                  = 6.e-2
    vars['Senescence_temp_c']['eps']             = 0.4
    ##vars['LAI_MAX']['eps' ]                      = 1.e-1 #1.e-4 marche aussi...
    vars['SLA']['eps']                           = 1.e-7
    vars['Z0_over_height']['eps' ]               = 1.e-7
    vars['Leafagecrit']['eps' ]                  = 1.e-3
    #vars['Z0_over_height']['eps' ]               = 1.e-7

    
    # -- How are computed the Jacobian and the derivative of the misfit
    # -- function for each parameter?
    #     + finite_differences (default)
    #     + tl (tangent linear)
    for vname in vars.keys():  vars[vname]['deriv'] = 'finite_differences'

    # Compute the gradient of misfit function (obs vs prior) as a function of eps
    test_gradMF_vs_eps = False 
    eps_val = [2, 1, 0.5, 0.1, 0.07, 0.06, 0.05, 0.04 , 0.03, 0.02, 0.01, 0.001, 0.0001, 0.00001] # values taken by eps

    # --- Prior values on the parameters (missval when no priori information)
    # -- prescribe some value to scan Fmisfit
    for vname in vars.keys():  vars[vname]['value'] = Config.missval[1]


    # -- Parameters to optimize: Transformations to apply to the parameters
    #    + none : ''
    #    + linear : (x-xp)/sigma
    #    + norm : (x-xmin)/(xmax-xmin)
    for vname in vars.keys(): vars[vname]['transform'] = 'linear' 



# ==============================================================================================


# ==============================================================================================
class Data_def:
#  Data characteristics
# ==============================================================================================

    # ---  Name of the potential observation
    obsnames_template = ['NEEt','Qh','Qle', 'Rn', 'fAPARt','aboBm','GPPt','Rh','Rm','Rg']
    
    # --- Dictionary for each variable
    vars = {}
    for name in obsnames_template:
        vars[name] = {}
    
    # --- Input files
    for name in obsnames_template:
        vars[name]['fic_obs'] = None           # name of the input observation file
        vars[name]['fic_sim'] = Config.orch_flux_out   # name of the ORCHIDEE output file

        vars[name]['name_obs'] = name           # name of variable in the input observation file
        vars[name]['name_sim'] = name           # name of the variable in the ORCHIDEE output file
        
        vars[name]['time_counter_obs'] = 'time_counter'
        vars[name]['time_counter_sim'] = 'time_counter'
        

    fapar_std_name = None # Name of the fAPAR error variable in the fic_flux file

    obsname = None       # Name of all optimized variables

    fapar_obs_skip = None          # number of days to skip in the observation file

  
    # --- Processing of the observed variables
    # Select the temporal resolution between predifined choices
    #   = ''               # temporal resolution of the input data
    #   = '21600.'         # subsampling of the data every six hours time step
    #   = 'daily'          # daily data
    #   = 'daily_smooth'   # daily data + smoothing
    #   = 'random_1460'    # random drawing of XXXX data among the whole time series
    #   = 'daily_diurnal'  # split data into 'daily' and 'diurnal' cycles
    #   = 'normalize_vMInp.vMAX'     # v = (v-vMIN)/(vMAX-vMIN)
    #   = 'interpol_daily' # interpol data on a daily basis
    #
    # smoothing : smoothmaw : moving average window (default)
    #             smoothgauss : gaussian filter
    #
    # typically for fAPAR use : 'daily_smoothgauss_normalize_0_100' => compute daily means
    #                                                                  smooth using gaussian filter
    #                                                                  normalize data between 0 and 1

    
    # np.ed to define the processing for OBSERVATIOnp.and ORCHIDEE SIMULATIONS
    for name in obsnames_template:
        vars[name] ['processing_obs'] = 'daily_smoothmaw'
        vars[name] ['processing_sim'] = 'daily_smoothmaw'

    
    # -- How are computed daily fluxes & mean diurnal flux cycles
    # - daily fluxes are computed as the mean of the data between tdaily_i and tdaily_f (local time)
    # - mean diurnal cycles are computed as the mean of the fluxes observed between 0h and 24h over a period
    # - of XXX days
    
    # - daily fluxes
    # temporal window
    [tdaily_d,tdaily_f] = [0,24] # daily fluxes calculated between 0h and 24h, local time 
    #[tdaily_d,tdaily_f] = [10,16]  # daily fluxes calculated between 10h and 16h, local time to soften errors

    # - diurnal cycles
    # length of the diurnal cycles : multiple of weeks | multiple of months
    #                                => the time series is splitted into a multiple of diurnal_length
    diurnal = {}
    diurnal['test'] = False
    diurnal['length'] = '1m'  # for months  
    #diurnal['length'] = '2w'# for weeks   

    # periodicity: The misfit function then accounts for the diurnal cycle every diurnal_period
    #  ex. if diurnal_period = 3 => every 3 month
    diurnal['period'] =   1 

    # possibility to account for the diurnal cycle for prescribed months (given as a list)
    # (see in Config.month_name). Then the duration of the time window for the computation
    # of the diurnal cycle is defined in  Config.month_length
    diurnal['month'] = None  # ['APR','MAY','AUG','SEP']
   
    
    # --- Test the misfit (RMSE) between data and prior simulations (OBSOLETE)
    #   (if True => STOP after the evaluation of the misfit)
    test_rmse_prior = False 


    # --- Errors        
        
    # - Uncertainties -

    for name in obsnames_template:
        vars[name]['sigma'] = 1

    
    # + sigma is defined as the standard deviation of the daily mean fluxes.
    #
    #   The units of sigma are given in gC/m2/day. A transformation is applied to
    #   translate sigma at the nominal temporal resolution of the data (usually half_hourly).
    #   Considering nobs_daily = 24*3600/tstep observations available, then
    #   sigma_tstep = sqrt(nobs_daily)*sigma_daily_means
    #
    # + For diurnal cycles, sigma_diurnal = sigma_tstep / sqrt(30) (simplier to consider that each month is made of 30 days)
    #
    # + np.te :it is also possible for the user to define sigma_diurnal independantly from sigma

    # + np.te that, for NEE, the units of ORCHIDEE outputs are in gC/m2/s. They are recast in ORCHIS in gC/m2/time_step
    #  (for instance 1e-6 gC/m2/s <=> 0.0018(=1e-6*1800= gC/m2/1800s)
        
   ##  error['NEEt']['sigma']   = 0.054*48 #0.015 # in gC/m2/daily_mean <=> 0.8=0.015*48 gC/m2/daily_total
##                                      #                     <=> 0.1 gC/m2/1800s with nobs = 48
##     error['Qle']['sigma']    = 20   #5 
##     error['Qh']['sigma']     = 20   #5
##     error['Rn']['sigma']     = 30   #7
##     error['fAPARt']['sigma'] = 0.1
##     error['aboBm']['sigma']   = 1.
##     error['woodBm']['sigma']   = 1.
    

    # Multiplicative parameter to scale night errors with respect to diurnal measurements
    correct_error_night = True
    for name in obsnames_template:
        vars[name]['coef_error_night'] = 2
    vars['fAPARt']['coef_error_night'] = 1

    # Time criteria to partition 24h of measurements between day and night
    [time_day_d, time_day_f] = [10,16]


    # --- Adjust the observation uncertainties

    # - so that the partial Chi2 of each obs is about 1
    # partial Chi2 = 2*MFobs/np.bs. The correction is applied once at the
    # loop # Config.nloop_adjust_chi2
    adjust_chi2_obs = False

    # - so that sigma(daily) = sigma(diurnal)  
    adjust_daily_diurnal = False

    
    # - contribution of the observation to the misfit function (Sum(contribMFobs) = 1)
    # Allow correction of the influence of a given obs on MFobs (the correction to apply is computed at nloop = 10)
    # The correction is applied once at the loop # Config.nloop_modif_contrib_obs
    # This is an additional correction, applied after that on partial Chi2
    adjust_contrib_MF_obs = False

    for name in obsnames_template:
        vars[name]['contrib_MF_obs'] = 1
          

    # -- Determine automatically the prior error on observations
    #    from the computation of the RMSE between observations and
    #    the prior simulation
    auto_sigma_obs = False
    #    and the corrective factor applied (sigma=rmse/corr)
    corr_sigma_obs = {}
    for name in obsnames_template:
        corr_sigma_obs[name] = 1.
    
# ==============================================================================================



# ==============================================================================================
class Opti_def:
#  Optimization characteristics
# ==============================================================================================

    #Modifs JDS for genetic algorithms
    #Number of Chromosomes
    n_chr=40
    #Mutation rate
    mutation_rate=0.2
    #number of crossing points
    n_cross_pts=2

    # -- Method
    #  - bfgs (default) | use the BFGS optimizer
    #  - iter_tarantola | use the iterative approach of tarantola
    method = 'bfgs'
    
    # -- Data space for the optimization
    #    - 'obs-par' : observations & parameters
    #    - 'obs' : observations
    #    - 'par' : parameters
    Fmisfit_space = 'obs-par'
    #space = 'obs'
    #space = 'par'
   


    # -- Calculate the prior error in observations space by
    #    propagating the prior error on parameters
    propagate_Bprior = False

    # -- Calculate the posterior error on observations
    calculate_Rpost = False

    # -- Sensitivity test of the misfit function around its minimum
    #  - The parameters are varied one after the other
    #  variation of the parameters around the posterior
    #  value by the amount of pcvar% of their variation range
    test_sensitivity_Fmisfit_prior = False
    test_sensitivity_Fmisfit_post  = False
    nlevels = 7
    pcvar   = 10
    
    # -- Maximum number of iteration loops for the optimization algorithm
    nloop_max = 100
    
    # -- Scan the value of the misfit function around the parameter values
    #  - Determine a simulation plan where all parameters are varied simultaneously
    scan_fmisfit_prior = False # for the prior parameters
    scan_fmisfit_post  = False # for the posterior parameters

    scan_levels = 11     # number of levels around xprior for each parameters
    scan_pc = 100        # percentage of variation around the prior value
    scan_local  = True   # scan around value +- eps*(levels-1)/2
    scan_global = False  # scan around value +- (max-min)*scan_pc


    
    # Determine if the computation of the misfit function is performed either accountig for :
    # - only the diagonal elements of the covariance matrices on observations & parameters 
    #   => no accounting for covariances
    # - all elements of the covariance matrices
    #computeFmisfit = {}
    #computeFmisfit['MFpar'] = 'diagonal' # 'full' or 'diagonal'
    #computeFmisfit['MFobs'] = 'diagonal' # 'ful' or 'diagonal'

    # -- Loop numbers at which the sigma of each observation are modified
    # -- in order to modify their respective weight in the misdit function

    # Number of loops after which the sigma on the diurnal cycle is modified
    # so that its contribution matches that of the corresponding daily data
    nloop_adjust_daily_diurnal = 5

    # Number of loops after which the sigma of each observation is modified
    # so that the relative chi2 = 1
    nloop_adjust_chi2 = 5
    
    # Number of loops after which the contribution of each observation on the
    # misfit function is modified
    nloop_modif_contrib_obs = 5

    # Save intermediate ORCHIDEE simulation at each iteration
    save_sim_iter = False

    
    # ==============================================================================
    


# ==============================================================================================
    

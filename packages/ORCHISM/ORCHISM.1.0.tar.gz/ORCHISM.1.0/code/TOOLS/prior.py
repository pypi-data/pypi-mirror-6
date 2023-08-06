#*******************************************************************************
# MODULE	: PRIOR
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 11/2007 (multisite: 03/2010)
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
Prior informations on the observation and parameters
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import os,sys,glob,random,copy
from orchis_config import Config, Paras_def
from time import localtime, strftime
import numpy as np

#from TOOLS import funcio, various, orchidee, io
import funcio, various, orchidee, io

# ==============================================================================
# Determine the indices in the observation time series kept for optimization
# Subsample of the observations if required
# ------------------------------------------------------------------------------
def indices(Data,isite):


    case = ['obs','sim']
    
    # --- Determine the indices kept for optimization ---
    
    for elem in case:

        for pname in Data.processing[isite][elem].keys():

            Data.processing[isite][elem][pname]['indices'] = None           
            bufname=pname.split('_')

            obsname = Data.processing[isite][elem][pname]['vars'][0]
            
            if elem == 'obs':
                n_ts = int(len(Data.obs[isite][obsname]))
            else:
                n_ts = int(len(Data.sim[isite][obsname]))
                    
            
            # subsampling of the data required
            # -> pname = 21600. or random_1500 (or similar to...)
            test_subsampling = False
            if 'random' in bufname or len(bufname) == 1:
                try:
                    time_scale = int(bufname[-1])
                    test_subsampling = True
                except ValueError:
                    test_subsampling = False


            if test_subsampling == True:

                print "SUBSAMPLING IS ACTIVATED FOR "+pname

                bufname=bufname[-1]
            
                # Random drawing of XXXX elements among the whole time series
                if 'random' in pname:
                    time_scale = int(bufname)
                    indices = sorted(random.sample(range(n_ts), time_scale))
                    
                # Classical temporal sampling  
                else:
                    time_scale = int(bufname)
                    sub_tstep = float(time_scale)
                    
                    # which file ?
                    for ific in Data.fic[isite][elem].keys():
                        if obsname in Data.fic[isite][elem][ific]['vars']:
                            ific = ific
                            break

                    if elem == 'obs':
                        time_step = (Data.obs[isite]['fic'][ific]['time_step'])[0]
                    else:
                        time_step = (Data.sim[isite]['fic'][ific]['time_step'])[0]
                    n_ts    = int(n_ts*time_step/sub_tstep)
                
                    indices = range(n_ts)
                    pas     = int(sub_tstep/time_step)

                    for it in range(len(indices)):
                        indices[it] = random.randint(it*pas, (it+1)*pas-1)
                        
                Data.processing[isite][elem][pname]['indices'] = indices


            
    # --- Subsample the data ---

    # - obs
    for pname in Data.processing[isite]['obs'].keys():
        if Data.processing[isite]['obs'][pname]['indices'] != None:
            print 'OBS'
            for obsname in Data.processing[isite]['obs'][pname]['vars']:
                print 'subsampling for',obsname
                Data.obs[isite][obsname] = np.take(Data.obs[isite][obsname], Data.processing[isite]['obs'][pname]['indices'])

    # - sim
    for pname in Data.processing[isite]['sim'].keys():
        if Data.processing[isite]['sim'][pname]['indices'] != None:
            print 'SIM'
            for obsname in Data.processing[isite]['sim'][pname]['vars']:
                print 'subsampling for',obsname
                Data.sim[isite][obsname] = np.take(Data.sim[isite][obsname], Data.processing[isite]['sim'][pname]['indices'])
            
# END indices
# ==============================================================================


# ==============================================================================
# Processing applied to each variable
# ------------------------------------------------------------------------------
def processing(Data, isite):



    case = ['obs','sim']
    # --- Get the total size of the observations ---

    for pname in Data.processing[isite]['obs'].keys():
        obsname = (Data.processing[isite]['obs'][pname]['vars'])[0]
        n_ts = np.product((Data.obs[isite][obsname]).shape)
           
        
        Data.processing[isite]['obs'][pname]['n_ts'] = n_ts

    for pname in Data.processing[isite]['sim'].keys():
        obsname = (Data.processing[isite]['sim'][pname]['vars'])[0]
        n_ts = np.product((Data.sim[isite][obsname]).shape)

            
        Data.processing[isite]['sim'][pname]['n_ts'] = n_ts        


# END processing
# ==============================================================================



# ==============================================================================
# Partitioning between nighttime & daytime measurements
#
# Determination of the correction coefficients of the observation uncertainties
# for measurements acquired at night
# ------------------------------------------------------------------------------
def det_nightandday(Data, Site, isite, logfile):


    print '# Definition of the correction coefficients of the observation uncertainties for nighttime measurements'
    logfile.write('# Definition of the correction coefficients of the observation uncertainties for nighttime measurements \n')


    # --- Determine the day vs night
    #  - Indices of the night measurements (# 1 for night | 0 for day)

    #  - with respect to the value of SWnet (= 0 for night), the incoming shorwave
    #    radiation (sechiba output) to partition nights and days
    #SWnet = funcio.get_fluxes(os.path.join(Config.PATH_EXEC_TMP , 'sech_out.nc'), obs_name = ['SWnet'], tempo_res = Data.tempo_res, indices = Data.indices, ndays = Site.njours)
    #SWnet = SWnet['SWnet']
    #Data.obs['SWnet'] = SWnet
    #Data.idx_night = np.where(SWnet == 0, np.ones(len(SWnet), np.int32), 0) 
    

    
    #  - Determine the day vs night with TIME_DAY_D and TIME_DAY_F define in Config
    #    (1 for night | 0 for day)

    processing_list = Data.processing[isite]['sim'].keys()

    #DEBUG print 'DETNIGHTDAY'
    
    for pname in processing_list:

        print pname
        obsname = Data.processing[isite]['sim'][pname]['vars']
        print obsname
       
        idx_night = []
        Data.processing[isite]['sim'][pname]['idx_night'] = np.array(idx_night)

        if pname == 'day_vs_night': continue

        # Case to process : everything but 'daily' and 'daily_smooth'
        if 'daily' not in pname and \
           'diurnal' not in pname:
            
            ndata_day = len(Data.obs[isite][obsname[0]]) / (Site.time[isite]['njours'])

            # which file ?
            for ific in Data.fic[isite]['sim'].keys():
                if obsname[0] in Data.fic[isite]['sim'][ific]['vars']:
                    ific = ific
                    break

            if ndata_day > 1:
                for i in range(Site.time[isite]['njours']):
                    indices = np.arange(i*ndata_day,(i+1)*ndata_day,1, np.int)
                    
                    h = (np.take(Data.obs[isite]['fic'][ific]['time_counter'],indices))/3600. % 24
                    h_masked = np.ma.masked_inside(h, Data.time_day_d, Data.time_day_f)
                    indices_masked = np.ma.where(h_masked.mask !=1, 1, 0)
                    
                    if i == 0:
                        idx_night = indices_masked.tolist()

                    else:
                       idx_night.extend(indices_masked.tolist())

        # Process diurnal                       
        elif 'diurnal' in pname:

            ndata_day = (Data.obs[Data.obsname[isite][0]+'_diurnal'].shape)[1]

            # which file ?
            for ific in Data.fic[isite]['sim'].keys():
                if obsname[0] in Data.fic[isite]['sim'][ific]['vars']:
                    ific = ific
                    break
                
            h = np.arange(ndata_day)*Data.obs[isite]['fic'][ific]['time_step'][0]/(3600.)
            h_masked = np.ma.masked_inside(h, Data.time_day_d, Data.time_day_f)
            indices_masked = np.ma.where(h_masked.mask !=1, 1, 0)
            idx_night = indices_masked.tolist()
            
               
        Data.processing[isite]['sim'][pname]['idx_night'] = np.array(idx_night)

                                 
    # -- Determination of the correction coefficients time series:
    #   = 1 for daytime acquisition
    #   = coef_error_night for nighttime acquisition

    for name in Data.obsname_opti[isite]:
        pname = Data.vars[isite][name]['processing_sim']
        Data.vars[isite][name]['coef_correct_night'] = np.ones(Data.obs[isite][name].shape)
        if len(Data.processing[isite]['sim'][pname]['idx_night'].tolist()) > 0:
            Data.vars[isite][name]['coef_correct_night'] = np.where(Data.processing[isite]['sim'][pname]['idx_night'] == 1, Data.vars[isite][name]['coef_error_night'], 1)
#        else:
#            if 'diurnal' in pname:
#                Data.vars[isite][name]['coef_correct_night'] = np.where(Data.processing[isite]['sim'][pname]['idx_night'] == 1, Data.vars[isite][name]['coef_error_night'], 1)
#            else:
                # daily data => no correction applied
#                Data.vars[isite][name]['coef_correct_night'] = np.ones(Data.obs[isite][name].shape)

        # For day vs night processing, quite straigthforward
        if '_night' in name:

            Data.vars[isite][name]['coef_correct_night'] = np.ones(Data.obs[isite][name].shape)*Data.vars[isite][name]['coef_error_night']
            #print Data.vars[isite][name]['coef_correct_night'][0:5]
        print name
        #print Data.vars[isite][name]['coef_correct_night']
            
# END det_nightandday
# ==============================================================================





# ==============================================================================
# Determine the background error variance-covariance matrix on parameters
# according to the information provided in the def_XXX.py file
#
# Add the component B to the structure received as input
# (error covariance matrix)
# ------------------------------------------------------------------------------
def detmatcov_paras(Site, Vars, logfile):
    

    print
    print '# Definition of B :',
    logfile.write('\n# Definition of B : ')
    

    # -- B diagonal
    Vars.B = {} # = np.ones(len(Paras.varname), np.float64)
    icnt = 0

    for name in Vars.vars['opti_varname']:

        # If the variables is region-dependent, we have a dictionnary of 1D (time) or 2D arrays (PFT*time)
        # for each region. After selecting the right map, the parameters values
        # in each region are concatenated (y direction). It is workable because the number of rows
        # (time dimension) is always the same.
        if len(Vars.vars[name]['dim_name']) > 2:

            icnt2 = 0            

            for ireg in Vars.vars[name]['3rd_loop']:

                #tmp = np.ones(Vars.vars[name]['value'][ireg].shape, np.float64) * (Vars.vars[name]['sigma']**2)
                tmp = Vars.vars[name]['sigma'][ireg]**2
                if icnt2 == 0:
                    Vars.B[name] = tmp
                else:
                    Vars.B[name] = np.concatenate((Vars.B[name], tmp))
                icnt2+=1
                
        else:
            #Vars.B[name] = np.ones(Vars.vars[name]['value'].shape, np.float64) * (Vars.vars[name]['sigma']**2)
            Vars.B[name] = Vars.vars[name]['sigma']**2

        if icnt == 0:
            Vars.B['all'] = np.array(Vars.B[name].ravel(), np.float64)
        else :
            Vars.B['all'] = np.concatenate((Vars.B['all'], Vars.B[name].ravel()))
        icnt+=1

    # -- Copy the value of B a priori to B a posteriori
    Vars.Bpost = copy.deepcopy(Vars.B)
    
    # -- Full B matrix
    #if Config.computeFmisfit['Jpar'] == 'full':
    #    print ' all covariances are accounted for ',
    #    
    #    Vars.B['array'] = np.identity(len(Vars.name), np.float64)
    #    
    #    for ip in range(len(Vars.name)):
    #        Vars.B['array'][ip,ip] = Vars.B['array'][ip,ip] * (Vars.vars[Vars.name[ip]]['sigma']**2)

            
    print ' OK'
    logfile.write('OK\n')

# END detmatcov_paras    
# ==============================================================================

# ==============================================================================
# Propagate the uncertainties on parameters in the observations space

def propagate_Bprior(Vars, Data, Opti, logfile):


    print
    print '# Propagation of prior error of parameters in observation space :'
    logfile.write('\n # Propagation of prior error of parameters in observation space :\n')

    #-DEBUG : test presence d'elements NaN
    #
    #buf = np.ma.masked_where(Data.Jacobian <= Config.missval[0], Data.Jacobian)
    #buf = np.ma.masked_where(Data.Jacobian >= Config.missval[1], buf)
    buf = np.ma.masked_values(Data.Jacobian, Config.missval[0])
    buf = np.ma.masked_values(buf, Config.missval[1])
    if buf.mask != None: 
        print '---------'*15
        print 'WARNING '*15
        print 'WARNING '*15
        print 'PRIOR : Presence de valeurs NaN dans le Jacobien pour le calcul de la matrice de covariance d''erreur a priori sur les obs'
        print 'WARNING '*15
        print 'WARNING '*15
        print '---------'*15
        logfile.write('\n'+'---------'*15)
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'PRIOR : Presence de valeurs NaN dans le Jacobien pour le calcul de la matrice de covariance d''erreur a priori sur les obs')
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'---------'*15+'\n')
    #    
    #-

    # -------------------
    # --- Computation ---
    # -------------------
    Bprior = np.zeros((Opti.n,Opti.n), np.float64)
    for i in range(Opti.n):
        Bprior[i,i] = Vars.B['all'][i]

    #buf = np.zeros((Data.nobs,Opti.n), np.float64)
    
    #for i in range(Data.nobs):
    #    for j in range(Opti.n):
    #        buf[i,j] = Data.Jacobian[j,i]*Vars.B['all'][j]

    buf    = np.dot(np.transpose(Data.Jacobian), Bprior)
    Opti.Rprior = np.dot(buf, Data.Jacobian)
    Data.Jacobian_prior = copy.deepcopy(Data.Jacobian)

    # ------------------------------------------
    # --- Save the results in the class Opti ---
    # ------------------------------------------
    #Opti.Rprior = Rprior

    # --- Free some memory...
    del(buf)
    
# END propagate_Bprior
# ==============================================================================


# ==============================================================================
# Determine the observation error variance-covariance matrix 
# according to the information provided in the def_XXX.py file
#
# Add the component Data.R to the structure received as input
# (error covariance matrix)
# ------------------------------------------------------------------------------
def detmatcov_obs(Site, Data, logfile, init = None, modif_sigma = False, detect_gapf = False):
    

    # -- Do we use the information provided by the prior simulation ?
    if Data.auto_sigma_obs == True and init == True:
        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:
                val_rmse = various.rmse(Data.obs[isite][name],Data.sim[isite][name])
                Data.vars[isite][name]['sigma'] = val_rmse / Data.corr_sigma_obs[name]
                

    print 
    print '# Definition of R :',
    logfile.write('\n# Definition of R :')

    
    # -- Diagonal covariance matrix
    Data.R = {}


    # -- Modify the values of sigma as a function of the chosen temporal
    #    resolution (done only at the first pass!)
    if modif_sigma == True:

        for isite in range(Site.npts):
        
            for name in Data.obsname_opti[isite]:
                
                
                # -- Save a copy of the value
                Data.vars[isite][name]['sigma_user'] = copy.copy(Data.vars[isite][name]['sigma'])

                # if assimilation of non integrated flux measurements, correction of SIGMA
                # with respect to the number of obs used.
                # if 'daily' not in Data.vars[isite][name]['processing_sim'] and \
                #    'diurnal' not in Data.vars[isite][name]['processing_sim']:
                
                # # Here we consider that only Data.nobs_daily are  used to compute the daily mean
                #    nnobs = Data.vars[isite][name]['nobs_daily']
                #    if nnobs == None:
                # # Here we consider that all data are used to compute the daily mean
                #       nnobs = 24*3600/Data.obs[isite]['time_step'][0]
                
                #    print Data.vars[isite][name]['sigma']
                #    Data.vars[isite][name]['sigma'] = Data.vars[isite][name]['sigma']*np.sqrt(nnobs)
                #    print Data.vars[isite][name]['sigma']
                #    raw_input('pause')
        
                # diurnal cycle 
                if 'diurnal' in Data.vars[isite][name]['processing_sim']:
                    
                    bufname=(name.split('_'))[0]
                    
                    # ## Here we consider that only Data.nobs_daily are  used to compute the daily mean
                    nnobs = Data.vars[isite][bufname]['nobs_daily']
                    if nnobs == None:
                        # ## Here we consider that all data are used to compute the daily mean
                        nnobs = 24*3600/Data.obs[isite]['time_step'][0]
                        
                    Data.vars[isite][name]['sigma'] = Data.vars[isite][bufname]['sigma']*np.sqrt(nnobs)/np.sqrt(30)
        

       
    # -- Save modified values in sigma_prior & sigma_diurnal_prior
    for isite in range(Site.npts):
        for name in Data.obsname_opti[isite]:
            #print Data.vars[isite][name]['sigma']
            Data.vars[isite][name]['sigma_prior'] = copy.deepcopy(Data.vars[isite][name]['sigma'])
            


    # -- Building the R matrix itself
    icnt = 0
    for isite in range(Site.npts):

        icnt2 = 0
        site = Site.name[isite]
        
        for name in Data.obsname_opti[isite]:
        
            print name

            # Set the data name to distinguish data from each site :
            # 'data name for the site' = 'data name'_'site number'
            name_site = name+'_'+Site.name[isite]


            # Only the diagonal elements of R are accounted for   
            # 1) Account for a temporal variation of fAPAR errors
            if name == 'fAPARt' and Data.fapar_std_name != None:
                Data.R[name_site] = Data.obs['std_fAPARt']**2            
            # 2) Normal case...
            else:
                Data.R[name_site] = np.multiply( np.ones( Data.obs[isite][name].shape , np.float64 ), Data.vars[isite][name]['sigma']**2)

            # Apply correction for nighttime measurements if required
            Data.R[name_site] = np.multiply( Data.R[name_site], Data.vars[isite][name]['coef_correct_night']**2)

            # Apply correction for gap-filled data (if activated) :
            # for each processed time step, sigma is multiplied by 1+'% of gap-filled data'
            if detect_gapf == True:
                #print Data.obs[isite][name+'_fqc']*48.
                coef_gap = 1+Data.coef_gapf*Data.obs[isite][name+'_fqc']
                #if coef_gap.any() == 1: print 'A perfect day !!'
                #if coef_gap.any() < 1: print 'Problem !!'
                #print coef_gap
                #print '================================'
                Data.R[name_site] = np.multiply( Data.R[name_site], coef_gap**2)
                #print coef_gap

            # All elements
            if icnt == 0:
                Data.R['all'] = np.array(Data.R[name_site].ravel(), np.float64)
            else:
                Data.R['all'] = np.concatenate((Data.R['all'], Data.R[name_site].ravel()))
            
            if icnt2==0:
                Data.R[site] = np.array(Data.R[name_site].ravel(), np.float64)
            else:
                Data.R[site] = np.concatenate((Data.R[site], Data.R[name_site].ravel()))

            icnt+=1
            icnt2+=1


    # -- Copy the value of R a priori 
    if init == True: Data.Rprior = copy.copy(Data.R)

    # Prepare R for a matrix product
    #if Config.computeFmisfit['Jobs'] == 'matrix':
    #    print ' forme matricielle ',
        
    #    for name in Data.obsname:
    #        Data.iR[name] = np.identity(nts, np.float64)/(Data.vars[name]['sigma']**2)

    print ' OK'
    logfile.write(' OK\n')


# END detmatcov_obs
# ==============================================================================



# ==============================================================================
# Determine the prior value of the optimization parameters
#
# Return a dictionnary with all informations on the parameters
# Return a class of dictionnary with all informations on the parameters,
# global attributes and dimensions for the writting of the NetCDF file
#
# ------------------------------------------------------------------------------
def detprior_paras(Paras, Site, logfile):

    print '# Definition of the a priori parameter values'
    logfile.write('# Definition of the a priori parameter values\n')


    # --- Determine which parameters are user defined and which are default values ---

    for pname in Paras.vars.keys():
        # default values are used
        if Paras.vars[pname]['value'] in Config.missval: Paras.vars[pname]['info_prior']='defaut'
        # user values are used
        else: Paras.vars[pname]['info_prior']='user' 


    # -- Loop on each site --- 

    vars_prior_site = {}
    vars_fg_site = {}
    gattr_site = {}
    dims_site = {}

    # - Background

    # Are there a user defined input parameter file ? ---
    if Paras.fic_val_xbg != None:
        if len(glob.glob(Paras.fic_val_xbg)) == 0:
            print " # WARNING : the user file containing the prior information on x has not been found "
            print "             ", Paras.fic_val_xbg
            print "            -> standard ORCHIDEE parameters are used as background"
                
            logfile.write(" # WARNING : the user file containing the prior information on x has not been found \n")
            logfile.write("              "+ Paras.fic_val_xbg + "\n")
            logfile.write("            -> standard ORCHIDEE parameters are used as background\n")
                
            Paras.fic_val_xbg = None


        
    # --- Get ORCHIDEE prior values
    # - Create a run.def file just to get the prior values of the parameters

    for isite in range(Site.npts):

        os.chdir(Config.PATH_EXEC_SITE[isite])

        file_para_prior = os.path.join(Config.PATH_EXEC_SITE[isite] , 'para_ORCH_prior.nc')
        driv_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'driv_restart.nc')
        sech_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'sech_restart.nc')
        stom_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'stom_restart.nc')    
        
        orchidee.gen_rundef(pathout = Config.PATH_EXEC_SITE[isite], \
                                site = Site.name[isite], \
                                ficConfig = Site.fic_cfg[isite], \
                                time_length = '1Y',\
                                optim = 'y', \
                                optim_para_in = Paras.fic_val_xbg, \
                                for_clim = Config.FORCING_FILE, \
                                driv_restart = driv_restart,\
                                sech_restart = sech_restart,\
                                stom_restart = stom_restart,\
                                optim_para_out = file_para_prior)
        
        # Execute ORCHIDEE
        os.system('rm -f ' + driv_restart + ' ' + sech_restart + ' '+stom_restart )
        os.system(Config.cmde_orchidee + ' > orchidee.log')
        os.system('rm -f   '+driv_restart + ' ' + sech_restart + ' '+stom_restart)
        
        [vars_prior_site[isite], gattr_site[isite], dims_site[isite]] = io.readnc(file_para_prior)

    [vars_prior, gattr_prior, dims_prior] = io.readnc(file_para_prior)


    # - First Guess
            
    # Are there a user defined input parameter file ? ---
    if Paras.fic_val_xfg != None:
        if len(glob.glob(Paras.fic_val_xfg)) == 0:
            print " # WARNING : the user  file containing the first guess on x has not been found :"
            print "             ", Paras.fic_val_xfg
            print "            -> standard ORCHIDEE parameters are used as first guess"
            
            logfile.write(" # WARNING : the user file containing the first guess on x has not been found \n")
            logfile.write("               "+ Paras.fic_val_xfg + "\n")
            logfile.write("            -> standard ORCHIDEE parameters are used as first guess \n")

            Paras.fic_val_xfg = None



    os.chdir(Config.PATH_EXEC_SITE[isite])
    
    # --- Get first guess values if necessary
    # - Create a run.def file just to get the first guess values of the parameters

    for isite in range(Site.npts):

        os.chdir(Config.PATH_EXEC_SITE[isite])

        file_para_fg = os.path.join(Config.PATH_EXEC_SITE[isite] , 'para_ORCH_fg.nc')
        driv_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'driv_restart.nc')
        sech_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'sech_restart.nc')
        stom_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'stom_restart.nc')  
    
        orchidee.gen_rundef(pathout = Config.PATH_EXEC_SITE[isite], \
                                site = Site.name[isite], \
                                ficConfig = Site.fic_cfg[isite], \
                                time_length = '1Y',\
                                optim = 'y', \
                                optim_para_in = Paras.fic_val_xfg, \
                                for_clim = Config.FORCING_FILE, \
                                driv_restart = driv_restart,\
                                sech_restart = sech_restart,\
                                stom_restart = stom_restart,\
                                optim_para_out = file_para_fg)
        
        # - Execute ORCHIDEE
        os.system('rm -f ' + driv_restart + ' ' + sech_restart + ' '+stom_restart )
        os.system(Config.cmde_orchidee + ' > orchidee.log')
        os.system('rm -f   '+driv_restart + ' ' + sech_restart + ' '+stom_restart)
    
        [vars_fg_site[isite], buf, buf] = io.readnc(file_para_fg)
        del(buf)

    [vars_fg, buf, buf]       = io.readnc(file_para_fg)
    del(buf)
            
    # ------------------------------------------------------------
    # --- Modify the dimensions to suit mulitiste optimization ---
    # ------------------------------------------------------------
    #     Allocate the values of the parameters according to the proper

    #     user defined dimensions

    # -- First create the output parameter dictionnary
    # -------------------------------------------------
    vars={}
    vars['opti_varname'] = Paras.opti_varname
    vars['varname']      = Paras.varname
  

    ## - PFT region ##
    
    # The PFT dictionnary has to be built for each region of each map...
    vars['PFT'] = copy.copy(vars_prior['PFT'])
    vars['PFT']['dim_name'] = tuple(['indice_pft'])
    vars['PFT']['dim_size'] = {}
    vars['PFT']['value'] = {}
    vars['PFT']['indexes']= {}
    
    #  Aggregate all the different pfts coming from the sites in one array for each region
    for imap in Site.real_maps:
        vars['PFT']['dim_size'][imap] = {}
        vars['PFT']['value'][imap] = {}
        vars['PFT']['indexes'][imap] = {}
        
        for ireg in Site.map['occupied_regions'][imap]:
            prems = 0
            #            print Site.site_ind[map][ireg]
            for isite in Site.site_ind[imap][ireg]:
                # Check if the site is in the region processed (index reg)
                if prems == 0:
                    tmp = copy.copy(Site.indice_pft[isite])
                    prems = 1
                else:
                    for i in range(len(Site.indice_pft[isite])):
                        if Site.indice_pft[isite][i] not in tmp:tmp.append(Site.indice_pft[isite][i])
            tmp.sort()
        
            vars['PFT']['dim_size'][imap][ireg] = len(tmp)
            vars['PFT']['value'][imap][ireg] = np.array(tmp, np.int32)
            
            # Identify in the pfts array the indexes corresponding to each site (useful later !)
            vars['PFT']['indexes'][imap][ireg] = {}
            for isite in Site.site_ind[imap][ireg]:
                ind = np.zeros(len(Site.indice_pft[isite]), np.int32)
                k=0
                for i in range(vars['PFT']['dim_size'][imap][ireg]):
                    if vars['PFT']['value'][imap][ireg][i] in Site.indice_pft[isite]:
                        np.put(ind,k,i)
                        k+=1
                vars['PFT']['indexes'][imap][ireg][isite]=ind

    ## - PFT site
    vars['PFT_site'] = {}
    vars['PFT_site']['dim_name'] = tuple(['indice_pft'])
    vars['PFT_site']['indexes']= {}
    k=0
    for isite in range(Site.npts):
        ind = np.arange(len(Site.indice_pft[isite]))+k
        vars['PFT_site']['indexes'][isite] = ind
        k=k+len(ind)


    ## - PFT global ##
                
    # same as before except that the PFT genericity is considered as global
    vars['PFT_global'] = {}
    vars['PFT_global']['dim_name'] = tuple(['indice_pft'])

    # Aggregate all the different pfts coming from the sites in one global array
    tmp = copy.copy(Site.indice_pft[0])
    for isite in range(Site.npts-1):
        for i in range(len(Site.indice_pft[isite+1])):
            if Site.indice_pft[isite+1][i] not in tmp:tmp.append(Site.indice_pft[isite+1][i])
    tmp.sort()
    vars['PFT_global']['dim_size'] = len(tmp)
    vars['PFT_global']['value'] = np.array(tmp, np.int32)

    # Identify in the pfts array the indexes corresponding to each site (useful later !)
    vars['PFT_global']['indexes']={}
    for isite in range(Site.npts):
        ind = np.zeros(len(Site.indice_pft[isite]), np.int32)
        k=0
        for i in range(vars['PFT_global']['dim_size']):
            if vars['PFT_global']['value'][i] in Site.indice_pft[isite]:
                np.put(ind,k,i)
                k+=1
        vars['PFT_global']['indexes'][isite] = ind
        
            
    # -- Second, resize the dimensions
    # --------------------------------
    dims = {}
    for imap in Site.real_maps:
        dims[imap]={}
        for ireg in Site.map['occupied_regions'][imap]:
            dims[imap][ireg] = copy.copy(dims_prior)
            for idim in range(len(dims[imap][ireg])):
                dimname = dims[imap][ireg][idim]['name']
                if dimname == 'points_terre': dims[imap][ireg][idim]['size'] = Site.npts_reg[imap][ireg]
                if dimname == 'indice_pft': dims[imap][ireg][idim]['size'] = vars['PFT']['dim_size'][imap][ireg]
                if dimname == 'variation_day': dims[imap][ireg][idim]['size'] = Site.time[isite]['njours']
                if dimname == 'variation_week': dims[imap][ireg][idim]['size'] = Site.time[isite]['nsemaines']
                if dimname == 'variation_month': dims[imap][ireg][idim]['size'] = Site.time[isite]['nmois']
                if dimname == 'variation_year': dims[imap][ireg][idim]['size'] = Site.time[isite]['nannees']
            


    # -- Third, scan each parameter
    # ------------------------------
    varnames = Paras_def.parnames_template
    for pname in varnames:
        if 'K'+pname in Paras.opti_varname: varnames.append('K'+pname)


    for pname in varnames:

        # LAI_init and Q10 : remove the dummy site-dependence
        if (pname == 'LAI_init' or pname == 'Q10') and 'points_terre' in vars_prior[pname]['dim_name']:
            vars_prior[pname]['value'] = vars_prior[pname]['value'][0]
            vars_fg[pname]['value'] = vars_fg[pname]['value'][0]
            for isite in range(Site.npts):
                vars_prior_site[isite][pname]['value'] = vars_prior_site[isite][pname]['value'][0]
                vars_fg_site[isite][pname]['value'] = vars_fg_site[isite][pname]['value'][0]

        #--- Allocate the default values ---
        
        #- Copy the default values
        if pname in vars_fg.keys():         # actual ORCHIDEE parameter
            #vars[pname] = copy.copy(vars_fg[pname])
            buf = copy.copy(vars_fg[pname])  # copy of the defaut parameters to be tuned with user defined informations
        else:
            sys.exit('The parameter '+pname+' cannot be find in the ORCHIDEE parameter file -> ORCHISM stops')

        # else:
        #     # initialization : null values
        #     vars[pname] = {}
        #     buf={}
        #     vars[pname]['value'] = -9999.
        #     buf['dim_name'] = copy.copy([])
            
        #     # multiplicative ORCHIDEE parameter for all PFTs
        #     if pname[1:] in vars_fg.keys(): 
        #         vars[pname] = copy.copy(vars_fg[pname[1:]])
        #         buf = copy.copy(vars_fg[pname[1:]])  # copy of the defaut parameters to be tuned with user defined informations
        #         buf['value'] = np.ones(len(buf['value']), np.float64)
                
        #     # Better to stop here than to do something probably wrong
        #     #else :
        #     #    sys.exit('The parameter '+pname+' cannot be find in the ORCHIDEE parameter file -> ORCHISM stops')
            
        #     if 'indice_pft' in buf['dim_name']:
        #         tmp = list(buf['dim_name'])
        #         tmp.remove('indice_pft')
        #         buf['dim_name'] = tuple(tmp)

        # -- Copy of the prior values
        values_prior = copy.deepcopy(vars_prior[pname]['value'])
        values_prior_site = {}
        for isite in range(Site.npts):
            values_prior_site[isite] = copy.deepcopy(vars_prior_site[isite][pname]['value'])

        # -- First guess
        values_fg = copy.deepcopy(vars_fg[pname]['value'])
        values_fg_site = {}
        for isite in range(Site.npts):
            values_fg_site[isite] = copy.deepcopy(vars_fg_site[isite][pname]['value'])


        # - Resize each parameter after checking the dependencies  in the definition file       
        tmp = list(buf['dim_name'])
        #tmp2= list(buf['dim_size'])

        # Dependence on site
        if pname in Paras.vars.keys():
                if Paras.vars[pname]['dims']['points_terre']==1 and 'points_terre' not in buf['dim_name']:
                    tmp.insert(0,'points_terre')

        if 'points_terre' in buf['dim_name'] and pname:
            if pname not in Paras.vars.keys() or (pname in Paras.vars.keys() and Paras.vars[pname]['dims']['points_terre']==0):
                tmp.remove('points_terre')

        # Dependence on the region (used only if optimized)
        if pname in Paras.vars.keys() :
            if Paras.vars[pname]['dims']['indice_region']>0:
                tmp.insert(0,'indice_region')
            # the dim_size value is not really important here
           #tmp2.insert(0,len(Site.maps['occupied_regions'][Paras.vars[pname]['dims']['indice_region']]-1]))

        buf['dim_name'] = tuple(tmp)
        #buf['dim_size'] = tuple(tmp2)
        # -------------------------------------------------------

        #- Values for the time dimension
        tstr = ''
        tsize = 1
        tvar = 'variation_fix'

        # if the parameter is optimizable and potentially defined by the user
        if pname in Paras.vars.keys():
            if Paras.vars[pname]['dims']['variation_temp'] == 'variation_day'  :tsize = Site.time[isite]['njours']   ; tvar = 'variation_day'  ; tstr = 'D'
            if Paras.vars[pname]['dims']['variation_temp'] == 'variation_week' :tsize = Site.time[isite]['nsemaines']; tvar = 'variation_week' ; tstr = 'W'
            if Paras.vars[pname]['dims']['variation_temp'] == 'variation_month':tsize = Site.time[isite]['nmois']    ; tvar = 'variation_month'; tstr = 'M'
            if Paras.vars[pname]['dims']['variation_temp'] == 'variation_year' :tsize = Site.time[isite]['nannees']  ; tvar = 'variation_year' ; tstr = 'Y'


        # - get the min & max values if defined by the user
        min_user = None
        max_user = None

        if pname in Paras.vars.keys():
            # Min
            if Paras.vars[pname]['min'] != Paras_def.vars[pname]['min']:
                # met sous forme de Tableau
                if type(Paras.vars[pname]['min']) == type(1) \
                   or type(Paras.vars[pname]['min']) == type(1.1):
                    min_user = np.array([Paras.vars[pname]['min']])
                    Paras.vars[pname]['min'] = min_user[:]
                else:
                    min_user = Paras.vars[pname]['min']
            # Max
            if Paras.vars[pname]['max'] != Paras_def.vars[pname]['max']:
                # met sous forme de Tableau
                if type(Paras.vars[pname]['max']) == type(1) \
                   or type(Paras.vars[pname]['max']) == type(1.1):
                    max_user = np.array([Paras.vars[pname]['max']])
                    Paras.vars[pname]['max'] = max_user[:]
                else:
                    max_user = Paras.vars[pname]['max']         

        
        # - Only temporal variation allowed for the parameter / variation TIME
        if len(buf['dim_name']) == 1:    
            
            buf['dim_size'] = (tsize,)
            buf['dim_name'] = (tvar,)
            v_bg = np.zeros((tsize,), np.float64)
            v_fg = np.zeros((tsize,), np.float64)
            for i in range(tsize):
                np.put(v_bg,i,values_prior)
                np.put(v_fg,i,values_fg)
                
            
            # - value
            buf['value'] = v_fg
            buf['prior'] = v_bg
            vars[pname] = copy.deepcopy(buf)
            if pname in Paras.vars.keys():                              
                longname = np.zeros(buf['value'].shape).tolist()
                site_par = np.zeros(buf['value'].shape).tolist()
                if tsize > 1:
                    for it in range(tsize):
                        longname[it] = (pname+'-'+tstr+'%0'+str(tsize%10)+'i') %(it+1)
                    site_par[:] = Site.name
                else:
                    longname = [pname]
                    site_par = Site.name
                buf['longname'] = longname
                buf['site_par'] = site_par

            # - min & max
            if min_user == None:
                min_value = np.array(Paras_def.vars[pname]['min'])
            else:
                min_value = np.array(min_user)
            min_value = np.minimum.reduce(min_value.ravel())
            if max_user == None:
                max_value = np.array(Paras_def.vars[pname]['max'])
            else:
                max_value = np.array(max_user)
            max_value = np.maximum.reduce(max_value.ravel())

            min_value = np.reshape(min_value,(1,))
            max_value = np.reshape(max_value,(1,))

            if 'sigma' in Paras_def.vars[pname].keys():
                sig_value = np.array(Paras_def.vars[pname]['sigma'])
                sig_value = np.maximum.reduce(sig_value.ravel())
                sig_value = np.reshape(sig_value,(1,))
            
            # -- Once the parameter formatted, save the whole thing !
            vars[pname] = copy.deepcopy(buf)

        # - variation (REGION,TIME) or (PFT,TIME) or (PTS,TIME)
        
        elif len(buf['dim_name']) == 2:  

            if 'indice_region' in buf['dim_name'] and pname in Paras.vars.keys():

                map = Paras.vars[pname]['dims']['indice_region']-1
                nb_reg = len(Site.map['occupied_regions'][map])
                buf['dim_size'] = (nb_reg, tsize)
                buf['dim_name'] = ('indice_region',tvar)
                
                buf['map'] = map

                # - value
                v_bg = np.zeros((nb_reg*tsize), np.float64)
                v_fg = np.zeros((nb_reg*tsize), np.float64)
                for i in range(nb_reg*tsize): 
                    np.put(v_bg,i,values_prior)
                    np.put(v_fg,i,values_fg)
                v_bg = np.reshape(v_bg,(nb_reg,tsize))
                v_fg = np.reshape(v_fg,(nb_reg,tsize))

                # - min & max
                if min_user == None:
                    vmin = np.array(Paras_def.vars[pname]['min'])
                else:
                    vmin = np.array(min_user)
                if max_user == None:
                    vmax = np.array(Paras_def.vars[pname]['max'])
                else:
                    vmax = np.array(max_user)
                
                min_value  = np.zeros((nb_reg*tsize), np.float64)
                max_value  = np.zeros((nb_reg*tsize), np.float64)
                for i in range(nb_reg*tsize): 
                    np.put(min_value,i,vmin)
                    np.put(max_value,i,vmax)
                min_value = np.reshape(min_value,(nb_reg,tsize))
                max_value = np.reshape(max_value,(nb_reg,tsize))

                if 'sigma' in Paras_def.vars[pname].keys():
                    vsig = np.array(Paras_def.vars[pname]['sigma'])
                    sig_value  = np.zeros((nb_reg*tsize), np.float64)
                    for i in range(nb_reg*tsize): np.put(sig_value,i,vsig)
                    sig_value = np.reshape(sig_value,(nb_reg,tsize))

                # Identification name of each component (reg & time dims) and corresponding sites
                if pname in Paras.vars.keys():
                    longname = np.zeros(buf['value'].shape).tolist()
                    site_par = np.zeros(buf['value'].shape).tolist()
                    for ireg in range(nb_reg):
                        
                        # find the sites in this region
                        names = []
                        ireg2 = Site.map['occupied_regions'][map][ireg]
                        for isite in Site.site_ind[map][ireg2]:names.append(Site.name[isite])
                            
                        if tsize > 1:
                            for it in range(tsize):
                                longname[ireg][it] = (pname+'-REG%0'+str(nb_reg%10)+'i-'+tstr+'%0'+str(tsize%10)+'i') \
                                                     %(ireg2+1,it+1)
                            site_par[ireg][:] = names
                        else:
                            longname[ireg] = (pname+'-REG%0'+str(nb_reg%10)+'i') %(ireg2+1)
                            site_par[ireg] = names
                    buf['longname'] = longname
                    buf['site_par'] = site_par
                                    
            # (PFT, TIME)
            elif 'indice_pft' in buf['dim_name']:

                buf['dim_size'] = (vars['PFT_global']['dim_size'],tsize)
                buf['dim_name'] = ('indice_pft',tvar)

                # - value
                val_bg = np.take(values_prior, (vars['PFT_global']['value']-1).tolist(), axis = 0)
                val_fg = np.take(values_fg, (vars['PFT_global']['value']-1).tolist(), axis = 0)
                v_bg = np.zeros((vars['PFT_global']['dim_size'],tsize), np.float64)
                v_fg = np.zeros((vars['PFT_global']['dim_size'],tsize), np.float64)
                for it in range(tsize):
                    v_bg[:,it] = val_bg[:,0]
                    v_fg[:,it] = val_fg[:,0]

                # - min & max
                #DEBUG print pname, 'min : ',min_user
                #DEBUG print pname, 'max : ',max_user
                if min_user == None:
                    vmin = np.take(Paras_def.vars[pname]['min'], (np.array(vars['PFT_global']['value'])-1).tolist())
                else:
                    if len(min_user) != vars['PFT_global']['dim_size']:
                        sys.exit("ROUTINE prior prior.detprior_paras: the USER-DEFINED lower bound of variation  "+pname+" has not the correct PFT dimensions")
                    else:
                        vmin = np.array(min_user)
                if max_user == None:
                    vmax = np.take(Paras_def.vars[pname]['max'], (np.array(vars['PFT_global']['value'])-1).tolist())
                else:
                    if len(max_user) != vars['PFT_global']['dim_size']:
                        sys.exit("ROUTINE prior prior.detprior_paras: the USER-DEFINED upper bound of variation for "+pname+" has not the correct PFT dimensions")
                    else:
                        vmax = np.array(max_user)

                min_value = np.zeros((vars['PFT_global']['dim_size'],tsize), np.float64)
                max_value = np.zeros((vars['PFT_global']['dim_size'],tsize), np.float64)
                for it in range(tsize):
                    min_value[:,it] =  vmin[:]
                    max_value[:,it] =  vmax[:]

                if 'sigma' in Paras_def.vars[pname].keys():
                    vsig = np.take(Paras_def.vars[pname]['sigma'], (np.array(vars['PFT_global']['value'])-1).tolist())
                    sig_value = np.zeros((vars['PFT_global']['dim_size'],tsize), np.float64)
                    for it in range(tsize):  sig_value[:,it] =  vsig[:]

                # save long name with pft & time elements
                if pname in Paras.vars.keys():
                    longname = np.zeros(buf['value'].shape).tolist()
                    site_par = np.zeros(buf['value'].shape).tolist()
                    for ipft in range(vars['PFT_global']['dim_size']):

                        # find the sites having this pft
                        names=[]
                        for isite in range(Site.npts):
                            if vars['PFT_global']['value'][ipft] in Site.indice_pft[isite]:names.append(Site.name[isite])
                            
                        if tsize > 1:
                            for it in range(tsize):
                                longname[ipft][it] = (pname+'-PFT%02i-'+tstr+'%0'+str(tsize%10)+'i') \
                                                     %(vars['PFT_global']['value'][ipft],it+1)
                            site_par[ipft][:] = names
                        else:
                            longname[ipft] = (pname+'-PFT%02i') %(vars['PFT_global']['value'][ipft])
                            site_par[ipft] = names
                    buf['longname'] = longname
                    buf['site_par'] = site_par

            # (PTS, TIME)
            elif 'points_terre' in buf['dim_name']:
                buf['dim_size'] = (Site.npts,tsize)
                buf['dim_name'] = ('points_terre',tvar)

                # - value
                v_bg = np.zeros((Site.npts*tsize), np.float64)
                v_fg = np.zeros((Site.npts*tsize), np.float64)
                for i in range(Site.npts): 
                    for j in range(tsize):
                        np.put(v_bg,i*tsize+j,values_prior_site[i])
                        np.put(v_fg,i*tsize+j,values_fg_site[i])
                v_bg = np.reshape(v_bg,(Site.npts,tsize))
                v_fg = np.reshape(v_fg,(Site.npts,tsize))

                # -min/max
                if min_user == None:
                    vmin = np.array(Paras_def.vars[pname]['min'])
                else:
                    vmin = np.array(min_user)
                if max_user == None:
                    vmax = np.array(Paras_def.vars[pname]['max'])
                else:
                    vmax = np.array(max_user)

                min_value  = np.zeros((Site.npts*tsize), np.float64)
                max_value  = np.zeros((Site.npts*tsize), np.float64)
                for i in range(Site.npts*tsize): 
                    np.put(min_value,i,vmin)
                    np.put(max_value,i,vmax)
                min_value = np.reshape(min_value,(Site.npts,tsize))
                max_value = np.reshape(max_value,(Site.npts,tsize))

                if 'sigma' in Paras_def.vars[pname].keys():
                    vsig = np.array(Paras_def.vars[pname]['sigma'])
                    sig_value  = np.zeros((Site.npts*tsize), np.float64)
                    for i in range(Site.npts*tsize): np.put(sig_value,i,vsig)
                    sig_value = np.reshape(sig_value,(Site.npts,tsize))


                # save long name with pts & time elements
                if pname in Paras.vars.keys():
                    longname = np.zeros(Site.npts).tolist()
                    site_par = np.zeros(Site.npts).tolist()
                    for ipts in range(Site.npts):

                        # find the site at this point
                        names = [Site.name[ipts]]
                        
                        if tsize > 1:
                            for it in range(tsize):
                                longname[ipts][it] = (pname+'-PTS%0'+str(Site.npts%10)+'i_'+tstr+'%0'+str(tsize%10)+'i') \
                                                     %(ipts+1,it+1)
                            site_par[ipts][:] = names
                        else:
                            longname[ipts] = (pname+'-PTS%0'+str(Site.npts%10)+'i') %(ipts+1)
                            site_par[ipts] = names
                    buf['longname'] = longname
                    buf['site_par'] = site_par
            else:
                sys.exit('Houston, we ve got a problem with the 2 dimensions regarding '+pname+' !!')

            # -- Once the parameter formatted, save the whole thing !
            buf['value'] = v_fg
            buf['prior'] = v_bg
            vars[pname] = copy.deepcopy(buf)


        elif len(buf['dim_name']) == 3:  

            # variation (REGION,PFT,TIME)
            if 'indice_region' in buf['dim_name'] and 'indice_pft' in buf['dim_name'] \
               and pname in Paras.vars.keys(): 
                #print 'Parameter '+pname+': variation REGION,PFT,TIME'
                # Scale the dimensions using the maximum number of different PFTS in one region
                pfts = {}
                map = Paras.vars[pname]['dims']['indice_region']-1
                for ireg in Site.map['occupied_regions'][map]:
                    pfts[ireg] = len(vars['PFT']['value'][map][ireg])
                pfts_max = max(pfts)
                nb_reg = len(Site.map['occupied_regions'][map])
                buf['dim_size'] = (nb_reg,pfts_max,tsize)
                buf['dim_name'] = ('indice_region','indice_pft',tvar)
                buf['map'] = map

                v_bg={}
                v_fg={}
                min_value={}
                max_value={}
                if 'sigma' in Paras_def.vars[pname].keys(): sig_value={}
                longname = {}
                site_par = {}
                
                for ireg in Site.map['occupied_regions'][map]:
                    
                    # - value
                    val_bg = np.take(values_prior, (vars['PFT']['value'][map][ireg]-1).tolist(), axis = 0)
                    val_fg = np.take(values_fg, (vars['PFT']['value'][map][ireg]-1).tolist(), axis = 0)
                    v_bg[ireg] = np.zeros((pfts[ireg],tsize), np.float64)
                    v_fg[ireg] = np.zeros((pfts[ireg],tsize), np.float64)
                    for it in range(tsize):
                        v_bg[ireg][:,it] = val_bg[:,0]
                        v_fg[ireg][:,it] = val_fg[:,0]

                    # - min & max
                    if min_user == None:
                        vmin = np.take(Paras_def.vars[pname]['min'], (np.array(vars['PFT']['value'][map][ireg])-1).tolist())
                    else:
                        if len(min_user) != pfts[ireg]:
                            sys.exit("ROUTINE prior prior.detprior_paras: the USER-DEFINED lower bound of variation  "+pname+" has not the correct PFT dimensions")
                        else:
                            vmin = np.array(min_user)
                    if max_user == None:
                        vmax = np.take(Paras_def.vars[pname]['max'], (np.array(vars['PFT']['value'][map][ireg])-1).tolist())
                    else:
                        if len(max_user) != pfts[ireg]:
                            sys.exit("ROUTINE prior prior.detprior_paras: the USER-DEFINED upper bound of variation for "+pname+" has not the correct PFT dimensions")
                        else:
                            vmax = np.array(max_user)

                    min_value[ireg]  = np.zeros((pfts[ireg],tsize), np.float64)
                    max_value[ireg]  = np.zeros((pfts[ireg],tsize), np.float64)
                    for it in range(tsize):
                        min_value[ireg][:,it] =  vmin[:]
                        max_value[ireg][:,it] =  vmax[:]


                    if 'sigma' in Paras_def.vars[pname].keys():
                        vsig = np.take(Paras_def.vars[pname]['sigma'], (np.array(vars['PFT']['value'][map][ireg])-1).tolist())
                        sig_value[ireg]  = np.zeros((pfts[ireg],tsize), np.float64)
                        for it in range(tsize): sig_value[ireg][:,it] =  vsig[:]


                    # save long name with reg & pft & time elements
                    longname[ireg] = np.zeros(val_bg.shape).tolist()
                    site_par[ireg] = np.zeros(val_bg.shape).tolist()
                    for ipft in range(vars['PFT']['dim_size'][map][ireg]):
                        
                        # find the site in this region with this pft
                        names = []
                        for isite in Site.site_ind[map][ireg]:
                            if vars['PFT']['value'][map][ireg][ipft] in Site.indice_pft[isite]:names.append(Site.name[isite])
                            
                        if tsize > 1:
                            for it in range(tsize):
                                longname[ireg][ipft][it] = (pname+'-REG%02i-PFT%02i-'+tstr+'%0'+str(tsize%10)+'i') \
                                                           %(ireg+1,vars['PFT']['value'][map][ireg][ipft],it+1)
                                site_par[ireg][ipft][:] = names
                        else:
                            longname[ireg][ipft] = (pname+'-REG%02i-PFT%02i') \
                                                   %(ireg+1,vars['PFT']['value'][map][ireg][ipft])
                            site_par[ireg][ipft] = names

                buf['longname'] = longname
                buf['site_par'] = site_par
                buf['value'] = v_fg
                buf['prior'] = v_bg
                buf['3rd_loop'] = Site.map['occupied_regions'][map]

            # variation (PTS,PFT,TIME)
            elif 'points_terre' in buf['dim_name'] and 'indice_pft' in buf['dim_name']:

                # Scale the dimensions using the maximum number of different PFTS in one site
                pfts = []
                for isite in range(Site.npts): pfts.append(len(Site.indice_pft[isite]))
                pfts_max = max(pfts)
                buf['dim_size'] = (Site.npts,pfts_max,tsize)
                buf['dim_name'] = ('points_terre','indice_pft',tvar)
                
                # - value
                v_bg={}
                v_fg={}
                min_value={}
                max_value={}
                if 'sigma' in Paras_def.vars[pname].keys(): sig_value ={}
                longname = {}
                site_par = {}

                for isite in range(Site.npts):
                    
                    # - value
                    val_bg = np.take(values_prior_site[isite], (np.array(Site.indice_pft[isite], np.int32)-1).tolist(), axis = 0)
                    val_fg = np.take(values_fg_site[isite], (np.array(Site.indice_pft[isite], np.int32)-1).tolist(), axis = 0)
                    v_bg[isite] = np.zeros((pfts[isite],tsize), np.float64)
                    v_fg[isite] = np.zeros((pfts[isite],tsize), np.float64)
                    for it in range(tsize):
                        v_bg[isite][:,it] = val_bg[:,0]
                        v_fg[isite][:,it] = val_fg[:,0]

                    # - min & max
                    if min_user == None:
                        vmin = np.take(Paras_def.vars[pname]['min'], (np.array(Site.indice_pft[isite])-1).tolist())
                    else:
                        if len(min_user) != pfts[isite]:
                            sys.exit("ROUTINE prior prior.detprior_paras: the USER-DEFINED lower bound of variation  "+pname+" has not the correct PFT dimensions")
                        else:
                            vmin = np.array(min_user)
                    if max_user == None:
                        vmax = np.take(Paras_def.vars[pname]['max'], (np.array(Site.indice_pft[isite])-1).tolist())
                    else:
                        if len(max_user) != pfts[isite]:
                            sys.exit("ROUTINE prior prior.detprior_paras: the USER-DEFINED upper bound of variation for "+pname+" has not the correct PFT dimensions")
                        else:
                            vmax = np.array(max_user)

                    min_value[isite]  = np.zeros((pfts[isite],tsize), np.float64)
                    max_value[isite]  = np.zeros((pfts[isite],tsize), np.float64)

                    for it in range(tsize):
                        min_value[isite][:,it] =  vmin[:]
                        max_value[isite][:,it] =  vmax[:]

                    if 'sigma' in Paras_def.vars[pname].keys():
                        vsig = np.take(Paras_def.vars[pname]['sigma'], (np.array(Site.indice_pft[isite])-1).tolist())
                        sig_value[isite]  = np.zeros((pfts[isite],tsize), np.float64)
                        for it in range(tsize): sig_value[isite][:,it] =  vsig[:]


                    # save long name with reg & pft & time elements
                    longname[isite] = np.zeros(val_bg.shape).tolist()
                    site_par[isite] = np.zeros(val_bg.shape).tolist()
                    for ipft in range(len(Site.indice_pft[isite])):
                        
                        # find the site in this region with this pft
                        names = []
                        names.append(Site.name[isite])
                            
                        if tsize > 1:
                            for it in range(tsize):
                                longname[isite][ipft][it] = (pname+'-PTS%02i-PFT%02i-'+tstr+'%0'+str(tsize%10)+'i') \
                                                           %(isite+1,Site.indice_pft[isite][ipft],it+1)
                        else:
                            longname[isite][ipft] = (pname+'-PTS%02i-PFT%02i') %(isite+1,Site.indice_pft[isite][ipft])
                        site_par[isite][ipft][it] = Site.name[isite]


                buf['longname'] = longname
                buf['site_par'] = site_par
                buf['value'] = v_fg
                buf['prior'] = v_bg
                buf['3rd_loop'] = range(Site.npts)

            else:
                print buf['dim_name']
                sys.exit('Houston, we ve got a problem with the 3 dimensions regarding '+pname+' !!')

            # -- Once the parameter formatted, save the whole thing !
            vars[pname] = copy.deepcopy(buf)
            
        elif  len(buf['dim_name']) == 0:    # undefined parameter
            vars[pname]['dim_size'] = (1,)
            vars[pname]['dim_name'] = ('variation_fix',)
            vars[pname]['attr_name'] = ['-']
            vars[pname]['attr_value'] = ['-']
            vars[pname]['datatype'] = 'd'

            
        #- Add the flag opti / info_prior
        vars[pname]['opti'] = 'n'
        vars[pname]['info_prior'] = 'defaut'

        #--- Now if the parameter is defined optimizable by the user ---
        
        if pname in Paras.vars.keys():

            #print pname

            vars[pname]['info_prior'] = Paras.vars[pname]['info_prior']
            vars[pname]['opti'] = 'y'
            
            #- Add the keys min, max, sigma, and transfor
            vars[pname]['min'] = np.array(Paras.vars[pname]['min'], np.float64)
            vars[pname]['max'] = np.array(Paras.vars[pname]['max'], np.float64)
            vars[pname]['eps'] = np.array(Paras.vars[pname]['eps'], np.float64)
            ####vars[pname]['pc_eps'] = np.array(Paras.vars[pname]['pc_eps'], np.float64)
            
            vars[pname]['transform'] = Paras.vars[pname]['transform']
            vars[pname]['deriv']     = Paras.vars[pname]['deriv']

            #- Min & Max
            if len(buf['dim_name']) == 3:
                vars[pname]['min_opti'] = min_value
                vars[pname]['max_opti'] = max_value
            else:
                vars[pname]['min_opti'] = np.array(min_value)
                vars[pname]['max_opti'] = np.array(max_value)

            # - Sigma
            if 'sigma' not in  Paras_def.vars[pname]:

                if 'sigma_pc' in dir (Paras):
                    sigma_pc = Paras.sigma_pc
                else: 
                    sigma_pc = Paras_def.sigma_pc

                if 'div_sigma' in dir(Paras):
                    div_sigma = Paras.div_sigma
                else:
                    div_sigma = Paras_def.div_sigma

                    
                if 'sigma' not in Paras_def.vars[pname].keys():

                    # sigma for each PFT (used only to write ORCHIDEE input files)
                    mn = np.ma.array(Paras.vars[pname]['min'])
                    mx = np.ma.array(Paras.vars[pname]['max'])
                    mn = np.ma.masked_values(mn, Config.missval[0]);
                    mn = np.ma.masked_values(mn, Config.missval[1]) 
                    mx = np.ma.masked_values(mx, Config.missval[0]);
                    mx = np.ma.masked_values(mx, Config.missval[1])
                    #if pname in Paras_def.centered_param:
                    sigma = (mx-mn)*sigma_pc/100
                    #else:
                    #sigma = values_prior.ravel()-mn
                    #if type(sigma) != type(np.ma.ones(1)): sigma=np.ma.reshape(sigma,(1,))
                    vars[pname]['sigma_pft'] = sigma.filled(Config.missval[0])#/div_sigma

                    # sigma actually used in ORCHIS
                    if len(buf['dim_name']) == 3:
                        vars[pname]['sigma']={}
                        for ireg in vars[pname]['3rd_loop']:
                            mn_opti = np.ma.array(min_value[ireg])
                            mx_opti = np.ma.array(max_value[ireg])
                            mn_opti = np.ma.masked_values(mn_opti, Config.missval[0]);
                            mn_opti = np.ma.masked_values(mn_opti, Config.missval[1]) 
                            mx_opti = np.ma.masked_values(mx_opti, Config.missval[0]);
                            mx_opti = np.ma.masked_values(mx_opti, Config.missval[1])
                            #if pname in Paras_def.centered_param:
                            sigma = (mx_opti-mn_opti)*sigma_pc/100
                            #else:
                            #sigma = np.array(buf['prior'][ireg])-mn_opti

                            sigma = sigma.filled(Config.missval[0])
                            vars[pname]['sigma'][ireg] = (sigma.ravel())/div_sigma

                    else:
                        mn_opti = np.ma.array(min_value)
                        mx_opti = np.ma.array(max_value)
                        mn_opti = np.ma.masked_values(mn_opti, Config.missval[0]);
                        mn_opti = np.ma.masked_values(mn_opti, Config.missval[1]) 
                        mx_opti = np.ma.masked_values(mx_opti, Config.missval[0]);
                        mx_opti = np.ma.masked_values(mx_opti, Config.missval[1])
                        #if pname in Paras_def.centered_param:
                        sigma = (mx_opti-mn_opti)*sigma_pc/100
                        #else:
                        #sigma = np.array(buf['prior'])-mn_opti
                            
                        sigma = sigma.filled(Config.missval[0])
                        vars[pname]['sigma'] = (sigma.ravel())#/div_sigma
            
            else:

                vars[pname]['sigma_pft'] = copy.deepcopy(Paras_def.vars[pname]['sigma'])
                    
                # sigma actually used in ORCHIS
                if len(buf['dim_name']) == 3:
                    vars[pname]['sigma']={}
                    for ireg in vars[pname]['3rd_loop']:
                        sigma = np.ma.array(sig_value[ireg])
                        sigma = np.ma.masked_values(sigma, Config.missval[0]);
                        sigma = np.ma.masked_values(sigma, Config.missval[1]);
                        sigma = sigma.filled(Config.missval[0])
                        vars[pname]['sigma'][ireg] = sigma.ravel()
                else:
                    sigma = np.ma.array(sig_value)
                    sigma = np.ma.masked_values(sigma, Config.missval[0]);
                    sigma = np.ma.masked_values(sigma, Config.missval[1]);
                    sigma = sigma.filled(Config.missval[0])
                    vars[pname]['sigma'] = sigma.ravel()

            # - Check that the parameter value is not out of bounds
            if len(buf['dim_name']) == 3:
                for ireg in vars[pname]['3rd_loop']:
                    dif = vars[pname]['value'][ireg]-vars[pname]['min_opti'][ireg]
                    if np.minimum.reduce(dif.ravel()) < 0:
                        sys.exit("ROUTINE prior.detprior_paras: in region "+str(ireg)+"a value of "+\
                                 "the USER-DEFINED lower bound of variation for "+pname+" is above the prior value")
                    dif = vars[pname]['max_opti'][ireg]-vars[pname]['value'][ireg]
                    if np.minimum.reduce(dif.ravel()) < 0:
                        sys.exit("ROUTINE prior.detprior_paras: in region "+str(ireg)+"a value of "+\
                                 "the USER-DEFINED upper bound of variation for "+pname+" is below the prior value")
            else :
                dif = vars[pname]['value']-vars[pname]['min_opti']
                if np.minimum.reduce(dif.ravel()) < 0:
                    sys.exit("ROUTINE prior.detprior_paras: a value of "+\
                             "the USER-DEFINED lower bound of variation for "+pname+" is above the prior value")
                dif = vars[pname]['max_opti']-vars[pname]['value']
                if np.minimum.reduce(dif.ravel()) < 0:
                    sys.exit("ROUTINE prior.detprior_paras: a value of "+\
                             "the USER-DEFINED upper bound of variation for "+pname+" is below the prior value")

            del(dif)

            #print pname
            #print vars[pname]['sigma']

            #- Just check if there is a consistency between the default dimension and the user defined one
            # if Paras.vars[pname]['dims']['indice_region'] >= 1 and 'indice_region' not in buf['dim_name']:
            #     sys.exit('ROUTINE prior.detprior_paras: The parameter '+pname+ ' has been attributed a region dimension, which is not allowed')

            # if Paras.vars[pname]['dims']['indice_pft'] == 1 and 'indice_pft' not in buf['dim_name']:
            #     sys.exit('ROUTINE prior.detprior_paras: The parameter '+pname+ ' has been attributed a PFT dimension, which is not allowed')

            # if Paras.vars[pname]['dims']['points_terre'] == 1 and 'points_terre' not in buf['dim_name']:
            #     sys.exit('ROUTINE prior.detprior_paras: The parameter '+pname+ ' has been attributed a site dimension, which is not allowed')

            #- Some Prior value is provided
            if Paras.vars[pname]['info_prior'] == 'user':
                if (Paras.vars[pname]['value']).shape == vars[pname]['dim_size']:
                    vars[pname]['value'] = np.array(Paras.vars[pname]['value'], np.float64)
                else:
                    
#                    print (Paras.vars[pname]['value']).shape
#                    print buf['dim_size']
                    logfile.write(str((Paras.vars[pname]['value']).shape) + '\n')
                    logfile.write(str(vars[pname]['dim_size']) + '\n')
                    logfile.write('ROUTINE prior.detprior_paras: The prior value array of the parameter '+pname+ \
                                     ' does not comply with the dimensions size')
                    
                    sys.exit('ROUTINE prior.detprior_paras: The prior value array of the parameter '+pname+ \
                             ' does not comply with the dimensions size')
              
    #-------------------------------------------------------------------------------------------    
    # --- Create a subset of variables usable for the separate runs of orchidee on each site ---
    #-------------------------------------------------------------------------------------------
    vars_site={}
    
    for isite in range(Site.npts):

        vars_site[isite]=copy.deepcopy(vars)


        vars_site[isite]['PFT']['dim_size'] = len(Site.indice_pft[isite])
        vars_site[isite]['PFT']['value'] = Site.indice_pft[isite]

        for idim in range(len(dims_site[isite])):

            if idim >= len(dims_site[isite]): idim = len(dims_site[isite])-1
            dimname = dims_site[isite][idim]['name']

            if dimname == 'indice_region' : dims_site[isite].pop(idim)
            if dimname == 'points_terre': dims_site[isite][idim]['size'] = 1
            if dimname == 'indice_pft': dims_site[isite][idim]['size'] = len(Site.indice_pft[isite])
            if dimname == 'variation_day': dims_site[isite][idim]['size'] = Site.time[isite]['njours']
            if dimname == 'variation_week': dims_site[isite][idim]['size'] = Site.time[isite]['nsemaines']
            if dimname == 'variation_month': dims_site[isite][idim]['size'] = Site.time[isite]['nmois']
            if dimname == 'variation_year': dims_site[isite][idim]['size'] = Site.time[isite]['nannees']
        
        for pname in varnames:

            #print pname

            buf = vars_site[isite][pname]
            buf2 = list(buf['dim_name'])
            del(buf['prior'])


            #print buf['dim_size'], buf['dim_name'], buf['value']

            if 'indice_pft' in buf['dim_name'] :
                    
                value = np.take(vars_fg_site[isite][pname]['value'], (np.array(Site.indice_pft[isite], np.int32)-1).tolist(), axis = 0)
                nvalue = np.zeros((len(Site.indice_pft[isite]),tsize), np.float64)
                for it in range(tsize): nvalue[:,it] = value[:,0]
                buf['value'] = nvalue
                buf['dim_size']=(len(Site.indice_pft[isite]),tsize)
                if 'indice_region' in buf['dim_name']: buf2.remove('indice_region')
                if 'points_terre' in buf['dim_name']: buf2.remove('points_terre')

                if pname in Paras.vars.keys():
                    buf['sigma'] = np.take(buf['sigma_pft'], (np.array(Site.indice_pft[isite], np.int32)-1).tolist(), axis = 0)
                    buf['min'] = np.take(buf['min'], (np.array(Site.indice_pft[isite], np.int32)-1).tolist(), axis = 0)
                    buf['max'] = np.take(buf['max'], (np.array(Site.indice_pft[isite], np.int32)-1).tolist(), axis = 0)

                            
            elif 'indice_region' in buf['dim_name'] :
                buf2.remove('indice_region')
                buf2.insert(0,'points_terre')
                buf['value'] = np.array(vars_fg_site[isite][pname]['value'],np.float64)
                buf['dim_size'] = (1,tsize)
                if pname in Paras.vars.keys():
                    buf['sigma'] = buf['sigma_pft']
                    
            elif 'points_terre' in buf['dim_name'] :
                nvalue = np.array(buf['value'][isite],np.float64)
                buf['value'] = nvalue
                buf['dim_size'] = (1,tsize)
                if pname in Paras.vars.keys():
                    buf['sigma'] = buf['sigma_pft']

            if 'longname' in buf:del(buf['longname'])
            if 'site_par' in buf:del(buf['site_par'])
            if 'min_opti' in buf:del(buf['min_opti'])
            if 'max_opti' in buf:del(buf['max_opti'])
            if 'sigma_pft' in buf:del(buf['sigma_pft'])
            if '3rd_loop' in buf:del(buf['3rd_loop'])
            if 'map' in buf:del(buf['map'])
                
            buf['dim_name'] = copy.deepcopy(tuple(buf2))
            vars_site[isite][pname] = copy.deepcopy(buf)


            #print buf['dim_size'], buf['dim_name'], buf['value']

    # ---------------------------------------------------------------------------------
    # --- Return the final dictionnary containing the informations on the variables ---
    # ---------------------------------------------------------------------------------

    class VarInfo:
        def __init__(self, vars, dims):
            self.vars = vars
            self.gattr = {'name': 'date','value':strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())}
            self.dims = dims

    Res = VarInfo(vars, dims)
    
    Res_site={}
    
    for isite in range(Site.npts):
        Res_site[isite] = VarInfo(vars_site[isite], dims_site[isite])


    return Res, Res_site
            
# END detprior_paras
# ==============================================================================


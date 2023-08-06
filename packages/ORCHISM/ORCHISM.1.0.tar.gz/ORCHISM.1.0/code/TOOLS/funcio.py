#*******************************************************************************
# MODULE	: FUNCIO
# AUTHORS	: C. BACOUR, S. KUPPEL & T. THUM
# CREATION	: 07/2007
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
Inputs/Outputs modules for ORCHIS
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import copy, glob, sys
import numpy as np
from time import localtime, strftime
from orchis_config import Paras_def, Config

#from TOOLS import various
import various,io



# ==============================================================================
# Get yearly means for the target variable
# T. Thum
# ------------------------------------------------------------------------------
def flux_yearly(name,
                data,
                ndays,
                nyears,  
                time_step,
                time_counter
                ):


    ndata_year = len(data) / (nyears)  # how many data values in a year
    val_yearly = np.zeros(nyears, np.float64) 
    time_counter_yearly = np.zeros(nyears, np.float64) 

    # ---
    # --- Compute yearly fluxes
    # ---
    
    for i in range(nyears):

        indices = np.arange(i*ndata_year,(i+1)*ndata_year,1,np.int)
#        print 'DEBUG : indices ',indices
        buf = np.take(data,indices, axis = 0)
        # deal with missing values      
        buf = np.ma.masked_where(buf <= Config.missval[0], buf)

        mean_yearly = np.ma.filled(np.ma.average(buf), Config.missval[0])

        np.put(val_yearly,i,mean_yearly)

                    
    nobs_yearly = 1
    time_counter = time_counter_yearly      
    
    time_step = np.array(365.*24.*3600., np.float64)

#    print 'val_yearly : ', val_yearly
#    raw_input('pause')

    indices =  np.where(val_yearly == Config.missval[0], Config.missval[0], np.arange(len(val_yearly)) )
    mask = np.ma.masked_equal(indices, Config.missval[0])
    indices = mask.compressed().tolist()
    
    # ---
    # --- Return
    # ---
    return val_yearly, time_counter, time_step, nobs_yearly, indices
 
        
    # -- Fin
# ==============================================================================



# ==============================================================================
# Get daily & diurnal flux data
# - daily : Mean for NEEt, Qh, Qle and Rn, computed between prescribed
#           times t_i and t_e
#
# - diurnal : 
# ------------------------------------------------------------------------------
def flux_daily_diurnal(name,
                       data,
                       ndays,
                       time_step,
                       time_counter,
                       tdaily, 
                       get_diurnal    = False,
                       get_daily      = False,
                       diurnal_length = None,
                       diurnal_start  = None,
                       test_smooth = None,
                       detect_gapf = False,
                       ind_gap     = None):


    ndata_day = len(data) / (ndays) # ndays <=> number of days of the time series
   
    
    # ---
    # --- Compute daily fluxes
    # ---
    
    time_counter_daily = np.zeros(ndays, np.float64)
    val_daily = np.zeros(ndays, np.float64)
    val2_daily = np.zeros(ndays, np.float64)
    val_diurnal = np.zeros(1)
    
    for i in range(ndays):

        indices = np.arange(i*ndata_day,(i+1)*ndata_day,1, np.int)
        buf = np.take(data,indices, axis = 0)

        if detect_gapf==True:
            buf2 = np.take(ind_gap,indices, axis = 0)
            #buf2 = np.ma.masked_where(buf <= Config.missval[0], buf2)

        # deal with missing values      
        buf = np.ma.masked_where(buf <= Config.missval[0], buf)
        time_counter_daily[i] = time_counter[indices[0]]
        heure = (time_counter[indices[0]:indices[-1]+1])/3600. % 24
        heure_masked = np.ma.masked_outside(heure, tdaily[0], tdaily[1])
        buf_daily = np.ma.masked_where( heure_masked.mask == True, buf)

        # mean
        mean_daily = np.ma.filled(np.ma.average(buf_daily), Config.missval[0])

        # mean fraction of gap-filled values
        if detect_gapf==True: 
            buf2_daily = np.ma.masked_where( heure_masked.mask == True, buf2)
            mean2_daily = np.array(np.ma.filled(np.ma.average(buf2_daily)))#, Config.missval[0]))
            np.put(val2_daily,i,mean2_daily)
        
        # account for daily means if there are more than 80% of available data
        # if buf_daily.count() < 0.8*len(buf_daily) and name[0:6] != 'fAPARt':
        # if buf_daily.count() < 0.8*heure_masked.count() and name[0:6] != 'fAPARt':
        if buf_daily.count() < 0.8*heure_masked.count():
            vdaily = np.array(Config.missval[0], np.float64)
        else:
            vdaily = np.array(mean_daily, np.float64)
            
        np.put(val_daily,i,vdaily)
            
    # --- NEE case
    if 'NEE' in name or 'GPP' in name or 'TER' in name or 'Resp' in name: 
        fac_cor_CO2 = np.array((tdaily[1]-tdaily[0])*3600.)/time_step # correct by the number of obs used to compute daily means
        val_daily = val_daily *  fac_cor_CO2 
        # raw_input( 'correction factor for DAILY NEE = '+str(fac_cor_CO2))
        
    nobs_daily = heure_masked.count() # number of measurements accounted for the computation of daily means

    time_counter = time_counter_daily

        
    # ---
    # --- Smoothing of the daily fluxes 
    # ---
    if test_smooth != None:
        if test_smooth == 'smooth' or test_smooth == 'smoothmaw' or test_smooth == 'smoothmav':
            val_daily = various.smooth_square(val_daily,Config.smooth_len_square_filter) 
            #print 'Daily SMOOTHING activated for ',name, ' using Moving Average Window'
        elif test_smooth == 'smoothgauss':
            val_daily = various.smooth_gaussian(val_daily,Config.smooth_gauss_filter) 
            #print 'Daily SMOOTHING activated for ',name, ' using Gaussian window'

        

    # ---
    # --- Compute diurnal fluxes : in fact diurnal cycle - daily means
    # ---
    if get_diurnal == True:

        val_diurnal = np.zeros(( len(diurnal_length), ndata_day), np.float64)

        # visualisation
        #import matplotlib.pyplot as plt

                       
        for icycle in range(len(diurnal_start)):


            j = diurnal_start[icycle]
            length = diurnal_length[icycle]
            
            buf_cycle = np.ma.zeros((length,ndata_day), np.float64)

            for ijour in range(length):
                indices = range((j+ijour)*ndata_day,(j+ijour+1)*ndata_day,1)
               
                buf = np.take(data,indices, axis = 0)
                buf = np.ma.masked_where(buf <= Config.missval[0], buf) # deal with missing values

                fac = 1
                if 'NEE' in name  or 'GPP' in name or 'TER' in name or 'Resp' in name:
                    fac = 1/fac_cor_CO2
                
                if val_daily[j+ijour] not in Config.missval:
                    buf_cycle[ijour,:] = buf - val_daily[j+ijour]*fac
                else:
                    buf_cycle[ijour,:] = np.ma.masked                  

                ###buf_cycle[ijour,:] = buf - val_daily[j+ijour]        # substract the daily mean

                # remarque : il semble que Diego utilise en fait :
                # buf_cycle[ijour,:] = buf - Mobs - val_daily[j+ijour]
                # avec Mobs = np.ma.average(obs sur icycle)
                
            mean_diurnal = np.ma.filled(np.ma.average(buf_cycle, axis = 0), Config.missval[0])

            
            # account for diurnal means if there are more than 80% of available data
            if buf_cycle[ijour,:].count() < 0.8*ndata_day: 
                vdiurnal = np.array(Config.missval[0], np.float64)
            else:
                vdiurnal = np.array(mean_diurnal, np.float64)

            ind = np.arange(icycle*ndata_day,(icycle+1)*ndata_day,1).tolist()
            np.put(val_diurnal,[ind],vdiurnal)


        nobs_diurnal = np.product(val_diurnal.shape)
        
        # visualisation
        
        #plt.plot(np.arange(0,ndata_day)+np.zeros(val_diurnal.shape), val_diurnal)
        #plt.show()
        ###raw_input('pause funcio')
        
        #for icycle in range(len(diurnal_start)):
        #    x.plot(np.arange(0,ndata_day), val_diurnal[icycle,:],'default','xvsy')
        #    print icycle
        #raw_input('pause funcio')
                  


    # --- Set the time step
    if get_diurnal == False: # if daily only => tstep = one day
        time_step = np.array(24.*3600., np.float64)
    else:                    # if diurnal, keep the tstep of the diurnal sampling
        time_step = time_step

    # --- Indices
    if get_daily == True:
        value = val_daily
    if get_diurnal == True:
        value = val_diurnal        
    indices =  np.where(value == Config.missval[0], Config.missval[0], np.arange(len(value)) ) #### NUMPY
    mask = np.ma.masked_equal(indices, Config.missval[0])
    indices = mask.compressed().tolist()
            
    # ---
    # --- Return
    # ---
    ###return val_daily, val_diurnal, time_counter, time_step, nobs_daily
    if get_daily == True:
        return val_daily, time_counter, time_step, nobs_daily, indices, val2_daily
    if get_diurnal == True:
        return val_diurnal, time_counter, time_step, nobs_diurnal, indices
 
        
    # -- Fin
# ==============================================================================




# ==============================================================================
# Separate daytime and nightime observations
# - daytime data are associated to the standard obs[name] variable
# - nighttime data are associated to the standard obs[name+'_night'] variable
# ------------------------------------------------------------------------------
def flux_day_vs_night(isite,
                      name,
                      data,
                      ndays,
                      time_counter,
                      tdaytime,
                      tnighttime,
                      detect_gapf = False,
                      ind_gap = None):
  
  
    ndata_day = len(data) / (ndays) # ndays <=> number of days of the time series

    
    # ---
    # --- Compute day mean fluxes
    # ---
    values = np.zeros(ndays, np.float64)
    values2 = np.zeros(ndays, np.float64)


    for i in range(ndays):


        indices = np.arange(i*ndata_day,(i+1)*ndata_day,1, np.int32)       
        buf = np.take(data, indices, axis = 0)

        if detect_gapf==True:
            buf2 = np.take(ind_gap,indices, axis = 0)
            #buf2 = np.ma.masked_where(buf <= Config.missval[0], buf2)            

        # deal with missing values      
        buf = np.ma.masked_where(buf <= Config.missval[0], buf)
        swdown    = np.take(Config.SWdown[isite], indices, axis = 0)

        if Config.dn_diff == 'SWdown':
            swdown    = np.take(Config.SWdown[isite], indices, axis = 0)
            ind_day   = np.ma.masked_where(swdown <=Config.SWdown_threshold, indices)
            ind_night = np.ma.masked_where(swdown >Config.SWdown_threshold , indices)
        else:
            hour      = (time_counter[indices[0]:indices[-1]+1])/3600. % 24
            ind_day   = np.ma.masked_outside(hour, tdaytime[0], tdaytime[1])
            ind_night = np.ma.masked_outside(hour, tnighttime[0], tnighttime[1])


        if '_night' not in name: # day
            #indices2   = np.ma.masked_where(swdown <=Config.SWdown_threshold, indices)
            #val  = np.ma.masked_where(swdown <=Config.SWdown_threshold, swdown)
            val  = np.ma.masked_where(ind_day.mask,buf)
            nobs = ind_day.count() 

            if detect_gapf==True: val2=np.ma.masked_where(ind_day.mask,buf2)

        else:                    #night
            #indices2 = np.ma.masked_where(swdown >Config.SWdown_threshold , indices)
            #val = np.ma.masked_where(swdown >Config.SWdown_threshold , buf)
            val = np.ma.masked_where(ind_night.mask,buf)
            nobs = ind_night.count()

            if detect_gapf==True: val2=np.ma.masked_where(ind_night.mask,buf2)                        
        #nobs   = indices2.count()
        

        # --- Variable expressed as a function of time
        fac_cor = 1
        if 'NEE' in name or 'GPP' in name or 'TER' in name or 'Resp' in name: 
            fac_cor   = ndata_day
        
        # account for means if there are more than 80% of available data
        if nobs == 0 or val.count() < 0.8*nobs :
            mean_val = np.array(Config.missval[0], np.float64)
        else:
            mean_val = np.ma.filled(np.ma.average(val), Config.missval[0]) * fac_cor

        np.put(values,i,mean_val)

        # mean fraction of gap-filled values
        if detect_gapf==True: 
            mean2_val = np.ma.filled(np.ma.average(val2))#, Config.missval[0])
            np.put(values2,i,mean2_val)

    # ---
    # --- Indices
    # ---
    indices =  np.where(values == Config.missval[0], Config.missval[0], np.arange(ndays))
    mask = np.ma.masked_equal(indices, Config.missval[0])
    indices = mask.compressed().tolist()

            
    # ---
    # --- Return
    # ---
    time_step = np.array(24.*3600., np.float64)

    return values, indices, time_step, values2
  
        
# -- END flux_day_vs_night
# ==============================================================================





# ==============================================================================
# Normalize data (obs & sim) between Min & Max
#
# The processing is performed on the common available data between obs and sim
# (i.e. non flagged data). Therefore the call to the routine can not be made
# in get_data (the processing of which implies only 1 NetCDF file)
#
# ------------------------------------------------------------------------------
def normalize_data(data, vars_info, logfile,
                   name = None, case = None,
                   tempo_res = None,
                   indices_obs = None,
                   indices_sim = None):

    
    nameobs =(name.split('_'))[0]

    
    # - Save max & min of each variable
    #if 'bound_'+case not in vars_info[name].keys():
    if 'bound_'+case not in vars_info[nameobs].keys():
        vars_info[nameobs]['bound_'+case] = {}                    
        vars_info[nameobs]['bound_'+case]['min'] = -9999
        vars_info[nameobs]['bound_'+case]['max'] = -9999

    buf = tempo_res.split('_')
    ind = buf.index('normalize')
    min_pc = int(buf[ind+1])
    max_pc = int(buf[ind+2])

    # - account only for intersection of the two indices
    indices = list(set(indices_obs).intersection(set(indices_sim)))
    indices.sort()   
    values = data[:]
    values = np.take(values, indices, axis = 0)

    # differences
    ## indices = [i for i in indices_obs+indices_sim if i not in indices_obs or i not in indices_sim] # difference. set() marche pa
##     values = data[:]
##     np.put(values,np.array(indices),  -9999.)
    
    if (name.split('_'))[-1] != 'tl' :
        [vmin, vmax] = various.detminmax(values, min_pc, max_pc, percentile = True)
        vars_info[nameobs]['bound_'+case]['min'] = vmin
        vars_info[nameobs]['bound_'+case]['max'] = vmax
        print '    +++ Normalization of '+name+ ' between '+str(min_pc)+ \
              '% and '+str(max_pc)+ '% of its range of variation =['+str(vmin)+';'+str(vmax)+']'
        logfile.write('    +++ Normalization of '+name+' between '+str(min_pc)+ \
                      '% and '+str(max_pc)+ '% of its range of variation = ['+str(vmin)+';'+str(vmax)+']\n')
        
        data = various.normalize(data,  vmin, vmax, logfile)

    # normalization for the TL variable
    else:
        vmax = vars_info[nameobs]['bound_'+case]['max']
        vmin = vars_info[nameobs]['bound_'+case]['min']
        print '+++ Normalization of the TL variable of '+nameobs+ ' between ['+ str(vmin)+';'+str(vmax)+']'
        logfile.write('\n+++ Normalization of the TL variable of '+nameobs+ ' between ['+ str(vmin)+';'+str(vmax)+']\n')        
        data = data * 1./(vmax-vmin)

    # - Return
    return data
# END normalize
# ==============================================================================




# ==============================================================================
# Get the data from a single NetCDF file
#
# Return a dictionnary containing the value of the observation variables
# res = {'NEE':value, 'Qh': value, \
#        'Qle': value, 'Rn': value, \
#        'fAPARt': value}
#
# if no data : value = 1e20
#
# Remarks: 
# - for one given site, the same number of days where observation are accounted
#   for must be prescribed for each variable
#
# ------------------------------------------------------------------------------
def get_data(fics_info, 
             isite,
             logfile,
             read_tl     = None, 
             ndays       = None,
             nyears      = None,
             tdaily      = None,
             tdaytime    = None,
             tnighttime  = None,
             diurnal_length    = None,
             diurnal_start     = None,
             vars_info         = None,           
             detect_gapf       = False,
             case              = None# obs or sim
             ):
    


    obs = {}


    # -- Loop on files --
    # -------------------
    nfic = fics_info.keys()
    obs['fic'] = {}
    
    for ific in nfic:

        ficname = fics_info[ific]['name']
        obs_name = fics_info[ific]['vars']

        # -- Initialize dictionnary --
        # ----------------------------
        obs['fic'][ific] = {}
        obs['fic'][ific]['name'] = ficname
        obs['fic'][ific]['time_counter']        = Config.missval[0]
        obs['fic'][ific]['time_counter_daily']  = Config.missval[0]
        obs['fic'][ific]['time_step']           = Config.missval[0]
        obs['fic'][ific]['nobs_daily']          = Config.missval[0]
        obs['fic'][ific]['units_Cflux']         = Config.missval[0]

        
        if len(glob.glob(ficname))==0: sys.exit('# The observation file does not exist : \n ' +ficname)

    
        # need to read flux_tl data
        if read_tl != None:
            buf = obs_name[:]       
            for name in obs_name:  buf.append(name+'_tl')
            obs_name = buf[:]

        for name in obs_name:
            obs[name] = Config.missval[0]
        
    
        # -- Read data --
        # ---------------
        data = io.readnc(ficname)
        data = data[0]


        # - obs       
        for name in obs_name:
            nname = name.split('_tl')[0]
            time_counter_name = vars_info[nname]['time_counter_'+case]
            name2read = vars_info[nname]['name_'+case]
            vname = name2read
            ### if '_tl' in name: vname=vname+'_tl'
            if (name.split('_'))[-1] == 'tl' : vname=vname+'_tl'
            obs[name]  = np.array(data[vname]['value'], np.float64)
            # DEBUG
            # print 
            # print 
            # print 
            # print '--- Lecture  ---'
            # print name,vname,np.average(data[vname]['value'].ravel()), np.minimum.reduce(data[vname]['value'].ravel()),\
            #     np.maximum.reduce(data[vname]['value'].ravel())


            # Gestion of  missing values = 1+e20 (not correctly accounted for by ScientificIO)
            obs[name] = np.where(obs[name] <= Config.missval[1], obs[name], Config.missval[0])

            # (If activated) meta info to dectect gap-filled values for observations
            if (name.split('_'))[-1] != 'tl' and detect_gapf == True:
                obs[name+'_fqc'] = np.array(data[vname+'_fqc']['value'], np.float64)
                obs[name+'_fqc'] = np.where(obs[name+'_fqc'] <= Config.missval[1], obs[name+'_fqc'], 0)
                obs[name+'_fqc'] = np.array(np.where( obs[name+'_fqc']>0,1, obs[name+'_fqc']))


        obs['fic'][ific]['time_counter']  = np.array(data[time_counter_name]['value'], np.float64)

        # units of C fluxes
        if 'NEEt' in obs_name:
            if 'units' in data['NEEt']['attr_name']:
                idx=data['NEEt']['attr_name'].index('units')
                obs['fic'][ific]['units_Cflux'] = data['NEEt']['attr_value'][idx]
        if 'GPPt' in obs_name:
            if 'units' in data['GPPt']['attr_name']:
                idx=data['GPPt']['attr_name'].index('units')
                obs['fic'][ific]['units_Cflux'] = data['GPPt']['attr_value'][idx]
        if 'TERt' in obs_name:
            if 'units' in data['TERt']['attr_name']:
                idx=data['TERt']['attr_name'].index('units')
                obs['fic'][ific]['units_Cflux'] = data['TERt']['attr_value'][idx]
        if 'Resp_ht' in obs_name:
            if 'units' in data['Resp_ht']['attr_name']:
                idx=data['Resp_ht']['attr_name'].index('units')
                obs['fic'][ific]['units_Cflux'] = data['Resp_ht']['attr_value'][idx]
        if 'Resp_gt' in obs_name:
            if 'units' in data['Resp_gt']['attr_name']:
                idx=data['Resp_gt']['attr_name'].index('units')
                obs['fic'][ific]['units_Cflux'] = data['Resp_gt']['attr_value'][idx]
        if 'Resp_mt' in obs_name:
            if 'units' in data['Resp_mt']['attr_name']:
                idx=data['Resp_mt']['attr_name'].index('units')
                obs['fic'][ific]['units_Cflux'] = data['Resp_mt']['attr_value'][idx]
        
        # because ORCHIDEE of ORCHIDEE time_counter that starts at an unpredictable date, set starting
        # date at 0!
        offset = obs['fic'][ific]['time_counter'][0] 
        obs['fic'][ific]['time_counter']  = obs['fic'][ific]['time_counter']-offset
        time_counter = obs['fic'][ific]['time_counter'] 

        # - time step / used for computation of daily / diurnal data            
        time_step = None #undefined
        if 'interval_write' in data[name2read]['attr_name']:
            idx = data[name2read]['attr_name'].index('interval_write')
            time_step = data[name2read]['attr_value'][idx]
            if type(time_step) == type([]):
                if 'day' in time_step and '/d' in obs['fic'][ific]['units_Cflux']:
                    time_step = int(time_step.split(' ')[0])*24*3600.                    
                else:
                    sys.exit(' Error in FUNCIO.PY : time step not recognized' )
            else:
                obs['fic'][ific]['time_step'] = time_step
            

        
        # - C fluxes in gC/m2/s
        #if 'NEEt' in obs_name : obs['NEEt'] = obs['NEEt']*obs['fic'][ific]['time_step']
        #if 'NEEt_tl' in obs_name : obs['NEEt_tl'] = obs['NEEt_tl']*obs['fic'][ific]['time_step']
        for name in obs_name:
            if 'NEEt' in name or 'GPPt' in name or 'TERt' in name \
                     or 'Resp_ht' in name or 'Resp_mt' in name or 'Resp_gt' in name:
                #print "UNITS =",obs['fic'][ific]['units_Cflux']
                if '/s' in obs['fic'][ific]['units_Cflux']:
                    # print "NEEt exprime en gC/m2/s"
                    obs[name] = np.where(obs[name] == Config.missval[0], Config.missval[0], obs[name]*time_step)
##                    print 'changement NEE',np.average(obs[name].ravel()), np.minimum.reduce(obs[name].ravel()),\
##                        np.maximum.reduce(obs[name].ravel())
##                    print "time step", time_step
##                    raw_input('pause')
                #else:
                    #print "NEEt exprime en gC/m2/j"
                    
                ###obs[name] = obs[name]*time_step
                ###print ' NEE = NEE*time_step avec time_step = ',time_step
        #if 'NEEt_tl' in obs_name : obs['NEEt_tl'] = obs['NEEt_tl']*time_step
        


        # -- Data processing --
        # ---------------------
        nobs_daily = None
        
        
        # Loop on parameters  
        for name in obs_name:

            nname = name.split('_tl')[0]
            
            test_smooth = None
            tempo_res = vars_info[nname]['processing_'+case]
       
            # -- Reshape flux data --
            if obs[name].all() != Config.missval[0]:               
                obs[name] = np.reshape(obs[name],(len(obs[name].ravel()),))
                if (name.split('_'))[-1] != 'tl' and detect_gapf == True:
                    obs[name+'_fqc'] = np.reshape(obs[name+'_fqc'],(len(obs[name].ravel()),))

            # -- Indices --
            indices =  np.where(obs[name] == Config.missval[0], Config.missval[0], np.arange(len(obs[name])) )
            mask = np.ma.masked_equal(indices, Config.missval[0])
            indices = mask.compressed().astype(np.int32).tolist()
            vars_info[nname]['indices_'+case] = indices

            # -- Interpol data on a daily basis --
            # used for observed fAPAR
            if 'interpol_daily' in tempo_res:

                print ndays
                print 'interpol_daily'
                
                obs_daily = np.ones(ndays, np.float64) * Config.missval[0]
                tc_out = np.arange(0,ndays)
                tc = time_counter+offset
                
                for i in range(len(tc)):
                    ind = np.nonzero((tc_out == tc[i]-1))
                    if len(ind) != 0:
                        np.put(obs_daily, ind, obs[name][i])
                        
                obs[name] = obs_daily
                indices =  np.where(obs[name] == Config.missval[0], Config.missval[0], np.arange(len(obs[name])) )
                mask = np.ma.masked_equal(indices, Config.missval[0])
                indices = mask.compressed().tolist()
                vars_info[nname]['indices_'+case] = indices

                        
            # -- Daily flux data --   
            if 'daily' in tempo_res and 'interpol' not in tempo_res and\
               'diurnal' not in name :

                # smoothing or not smoothing
                # activiting smoothing just requires that the string "smooth" is part of the "processing" string attribute
                if 'smooth' in tempo_res:
                    ind = tempo_res.index('smooth')
                    test_smooth = (tempo_res[ind:].split('_'))[0]
                    #print 'TEST_SMOOTH', test_smooth
        

                if detect_gapf == True and case =='obs':
                    #print name
                    ans = flux_daily_diurnal(name, 
                                             obs[name], 
                                             ndays, 
                                             time_step, 
                                             time_counter, 
                                             tdaily,
                                             get_daily = True,
                                             test_smooth = test_smooth,
                                             detect_gapf = True,
                                             ind_gap = obs[name+'_fqc'])                   
                    
                    obs[name+'_fqc'] = ans[5]
                                             ###if name in flux_name:
                else:
                    ans = flux_daily_diurnal(name, 
                                             obs[name], 
                                             ndays, 
                                             time_step, 
                                             time_counter, 
                                             tdaily,
                                             get_daily = True,
                                             test_smooth = test_smooth)


                obs[name] = ans[0]
                obs['fic'][ific]['time_counter']       = ans[1]
                obs['fic'][ific]['time_counter_daily'] = ans[1]
                obs['fic'][ific]['time_step']          = ans[2]
                #obs['fic'][ific]['nobs_daily']        = ans[3]
                vars_info[nname]['nobs_daily']         = ans[3]
                vars_info[nname]['indices_'+case]       = ans[4]

            # -- Distinguish between 'daily' & 'diurnal' cycles --
            if 'diurnal' in tempo_res and 'diurnal' in name:

                #print 'calcul DIURNAL for '+ name
                
                # - smoothing or not smoothing
                # activiting smoothing just requires that the string "smooth" is part of the "processing" string attribute
                name_daily = name.split('_diurnal')[0]

               
                # if no daily observations accounted for then smoothing daily data by default
                if name_daily not in vars_info.keys():
                    test_smooth = 'smooth'
                # else same smoothing that the companion daily data
                else:
                    buf_tempo_res = vars_info[name_daily]['processing_'+case]
                    print 'tempo res', buf_tempo_res 
                    if 'smooth' not in buf_tempo_res:
                        test_smooth = 'nosmooth'
                    else:
                        ind = buf_tempo_res.index('smooth')
                        test_smooth = (buf_tempo_res[ind:].split('_'))[0]
                ###print '   DIURNAL : TEST_SMOOTH', test_smooth
        
                ans = flux_daily_diurnal(name,
                                         obs[name],
                                         ndays,
                                         time_step,
                                         time_counter,
                                         tdaily, 
                                         get_diurnal = True,
                                         diurnal_length = diurnal_length,
                                         diurnal_start = diurnal_start,
                                         test_smooth = test_smooth)

                obs[name] = ans[0]
                
                #if '_tl' not in name:
                if (name.split('_'))[-1] != 'tl' :
                    obs[name+'_diurnal'] = ans[0]
                else: # cas TL
                    obs[name.split('_')[0]+'_diurnal_tl'] = ans[0]
                                
                obs['fic'][ific]['time_counter']       = ans[1]
                obs['fic'][ific]['time_counter_diurnal'] = ans[1]
                obs['fic'][ific]['time_step']          = ans[2]
                ###obs['fic'][ific]['nobs_diurnal']       = ans[3]
                vars_info[nname]['nobs_diurnal']       = ans[3]
                vars_info[nname]['indices_'+case]       = ans[4]


            # -- Separate daytime from nighttime observations --   
            
            if tempo_res == 'day_vs_night':
                
                if detect_gapf == True and case =='obs':
                    #print name
                    ans = flux_day_vs_night(isite,
                                            name,
                                            obs[name], 
                                            ndays,
                                            time_counter,
                                            tdaytime,
                                            tnighttime,
                                            detect_gapf = detect_gapf,
                                            ind_gap = obs[name+'_fqc'])

                    obs[name+'_fqc'] = ans[3]

                else:
                    ans = flux_day_vs_night(isite,
                                            name,
                                            obs[name], 
                                            ndays,
                                            time_counter,
                                            tdaytime,
                                            tnighttime)
                    
                obs[name] = ans[0]
                    
##                 if (name.split('_'))[-1] != 'tl' :
##                     obs[name+'_night'] = ans[0]
##                 else: # cas TL
##                     obs[name.split('_')[0]+'_night_tl'] = ans[2]
                vars_info[nname]['indices_'+case]          = ans[1]
                obs['fic'][ific]['time_counter']           = time_counter
                obs['fic'][ific]['time_step']              = ans[2]


            # -- Yearly flux data --   
            
            if tempo_res == 'yearly':
                
                print nyears
                print type(nyears)
                ans = flux_yearly(name,
                                  obs[name],
                                  ndays,
                                  nyears,
                                  time_step,
                                  time_counter)
                obs[name] = ans[0]
                obs['fic'][ific]['time_counter']       = ans[1]
                obs['fic'][ific]['time_counter_daily'] = ans[1]
                obs['fic'][ific]['time_step']          = ans[2]
                ###vars_info[name]['nobs_daily']          = None
                vars_info[nname]['indices_'+case]       = ans[4]

                print obs['fic'][ific]['time_step']
                raw_input('pause')
                
            # -- Apply smoothing if not done already for daily and diurnal processing--
            if 'smooth' in tempo_res and test_smooth == None:
                ind = tempo_res.index('smooth')
                test_smooth = (tempo_res[ind:].split('_'))[0]
                # print 'TEST_SMOOTH FINAL', test_smooth                
                #print ' SMOOTHING activated for ',name,
                if test_smooth == 'smooth' or test_smooth == 'smoothmav':
                    obs[name] = various.smooth_square(obs[name],Config.smooth_len_square_filter) 
                     #print ' using Moving Average Window' 
                elif test_smooth == 'smoothgauss':
                    obs[name] = various.smooth_gaussian(obs[name],Config.smooth_gauss_filter) 
                    #print ' using Gaussian window'
    
                indices =  np.where(obs[name] == Config.missval[0], Config.missval[0], np.arange(len(obs[name])) )
                mask = np.ma.masked_equal(indices, Config.missval[0])
                indices = mask.compressed().tolist()

            
            
            # -- Normalization of the variables --
            # Normalization is performed on common time steps between obs and sim, which
            # require a prior definition of the corresponding available indices
            if 'normalize' in tempo_res :

                # Normalize
                if vars_info[nname]['indices_obs'] != None \
                   and vars_info[nname]['indices_sim'] != None :
                    #print "DEBUG / funcio.get_data / normalize", name
                    obs[name] = normalize_data(obs[name], vars_info, logfile,                                               
                                               name = name, case = case, tempo_res = tempo_res, 
                                               indices_obs = vars_info[nname]['indices_obs'],
                                               indices_sim = vars_info[nname]['indices_sim'])
                else:
                    continue

            # -- Substract the longterm trend --
            if 'detrend' in tempo_res :
                buf = np.ma.masked_where(obs[name] <= Config.missval[0], obs[name])
                vmean = np.ma.filled(np.ma.average(buf), Config.missval[0])
                obs[name] = obs[name] - vmean
                    
    # --- Return values ---
    return obs
# END get_data
# ==============================================================================







# ==============================================================================
# Get the estimated fAPAR from a NetCDF file 
#
# Return a dictionnary containing the value of the daily fAPAR
# obs = {'fAPAR':value, 'time_counter': value , 'time_step': value}
#
# Si pas de donnee : value = 1e20
# ------------------------------------------------------------------------------
def get_fapar_obs(ficname,
                  Data,
                  njours,
                  logfile,
                  obs_name = None,
                  smooth_fapar = None,
                  fapar_normalize = None,
                  fapar_normalize_minmax = None,
                  fapar_obs_skip = None
                  ):
    
    
    if len(glob.glob(ficname))==0: sys.exit('# The fAPAR file does not exist : \n ' +ficname)

    # -- Initialize dictionnary
    obs = {}
    obs['fAPARt'] = Config.missval[0]
    
    # -- Read data
    data = io.readnc(ficname)
    data = data[0]


    # -- Patch for missing values
    values = data[obs_name[0]]['value']
    values_mask = np.ma.masked_where(values <= Config.missval[0], values)
    values      = np.ma.masked_where(values >= Config.missval[1], values_mask)
    data[obs_name[0]]['value'] = values.filled(Config.missval[0])         
    
    jours_obs = np.array(data[Data.fapar_time_dim]['value'], np.float64)
    fAPAR_obs = np.array(data[obs_name[0]]['value'], np.float64)
    fAPAR_obs = np.reshape(fAPAR_obs,(len(fAPAR_obs),))

    
    # -- Daily fAPAR
    fAPAR = np.ones(njours, np.float64) * Config.missval[0]
    jours_sim = np.arange(0,njours)


    # -- skip some data
    if fapar_obs_skip !=None:  jours_sim = jours_sim + fapar_obs_skip

  
    for i in range(len(jours_obs)):
        ind = np.nonzero((jours_sim == jours_obs[i]-1))
        if len(ind) != 0:
            np.put(fAPAR, ind, fAPAR_obs[i])



    # - Result
    obs['fAPARt'] = fAPAR


    # -- fAPAR sigma errors
    obs['std_fAPARt'] = np.ones(njours, np.float64) * Config.missval[0]
    
    if Data.fapar_std_name != None:
        print '      + reading of fAPAR standard deviation errors : ', Data.fapar_std_name
        logfile.write('      + reading of fAPAR standard deviation errors : '+ Data.fapar_std_name +'\n')
                
        values_std = np.ma.masked_array(data[Data.fapar_std_name]['value'], values.mask)
        std_fAPAR_obs = np.array(values_std, np.float64)
        std_fAPAR_obs = np.reshape(std_fAPAR_obs,(len(std_fAPAR_obs),))
        std_fAPAR     = np.ones(njours, np.float64) * Config.missval[0]
        for i in range(len(jours_obs)):
            ind = np.nonzero((jours_sim == jours_obs[i]-1))
            if len(ind) != 0:
                np.put(std_fAPAR, ind, std_fAPAR_obs[i])
        obs['std_fAPARt'] = std_fAPAR

                
    # -- Temporal smoothing of fAPAR
    if smooth_fapar == True:
        ###print '      + smoothing fAPAR + '
        ###logfile.write('      + smoothing fAPAR + \n')

        obs['fAPARt'] = various.smooth_gaussian(obs['fAPARt'],Config.smooth_gauss_filter)

        
    # -- Normalization of fAPAR
##     if fapar_normalize == True:
##         obs['fAPARt'] = normalize_fapar(obs['fAPARt'], fapar_normalize_minmax[0], fapar_normalize_minmax[1])

    # -- Return value
    return obs
# END get_fluxes
# ==============================================================================
 








# ==============================================================================
# Write the fluxes that are actually optimized to a NetCDF file
# This account for potential temporal subsampling of the data...
#
# ------------------------------------------------------------------------------
def write_fluxes(ficname, Data, Site, datacase = None, mode = None):

    
    ####dim_order = ['lon','lat','PFT','time_counter','time_counter_daily']

    # -- Data to write
    if datacase == 'obs':
        data = copy.copy(Data.obs)
    if datacase[0:3] == 'sim':
        data = copy.copy(Data.sim)

           
    # -- Define the dimensions of the NetCDF file
    dims = [{'name': 'lon', 'size':Site.npts}]
    dims.append({'name': 'lat', 'size':Site.npts})
    dims.append({'name': 'Site', 'size':Site.npts})

     
    
     # -- Define the global attributes of the NetCDF file
    gattr = [{'name': 'date', 'value':strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())}]

    
    # -- Variables to write
    out = {}
    dim_list_time = []
    for isite in range(Site.npts):
        
        # -- informations on time counters
        for pname in Data.processing[isite]['sim'].keys():
            nts = Data.processing[isite]['sim'][pname]['n_ts']

            if pname !='': pname='_'+pname
            pname = pname + '_'+str(nts)

            pname = 'time_counter'+pname
            
            if pname not in dim_list_time:            
                dim_list_time.append(pname)
                dims.append({'name': pname, 'size':nts})
                #dims.append({'name': 'time_counter'+pname, 'size':nts})


        # -- variables       
        for name in Data.obsname_opti[isite]:       

            name_site = name+'_'+Site.name[isite]

            name_time_counter = Data.vars[isite][name]['processing_sim']
            nts = Data.processing[isite]['sim'][name_time_counter]['n_ts']
            
            if name_time_counter != '': name_time_counter='_'+name_time_counter

            name_time_counter = name_time_counter+'_'+str(nts)

            
            name_time_counter = 'time_counter' +name_time_counter
            
            out[name_site+'_'+datacase] = {'datatype': 'd', 'ndims':1, 'dim_name':(name_time_counter,), \
                                           'dim_size': 1, 'value': data[isite][name].ravel(), \
                                           'attr_name':['longname'], 'attr_value':['Values of '+name_site]}


    # -- Write the file
    if mode == 'w':
        io.writenc(ficname,gattr = gattr, dims = dims, append = 0)

    keys = out.keys()     
    keys.sort()
    if mode == "o": # overwrite
        for name in keys:
            io.writenc(ficname, vars = {name:out[name]} , append = 0)
    else:           # append
        for name in keys:
            io.writenc(ficname, vars = {name:out[name]} , append = 1)

        
# END write_fluxes
# ==============================================================================



# ==============================================================================
# Write the Root Mean Square Error between observations and ORCHIDEE simulations
#
# ------------------------------------------------------------------------------
def write_rmse_data(ficname,Data,logfile):

   
    f = open(ficname,'w')
    
    for name in Data.obsname_opti:
        val_rmse = various.rmse(Data.obs[name],Data.sim[name])
        print ' + RMSE ('+name+ ') = ', val_rmse
        logfile.write( ' + RMSE ('+name+ ') = '+ str(val_rmse) + '\n')
        f.write('RMSE(%s) = %s \n' %(name,val_rmse) )
    f.close()

# END
# ==============================================================================


# ==============================================================================
# Write infos about which site is in whcih regions (useful ?)
#
# ------------------------------------------------------------------------------
def write_sites_regions(ficname,Site, logfile):

    for imap in Site.real_maps:
        
        fictmp = ficname.split('.')[0]+str(imap+1)+'.'+ficname.split('.')[1]
        f = open(fictmp,'w')
        for isite in range(Site.npts):
            file = Site.fic_forc[isite].split('/')
            file = file[len(file)-1]
            startyr = file[6:10]
            if len(file) == 18:
                endyr = file[11:15]
            else:
                endyr = startyr
            f.write('%s %s %s %s \n' %(Site.name[isite],Site.loc[imap][isite],startyr,endyr) )
        f.close()

    print
    print '++ List of regions per site written ++'
    logfile.write('\n ++ List of regions per site written ++ \n\n')

# END
# ==============================================================================


# ==============================================================================
# Write the values of dMF/dx around the minimum of the misfit function
# (convergence test)
#
# ------------------------------------------------------------------------------
def write_sensiMF(ficname, Vars, Data, Opti):


    # --- Create headers
    format_para = '+++++ %-11s\n'
    fdata = '%7.6f'
    format_data = fdata
    for i in range(Opti.nlevels-1):
        format_data = format_data + ','+ fdata 

    format_data = ' + %11s  ' + format_data + '\n'

    # --- Write data
    f = open(ficname,'w')
            
    icnt=0
    for i in range(len(Vars.vars['opti_varname'])):
        vname = Vars.vars['opti_varname'][i]

      
        for ip in range(len(Opti.xmask[vname])):

            # - skip if undefined element
            if type(Opti.xmask[vname][ip]) == type(np.ma.masked):  continue
                
            f.write(format_para % tuple([vname]) )
            buf = ['MF']+ Opti.sensiMF[icnt,:].tolist()
            f.write(format_data % tuple(buf) )
            buf = ['MFpar'] + Opti.sensiMFpar[icnt,:].tolist()
            f.write(format_data % tuple(buf) )
            
            for oname in Data.obsname_opti:
                buf = ['MF'+oname] + Opti.sensiMFobs[oname][icnt,:].tolist()
                f.write(format_data % tuple(buf) )
                    
        icnt+=1

        
    f.close()
    
# END
# ==============================================================================



# ==============================================================================
# Write the values of dMF/dx as a function of eps
#
# ------------------------------------------------------------------------------
def write_gradMF_vs_eps(ficname, Opti, Site, Data, var_name = None, eps_val = None):


    # --- Create headers
    format_para = '+++++ %-11s\n'
    fdata = '%14.12f'
    format_data = fdata
    nlevels = len(eps_val)
    for i in range(nlevels-1):
        format_data = format_data + ','+ fdata 

    format_data = ' + %11s  ' + format_data + '\n'

    # --- Write data
    f = open(ficname,'w')

    # values for eps
    buf = ['eps'] + eps_val
    f.write(format_data % tuple(buf) )
    
    # variables and gradients
    for vname in var_name:
        
        f.write(format_para % tuple([vname]) )
        buf = ['gradMF']+ Opti.hist_gradMF_eps['MF'][vname].tolist()
        f.write(format_data % tuple(buf) )

        buf = ['gradMFpar']+ Opti.hist_gradMF_eps['MFpar'][vname].tolist()
        f.write(format_data % tuple(buf) )

        buf = ['gradMFobs_total']+ Opti.hist_gradMF_eps['MFobs_total'][vname].tolist()
        f.write(format_data % tuple(buf) )

        for isite in range(Site.npts):
            for name in Data.obsname_opti[isite]:

                name_site = name+'_'+Site.name[isite]
            
                buf = ['gradMFobs_'+name_site] + Opti.hist_gradMF_eps['MFobs_'+name_site][vname].tolist()
                f.write(format_data % tuple(buf) )
                    
    f.close()
    
# END
# ==============================================================================



# ==============================================================================
# Write the current state of the variables
#
# ------------------------------------------------------------------------------
def write_paras(ficname, Site, Vars, Opti, varname_tl = None, value_tl = None):


    dim_order = ['points_terre','indice_pft',\
                 'variation_day','variation_week',\
                 'variation_month','variation_year','variation_fix']

    
    # -- Copy the input dictionnary
    buf = copy.deepcopy(Vars.vars)
    
    vnames=various.triname(buf.keys(), Paras_def.parnames_template)
   
    # -- Write the nc file
    # global attributes + dimensions
    imap = Site.real_maps[0]
    ireg = Site.map['occupied_regions'][imap][0]
    dim = Vars.dims[imap][ireg]

    for i in range(len(dim)):
        # A quick fix for variables depending on global PFT (and unoptimized variables)
        if dim_order[i]=='indice_pft':dim[i]['size'] = Vars.vars['PFT_global']['dim_size']
        # A quick fix for variables depending on sites
        if dim_order[i]=='points_terre':dim[i]['size'] = Site.npts
        
    for imap in Site.real_maps:
        
        dim_order.append('map'+str(imap+1))
        dim.append({'name': 'map'+str(imap+1), 'size':len(Site.map['occupied_regions'][imap])})
        
        tmp = 0
        for ireg in Site.map['occupied_regions'][imap]:
            tmp = tmp + buf['PFT']['dim_size'][imap][ireg]

        dim_order.append('map_pft'+str(imap+1))
        dim.append({'name': 'map_pft'+str(imap+1), 'size':tmp})
        
    tmp2 = 0
    for isite in range(Site.npts):
        tmp2 = tmp2 + len(Site.indice_pft[isite])
    dim.append({'name': 'site_pft', 'size':tmp2})
    dim_order.append('site_pft')


    io.writenc(ficname,gattr = Vars.gattr, dims = dim, dim_order = dim_order)

    # variables

    for elemname in vnames:

        # reshape name and values of the attribute
        if elemname != 'PFT':

            # If the paramter is pft and region dependent it has to be reshaped :
            # writenc cannot manipulate dictionaries...
            if len(buf[elemname]['dim_name']) == 3:

                if 'indice_region' in buf[elemname]['dim_name']:
                    imap = buf[elemname]['map']
                    buf[elemname]['dim_name'] = ('map_pft'+str(imap+1),)
                else:
                    buf[elemname]['dim_name'] = ('site_pft',)

                buf[elemname]['value'] = Opti.x[elemname]
                buf[elemname]['dim_size'] = (len(Opti.x[elemname].ravel()))
                
            elif 'indice_region' in buf[elemname]['dim_name']:
                imap = buf[elemname]['map']
                #buf[elemname]['value'] = Opti.x[elemname]
                buf[elemname]['dim_name'] = ('map'+str(imap+1),)
                #buf[elemname]['dim_size'] = (len(Opti.x[elemname].ravel()))   
            
            attr_name = buf[elemname]['attr_name']
            
            attr_name.extend(['opti','info_prior'])
            buf[elemname]['attr_name'] = attr_name

            attr_value = buf[elemname]['attr_value']
            attr_value.extend([buf[elemname]['opti'],buf[elemname]['info_prior']])
            buf[elemname]['attr_value'] = attr_value

            if buf[elemname]['opti'] == 'y':
                attr_name = buf[elemname]['attr_name']
                attr_value = buf[elemname]['attr_value']               

                if 'sigma_pft' in buf[elemname].keys():
                    attr_name.extend(['min','max','sigma','transform'])
                    attr_value.extend([buf[elemname]['min'],buf[elemname]['max'], \
                                           buf[elemname]['sigma_pft'],buf[elemname]['transform']])
                else:
                    attr_name.extend(['min','max','transform'])
                    attr_value.extend([buf[elemname]['min'],buf[elemname]['max'], \
                                       buf[elemname]['transform']])
                
                buf[elemname]['attr_value'] = attr_value
                buf[elemname]['attr_name'] = attr_name

                # If there is no PFT dimension for some parameters, one optimize
                # a multiplicative parameter instead of a real physical variable
                if 'K'+elemname in Vars.vars.keys():
                    print
                    print 'Gestion de K'+elemname, buf['K'+elemname]['value']
                    
                    print buf[elemname]['value'],' --->',
                    buf[elemname]['value'] = buf['K'+elemname]['value']*buf[elemname]['value']
                    print
                    print buf[elemname]['value']
                    print


            # Tangent linear 
            if elemname == varname_tl:                    
                # Modify the attribute of the independant variable 
                attr_name.extend(['tangent_linear'])
                attrib_tl = 'y'            
                attr_value.extend([attrib_tl])
            
            ###print
            ###print 'ECRITURE PARAS_TL POUR ',elemname, ' / PFT #',pft_tl
            

        # skip if parameter not defined in para_ORCH_def.nc
        if buf[elemname]['attr_name'][0] != "-" and buf[elemname]['value'].all() !=Config.missval[0]:
            var = {elemname:buf[elemname]}
            io.writenc(ficname, vars = var, append = 1)
          
        # Writing Var_tl
        if value_tl !=None and elemname == varname_tl:
            # Create the value_tl variable containing the tl values
            # (0 / 1, 1 for activating TL mode)
           
            Vars.vars['Var_tl'] = {}
            Vars.vars['Var_tl']['value'] = value_tl
            Vars.vars['Var_tl']['dim_name'] = Vars.vars[elemname]['dim_name']
            Vars.vars['Var_tl']['dim_size'] = Vars.vars[elemname]['dim_size']
            Vars.vars['Var_tl']['attr_name'] = ['long_name']
            Vars.vars['Var_tl']['attr_value'] = ['Activate TL mode when = 1']
            Vars.vars['Var_tl']['datatype'] = 'i'
                
            io.writenc(ficname, vars = {'Var_tl':Vars.vars['Var_tl']} , append = 1)

    #raw_input('pause : ecriture fichier parametres OK')
        
    # -- Delete the copy
    del(buf)
# END write_paras
# ==============================================================================






# ==============================================================================
# Write the optimisation outputs
#
# ------------------------------------------------------------------------------
def write_optires(ficname, Site, Opti, Vars, Data, test_convergence = None):

     
    
    # --- Define the dimensions of the NetCDF file ---
    # ------------------------------------------------

    # Here we will distinguish the dimensions definitions between :
    # - parameters PFT AND region dependent
    # - parameters only PFT dependent
    # --> because there are not the same amount of pft in the differents regions
    # + the possibility of different maps has to be added on top...


    dim_order = ['parameter',
                 'site','nosite',
                 'nomap',
                 'nostpft',
                 'pft_global','nopft',
                 'n','nobs','nloop']
    
    dim_time  = ['variation_day','variation_week',
                 'variation_month','variation_year','variation_fix']

    dims = [{'name': 'parameter', 'size':1}]

    dims.append({'name': 'site', 'size':Site.npts})
    dims.append({'name': 'nosite', 'size':1})
    dims.append({'name': 'nomap', 'size':1})
    dims.append({'name': 'nostpft', 'size':1})
    dims.append({'name': 'pft_global', 'size':Vars.vars['PFT_global']['dim_size']})
    dims.append({'name': 'nopft', 'size':1})
    dims.append({'name': 'n', 'size':Opti.n})
    dims.append({'name': 'nobs', 'size':Data.nobs})
    dims.append({'name': 'nloop', 'size':Opti.nloop})
    
    for imap in Site.real_maps:
        
        dim_order.append('map'+str(imap+1))
        dims.append({'name': 'map'+str(imap+1), 'size':len(Site.map['occupied_regions'][imap])})
        
        tmp = 0
        for ireg in Site.map['occupied_regions'][imap]:
            tmp = tmp + Vars.vars['PFT']['dim_size'][imap][ireg]

        dim_order.append('map_pft'+str(imap+1))
        dims.append({'name': 'map_pft'+str(imap+1), 'size':tmp})

    tmp2 = 0
    for isite in range(Site.npts):
        tmp2 = tmp2 + len(Site.indice_pft[isite])
    dims.append({'name': 'site_pft', 'size':tmp2})
    dim_order.append('site_pft')
        
    # Optimized parameter names
    opti_varnames=';'.join(Opti.xname)
    dim_order.extend(['str_var'])
    dims.append({'name': 'str_var', 'size':len(opti_varnames)})

    # List of the site names
    tmp = []
    for isite in range(Site.npts):tmp.append(Site.name[isite])
    site_names=';'.join(tmp)
    
    # dimensions temporelles pour parametres variant temporellement
    time_dim_name = []
    time_dim_size = []
    imap = Site.real_maps[0]
    ireg = Site.map['occupied_regions'][imap][0]
    for i in range(len(Vars.dims[imap][ireg])):
        name = Vars.dims[imap][ireg][i]['name']
        if name.split('_')[0] == 'variation':
            time_dim_name.append(name)
            time_dim_size.append(Vars.dims[imap][ireg][i]['size'])
            
    for i in range(len(time_dim_name)):
        dims.append({'name': time_dim_name[i], 'size': time_dim_size[i]})
        

    # dim_order
    dim_order = dim_order + dim_time
    if Opti.method == 'bfgs':
        dim_order.extend(['str_task'])
        dims.append({'name': 'str_task', 'size':len(Opti.BFGS['task'])})
        if Opti.scan_fmisfit_prior == False:
            dim_order.extend(['str_task_hist'])
            dims.append({'name': 'str_task_hist', 'size':len(Opti.BFGS['task_hist'][0])})
        
    #- dimension "Region" des parametres NON PFT dependent
    var_region = {}

    for name in Opti.x.keys():
        var_region[name]='nomap'
        if name != 'all' and 'indice_region' in Vars.vars[name]['dim_name'] and 'indice_pft' not in Vars.vars[name]['dim_name']:
            imap = Vars.vars[name]['map']
            var_region[name] = 'map'+str(imap+1)

    #- dimension "Site" des parametres NON region dependent
    var_site = {}

    for name in Opti.x.keys():
        var_site[name]='nosite'
        if name != 'all' and 'points_terre' in Vars.vars[name]['dim_name'] and 'indice_region' not in Vars.vars[name]['dim_name']:
            var_site[name] = 'site'

            
    #- dimension PFT des parametres NON region dependent
    var_pft = {}

    for name in Opti.x.keys():
        var_pft[name]='nopft'
        if name != 'all' and 'indice_pft' in Vars.vars[name]['dim_name'] and 'indice_region' not in Vars.vars[name]['dim_name']:
            var_pft[name] = 'pft_global'

    #- dimension region + pft des parametres
    var_mappft = {}

    for name in Opti.x.keys():
        var_mappft[name]='nomap'
        if name != 'all' and 'indice_pft' in Vars.vars[name]['dim_name'] and 'indice_region' in Vars.vars[name]['dim_name']:
            imap = Vars.vars[name]['map']
            var_mappft[name] = 'map_pft'+str(imap+1)

    #- dimension site + pft des parametres
    var_sitepft = {}

    for name in Opti.x.keys():
        var_sitepft[name]='none'
        if name != 'all' and 'points_terre' in Vars.vars[name]['dim_name'] and 'indice_pft' in Vars.vars[name]['dim_name']:
            var_sitepft[name] = 'site_pft'


            
    #- dimension temporelle des parametres
    var_time = {}
    for name in Opti.x.keys():
        if name != 'all':
            var_dim= list(Vars.vars[name]['dim_name'])
            for tdim in time_dim_name:
                if tdim in var_dim:
                    var_time[name] = tdim

    
    # --- Define the global attributes of the NetCDF file ---
    # -------------------------------------------------------
    gattr = [{'name': 'date', 'value':strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())}]


    # --- Define the variables to write ---
    # -------------------------------------

    out = {}
    varnames = various.triname(Opti.x.keys(), Paras_def.parnames_template)


    # -- variables & uncertainties (prior & posterior)
    # -
    out['Site'] =  {'datatype': 'd', 'ndims':1, 'dim_name':('site',), \
                   'dim_size': 1, 'value': np.arange(Site.npts), \
                   'attr_name':['longname'], 'attr_value':['Sites']}

    out['Site_names'] =  {'datatype': 'c', 'ndims':1, 'dim_name':('site',), \
                          'dim_size': 1, 'value': site_names, \
                          'attr_name':['longname'], 'attr_value':['Names of the sites']}

    
    
    for name in varnames:

        sig_post = np.ma.array(Opti.Bpost_diag[name][:])
        sig_post = np.ma.masked_where(sig_post == Config.missval[0], sig_post)
        sig_post = np.ma.filled(np.ma.sqrt(sig_post), Config.missval[0])
        #print 'sig_post',sig_post

        if len(Vars.vars[name]['dim_name']) < 3:

            out[name] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_site[name],var_region[name],var_time[name]), \
                         'dim_size': 4, 'value': Opti.x[name], \
                         'attr_name':['longname'], 'attr_value':['Values of '+name]}
            
            out[name+'_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_site[name],var_region[name],var_time[name]), \
                                  'dim_size': 4, 'value': Opti.xprior[name], \
                                  'attr_name':['longname'], 'attr_value':['Prior values of '+name]}
            
            out['hist_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop', var_pft[name],var_site[name],var_region[name],var_time[name]), \
                                 'dim_size': 5, 'value': Opti.hist_x[name], \
                                 'attr_name':['longname'], 'attr_value':['Values of '+name]}
            
            out[name+'_SIG_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_site[name],var_region[name],var_time[name]), \
                                      'dim_size': 4, 'value': np.sqrt(Opti.B[name]), \
                                      'attr_name':['longname'], 'attr_value':['Prior SIGMA on '+name]}

#             if Opti.Bpost_diag[name][0] >= 0:
#                 out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_site[name],var_region[name],var_time[name]), \
#                                          'dim_size': 4, 'value': np.sqrt(Opti.Bpost_diag[name]), \
#                                          'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}

#             else:
#                 out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_site[name],var_region[name],var_time[name]), \
#                                          'dim_size': 4, 'value': Opti.Bpost_diag[name], \
#                                          'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}

                
            out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_site[name],var_region[name],var_time[name]), \
                                     'dim_size': 4, 'value': sig_post, \
                                     'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}

            
        if len(Vars.vars[name]['dim_name']) == 3:

            if 'indice_region' in Vars.vars[name]['dim_name'] :


                out[name] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_mappft[name],var_time[name]), \
                                 'dim_size': 2, 'value': Opti.x[name], \
                                 'attr_name':['longname'], 'attr_value':['Values of '+name]}
                
                out[name+'_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_mappft[name],var_time[name]), \
                                          'dim_size': 2, 'value': Opti.xprior[name], \
                                          'attr_name':['longname'], 'attr_value':['Prior values of '+name]}
                
                out['hist_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop', var_mappft[name],var_time[name]), \
                                         'dim_size': 3, 'value': Opti.hist_x[name], \
                                         'attr_name':['longname'], 'attr_value':['Values of '+name]}
                
                out[name+'_SIG_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_mappft[name],var_time[name]), \
                                              'dim_size': 2, 'value': np.sqrt(Opti.B[name]), \
                                              'attr_name':['longname'], 'attr_value':['Prior SIGMA on '+name]}
                
                #             if Opti.Bpost_diag[name][0] >= 0:
                #                 out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_mappft[name],var_time[name]), \
                    #                                          'dim_size': 2, 'value': np.sqrt(Opti.Bpost_diag[name]), \
                    #                                          'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}
                    #             else:
                    #                 out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_mappft[name],var_time[name]), \
                        #                                          'dim_size': 2, 'value': Opti.Bpost_diag[name], \
                        #                                          'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}
                
                out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_mappft[name],var_time[name]), \
                                             'dim_size': 2, 'value': sig_post, \
                                             'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]} 

            elif 'points_terre' in Vars.vars[name]['dim_name']:


                out[name] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_sitepft[name],var_time[name]), \
                                 'dim_size': 2, 'value': Opti.x[name], \
                                 'attr_name':['longname'], 'attr_value':['Values of '+name]}
                
                out[name+'_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_sitepft[name],var_time[name]), \
                                          'dim_size': 2, 'value': Opti.xprior[name], \
                                          'attr_name':['longname'], 'attr_value':['Prior values of '+name]}
                
                out['hist_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop', var_sitepft[name],var_time[name]), \
                                         'dim_size': 3, 'value': Opti.hist_x[name], \
                                         'attr_name':['longname'], 'attr_value':['Values of '+name]}
                
                out[name+'_SIG_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_sitepft[name],var_time[name]), \
                                              'dim_size': 2, 'value': np.sqrt(Opti.B[name]), \
                                              'attr_name':['longname'], 'attr_value':['Prior SIGMA on '+name]}
                
                #             if Opti.Bpost_diag[name][0] >= 0:
                #                 out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_sitepft[name],var_time[name]), \
                    #                                          'dim_size': 2, 'value': np.sqrt(Opti.Bpost_diag[name]), \
                    #                                          'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}
                    #             else:
                    #                 out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_sitepft[name],var_time[name]), \
                        #                                          'dim_size': 2, 'value': Opti.Bpost_diag[name], \
                        #                                          'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}
                
                out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_sitepft[name],var_time[name]), \
                                             'dim_size': 2, 'value': sig_post, \
                                             'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]} 

    out['var_Bprior_diag'] = {'datatype': 'd', 'ndims':1, 'dim_name':('n',), \
                              'dim_size': 1, 'value': Opti.B['all'], \
                              'attr_name':['longname'], 'attr_value':['Prior covariance matrix on the parameters (diagonal)']}

        
    if Opti.scan_fmisfit_prior == False:
        out['var_Bpost'] = {'datatype': 'd', 'ndims':2, 'dim_name':('n','n'), \
                            'dim_size': 2, 'value': Opti.Bpost, \
                            'attr_name':['longname'], 'attr_value':['Posterior covariance matrix on the parameters']}
        
        
    # -- observation & uncertainties (prior & current)
    # - 
    # obsnames = various.triname(Data.obsname_opti, Config.obsnames_template)
    #obsnames = various.triname(Data.obsname_opti, Data.obsnames_template)

    #for name in obsnames:
    for isite in range(Site.npts):
        for name in Data.obsname_opti[isite]:
             
            name_site = name+'_'+Site.name[isite]

            out[name_site+'_SIG_user'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                                     'dim_size': 1, 'value': (Data.vars[isite][name]['sigma_user'],), \
                                     'attr_name':['longname'], 'attr_value':['Prior user-defined SIGMA on '+name_site]}
            
            
            out[name_site+'_SIG_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                                      'dim_size': 1, 'value': (Data.vars[isite][name]['sigma_prior'],), \
                                      'attr_name':['longname'], \
                                      'attr_value':['Prior SIGMA on '+name_site+' after modification with respect to the temporal sampling ' ]}
            
            out[name_site+'_SIG'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                                     'dim_size': 1, 'value': (Data.vars[isite][name]['sigma'],), \
                                     'attr_name':['longname'], 'attr_value':['Current SIGMA on '+name_site]}

    # Names of the optimized parameters
    out['opti_varnames'] = {'datatype': 'c', 'ndims':1, 'dim_name':('str_var',), \
                                'dim_size': 1, 'value': opti_varnames, \
                                'attr_name':['longname'], 'attr_value':['Name of the optimized parameters']}



    if Opti.scan_fmisfit_prior == False and Opti.propagate_Bprior == True and Opti.nloop >= 1:
        
        #out['obs_Rprior'] = {'datatype': 'd', 'ndims':2, 'dim_name':('nobs','nobs'), \
        #                    'dim_size': 2, 'value': Opti.Rprior, \
        #                    'attr_name':['longname'], 'attr_value':['Prior covariance matrix on the observations']}

        #-DEBUG
	if 'Jacobian_prior' in dir(Data):
		out['Jacobian_prior'] = {'datatype': 'd', 'ndims':2, 'dim_name':('n','nobs'), \
                                     'dim_size': 2, 'value': Data.Jacobian_prior, \
                                     'attr_name':['longname'], 'attr_value':['Prior Jacobian']}
        #-


    out['data_Rprior_diag'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nobs',), \
                                  'dim_size': 1, 'value': Data.Rprior['all'], \
                                  'attr_name':['longname'], 'attr_value':['Prior covariance matrix on the observations (diagonal)']}

    if Opti.scan_fmisfit_prior == False and Opti.calculate_Rpost == True and test_convergence == True \
       and 'Rpost' in dir(Opti):
        
        out['obs_Rpost'] = {'datatype': 'd', 'ndims':2, 'dim_name':('nobs','nobs'), \
                            'dim_size': 2, 'value': Opti.Rpost, \
                            'attr_name':['longname'], 'attr_value':['Posterior covariance matrix on the observations']}
        

    # -- Jacobian of the model at the minimum
    # -
    if Opti.scan_fmisfit_prior == False:
	if 'Jacobian' in dir(Data):
	       	out['Jacobian'] = {'datatype': 'd', 'ndims':2, 'dim_name':('n','nobs'), \
                    'dim_size': 2, 'value': Data.Jacobian, \
                    'attr_name':['longname'], 'attr_value':['Jacobian matrix of ORCHIDEE at the minimum of the misfit function']}
        

    # -- BFGS
    # -
    if Opti.method == 'bfgs':
        out['task'] = {'datatype': 'c', 'ndims':1, 'dim_name':('str_task',), \
                       'dim_size': 1, 'value': Opti.BFGS['task'], \
                       'attr_name':['longname'], 'attr_value':['Termination message for BFGS']}

        if Opti.scan_fmisfit_prior == False:
            out['task_hist'] = {'datatype': 'c', 'ndims':1, 'dim_name':('str_task_hist',), \
                                'dim_size': 1, 'value': Opti.BFGS['task_hist'][0], \
                                'attr_name':['longname'], 'attr_value':['Termination messages for BFGS']}


    # -- misfit function
    # -
            
    out['nloop'] = {'datatype': 'i', 'ndims':1, 'dim_name':('parameter',), \
                    'dim_size': 1, 'value': Opti.nloop, \
                    'attr_name':['longname'], 'attr_value':['Number of iterations']}


    out['MF'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                'dim_size': 1, 'value': Opti.MF, \
                'attr_name':['longname'], 'attr_value':['Value of the misfit function at the end of the optimization']}

    out['hist_MF'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop',), \
                    'dim_size': 1, 'value': Opti.hist_MF, \
                    'attr_name':['longname'], 'attr_value':['History of the misfit function values']}
   
    out['MFpar'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                   'dim_size': 1, 'value': Opti.MFpar, \
                   'attr_name':['longname'], 'attr_value':['Value of the misfit function for the parameters at the end of the optimization']}

    out['hist_MFpar'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop',), \
                        'dim_size': 1, 'value': Opti.hist_MFpar, \
                        'attr_name':['longname'], 'attr_value':['History of the misfit function values for the parameters']}
    

    for name in Opti.hist_MFobs.keys():
        out['MFobs_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                             'dim_size': 1, 'value': Opti.MFobs[name], \
                             'attr_name':['longname'], 'attr_value':['Value of the misfit function at the end of the optimization for '+name]}

        out['hist_MFobs_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop',), \
                                  'dim_size': 1, 'value': Opti.hist_MFobs[name], \
                                  'attr_name':['longname'], 'attr_value':['History of the misfit function values for '+name]}
        
    
    out['hist_MFobs'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop',), \
                        'dim_size': 1, 'value': Opti.hist_MFobs['total'], \
                        'attr_name':['longname'], 'attr_value':['History of the misfit function values for the whole of the observations']}
    


    # -- gradient
    # -
    out['gradMF'] = {'datatype': 'd', 'ndims':1, 'dim_name':('n',), \
                    'dim_size': 1, 'value': Opti.gradMF, \
                    'attr_name':['longname'], 'attr_value':['Value of the gradient of the misfit function at the end of the optimization']}

    out['hist_gradMF'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop','n'), \
                              'dim_size': 2, 'value': Opti.hist_gradMF['MF'], \
                              'attr_name':['longname'], 'attr_value':['History of the gradient of the misfit function']}

    out['hist_gradMFpar'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop','n'), \
                                 'dim_size': 2, 'value': Opti.hist_gradMF['MFpar'], \
                                 'attr_name':['longname'], 'attr_value':['History of the gradient of the misfit function for the parameters']}

    out['hist_gradMFobs'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop','n'), \
                                 'dim_size': 2, 'value': Opti.hist_gradMF['MFobs_total'], \
                                 'attr_name':['longname'], 'attr_value':['History of the gradient of the misfit function for the observations']}

    for name in Opti.hist_MFobs.keys():
        out['hist_gradMFobs_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop','n'), \
                                     'dim_size': 2, 'value': Opti.hist_gradMF['MFobs_'+name], \
                                     'attr_name':['longname'], 'attr_value':['History of the gradient of the misfit function for '+name]}

     

    # --- Order of the parameters to write ---
    # ----------------------------------------
    var_order = ['Site']

    #var_order.extend(['Site_names'])
    
    for name in varnames:
        var_order.extend([name, name+'_prior', 'hist_'+name, name+'_SIG_prior', name+'_SIG_post'])

    if Opti.scan_fmisfit_prior == False:   var_order.extend(['var_Bpost'])

    for isite in range(Site.npts):
        for name in Data.obsname_opti[isite]:  
            name_site = name+'_'+Site.name[isite]
            var_order.extend([name_site+'_SIG_user',name_site+'_SIG_prior', name_site+'_SIG'])

    var_order.extend(['opti_varnames'])

    if Opti.scan_fmisfit_prior == False:
	if 'Jacobian' in dir(Data):
		var_order.extend(['Jacobian'])

    var_order.extend(['var_Bprior_diag'])
    var_order.extend(['data_Rprior_diag'])
    var_order.extend(['nloop'])
    
    if Opti.method == 'bfgs':
        var_order.extend(['task'])
        if Opti.scan_fmisfit_prior == False:
            var_order.extend(['task_hist'])

    var_order.extend(['MF','hist_MF','MFpar','hist_MFpar'])
        
    for name in Opti.hist_MFobs.keys():
        var_order.extend(['MFobs_'+name,'hist_MFobs_'+name])
    var_order.extend(['gradMF'])
    var_order.extend(['hist_gradMF', 'hist_gradMFpar', 'hist_gradMFobs'])
    
    for name in Opti.hist_MFobs.keys():
        var_order.extend(['hist_gradMFobs_'+name])

    if Opti.scan_fmisfit_prior == True or Opti.scan_fmisfit_post == True:
        var_order = []
        for name in varnames:
            var_order.extend([name, name+'_prior', 'hist_'+name])
        var_order.extend(['nloop','hist_MF','hist_MFpar'])
        for name in Opti.hist_MFobs.keys():
            var_order.extend(['hist_MFobs_'+name])

    # Prior error covariance matrix on observations
    if Opti.scan_fmisfit_prior == False and Opti.propagate_Bprior == True and Opti.nloop >= 1 :
	if 'Jacobian_prior' in dir(Data):
            #var_order.extend(['obs_Rprior'])
            var_order.extend(['Jacobian_prior'])

    # Posterior error covariance matrix on observations
    if Opti.scan_fmisfit_prior == False and test_convergence == True \
       and Opti.calculate_Rpost == True and 'Rpost' in dir(Opti):

        var_order.extend(['obs_Rpost'])

   
    # --- Write the file ---
    # ----------------------
    
    
    # global attributes + dimensions
    io.writenc(ficname,gattr = gattr, dims = dims, dim_order = dim_order)
    for name in var_order:
        io.writenc(ficname, vars = {name:out[name]} , append = 1)


    # ---- Liberate some memory space...
    if Opti.scan_fmisfit_prior == False and test_convergence == True:
        if Opti.calculate_Rpost == True and 'Rpost' in dir(Opti):
            del(Opti.Rpost)
            del(Data.Jacobian)
        if Opti.propagate_Bprior == True and 'Jacobian_prior' in dir(Data):
            #del(Opti.Rprior)
            del(Data.Jacobian_prior)
        
                
# END write_optires
# ==============================================================================

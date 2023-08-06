#*******************************************************************************
# MODULE	: FUNCIO_SITE
# AUTHOR	: S. KUPPEL
# CREATION	: 04/2010
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
Routines adapted from funcio.py for use on individual sites
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import copy,io
import numpy as np
from time import localtime, strftime
from orchis_config import Paras_def, Config, Data_def

#from TOOLS import various
import various

# ==============================================================================
# Write the fluxes that are actually optimized to a NetCDF file, for each
# site individually.
# This account for potential temporal subsampling of the data...
#
# ------------------------------------------------------------------------------
def write_fluxes(isite, ficname, Data, Site, datacase = None, mode = None):


    # -- Data to write
    if datacase == 'obs':
        data = copy.copy(Data.obs[isite])
    if datacase[0:3] == 'sim':
        data = copy.copy(Data.sim[isite])

           
    # -- Define the dimensions of the NetCDF file
    dims = [{'name': 'lon', 'size':1}]
    dims.append({'name': 'lat', 'size':1})
    dims.append({'name': 'PFT', 'size':len(Site.indice_pft[isite])})


    # -- informations on time counters
    for pname in Data.processing[isite]['sim'].keys():
        nts = Data.processing[isite]['sim'][pname]['n_ts']
        if pname !='': pname='_'+pname
        dims.append({'name': 'time_counter'+pname, 'size':nts})
      
    
    # -- Define the global attributes of the NetCDF file
    gattr = [{'name': 'Site_number', 'value':str(isite+1)}]
    gattr.append({'name': 'Site_name', 'value':Site.name[isite]})
    gattr.append({'name': 'date', 'value':strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())})

    
    # -- Variables to write
    out = {}
    for name in Data.obsname_opti[isite]:       

         
        name_time_counter = Data.vars[isite][name]['processing_sim']
        if name_time_counter != '': name_time_counter='_'+name_time_counter
        name_time_counter = 'time_counter' +name_time_counter

        out[name+'_'+datacase] = {'datatype': 'd', 'ndims':1, 'dim_name':(name_time_counter,), \
                                  'dim_size': 1, 'value': data[name].ravel(), \
                                  'attr_name':['longname'], 'attr_value':['Values of '+name]}


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

        
# END write_fluxes_site
# ==============================================================================



# ==============================================================================
# Write the Root Mean Square Error between observations and ORCHIDEE simulations
#
# ------------------------------------------------------------------------------
def write_rmse_data(isite,ficname,Data,logfile):

   
    f = open(ficname,'w')
    
    for name in Data.obsname_opti[isite]:
        val_rmse = various.rmse(Data.obs[isite][name],Data.sim[isite][name])
        print ' + RMSE ('+name+ ') = ', val_rmse
        logfile.write( ' + RMSE ('+name+ ') = '+ str(val_rmse) + '\n')
        f.write('RMSE(%s) = %s \n' %(name,val_rmse) )
    f.close()

# END
# ==============================================================================


# ==============================================================================
# Write the current state of the variables 
#
# ------------------------------------------------------------------------------
def write_paras(ficname, Vars, varname_tl = None, value_tl = None):


    dim_order = ['points_terre','indice_pft',\
                 'variation_day','variation_week',\
                 'variation_month','variation_year','variation_fix']

    
    # -- Copy the input dictionnary
    buf = copy.deepcopy(Vars.vars)

    vnames = ['PFT']
    vnames.extend(various.triname(buf.keys(), Paras_def.parnames_template))
   
    # -- Write the file
    # global attributes + dimensions
    io.writenc(ficname,gattr = Vars.gattr, dims = Vars.dims, dim_order = dim_order)

    # variables
#    print "#DEBUG / funcio.write_paras"
    for elemname in vnames:

        # reshape name and values of the attribute
        if elemname != 'PFT':
            
            attr_name = buf[elemname]['attr_name']
            
            attr_name.extend(['opti','info_prior'])
            buf[elemname]['attr_name'] = attr_name

            attr_value = buf[elemname]['attr_value']
            attr_value.extend([buf[elemname]['opti'],buf[elemname]['info_prior']])
            buf[elemname]['attr_value'] = attr_value

            if buf[elemname]['opti'] == 'y':
                attr_name = buf[elemname]['attr_name']
                attr_name.extend(['min','max','sigma','transform'])
                buf[elemname]['attr_name'] = attr_name
                
                attr_value = buf[elemname]['attr_value']
                attr_value.extend([buf[elemname]['min'],buf[elemname]['max'], \
                                   buf[elemname]['sigma'],buf[elemname]['transform']])
                buf[elemname]['attr_value'] = attr_value

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

#                print '  # DEBUG / '+elemname,' :',buf[elemname]['value']

            # Tangent linear 
            if elemname == varname_tl:                    
                # Modify the attribute of the independant variable 
                attr_name.extend(['tangent_linear'])
                attrib_tl = 'y'            
                attr_value.extend([attrib_tl])

                            ###print
                ###print 'ECRITURE PARAS_TL POUR ',elemname, ' / PFT #',pft_tl
                
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
def write_optires(isite, ficname, Site, Opti, Vars_tot, Vars, Data, indice_pft, test_convergence = None):


    
    # --- Define the dimensions of the NetCDF file ---
    # ------------------------------------------------
    dim_order = ['parameter','pft','nopft','n','nloop','nobs']
    dim_time  = ['variation_day','variation_week',
                 'variation_month','variation_year','variation_fix']

    dims = [{'name': 'parameter', 'size':1}]
    dims.append({'name': 'pft', 'size':len(indice_pft)})
    dims.append({'name': 'nopft', 'size':1})
    dims.append({'name': 'n', 'size':Opti.ns[isite]})
    dims.append({'name': 'nloop', 'size':Opti.nloop})
    dims.append({'name': 'nobs', 'size':Data.nobs_site[isite]})

    # Optimized parameter names
    tmp = []
    for ipar in Opti.indsite[isite]:
        tmp.append(Opti.xname[ipar])
    opti_varnames=';'.join(tmp)
    dim_order.extend(['str_var'])
    dims.append({'name': 'str_var', 'size':len(opti_varnames)})

    # dimensions temporelles pour parametres variant temporellement
    time_dim_name = []
    time_dim_size = []
    for i in range(len(Vars.dims)):
        name = Vars.dims[i]['name']
        if name.split('_')[0] == 'variation':
            time_dim_name.append(name)
            time_dim_size.append(Vars.dims[i]['size'])

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
        

    #- dimension "Site" des parametres
    var_site = {}
    dim_site = 1

    for name in Opti.x.keys():
        var_site[name]='nosite'
        if name != 'all' and 'points_terre' in Vars_tot.vars[name]['dim_name']:
            var_site[name] = 'site'
            dim_site = Site.npts

    #- dimension PFT des parametres
    var_pft = {}
    dim_pft = 1

    for name in Opti.x.keys():
        var_pft[name]='nopft'
        if name != 'all':
            if 'indice_pft' in Vars.vars[name]['dim_name']:
                var_pft[name] = 'pft'
                dim_pft = len(indice_pft) 


    #- dimension temporelle des parametres
    var_time = {}
    dim_time = {}
    ###print '+++ Variation T pour les variables'
    for name in Opti.x.keys():
        print name
        if name != 'all':
            var_dim= list(Vars.vars[name]['dim_name'])
            for tdim in time_dim_name:
                if tdim in var_dim:
                    var_time[name] = tdim
                    idx = var_dim.index(tdim)
                    dim_time[name] = Vars.vars[name]['dim_size'][idx]
                
            ###print '  + '+name,var_time[name],dim_time[name]
        
    
        

    
    # --- Define the global attributes of the NetCDF file ---
    # -------------------------------------------------------
    gattr = [{'name': 'date', 'value':strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())}]


    # --- Define the variables to write ---
    # -------------------------------------

    out = {}
    varnames = various.triname(Opti.x.keys(), Paras_def.parnames_template)


    # -- variables & uncertainties (prior & posterior)
    # -
    out['PFT'] =  {'datatype': 'd', 'ndims':1, 'dim_name':('pft',), \
                   'dim_size': 1, 'value': indice_pft, \
                   'attr_name':['longname'], 'attr_value':['Plant Functional Types']}

    #print Site.name[isite]
    
    for name in varnames:

        # --- Check for site or pft dependence, in order to isolate one site the right way
        if var_site[name] == 'site' and var_pft[name] == 'nopft':
            ind = copy.copy([isite])

        elif var_pft[name] == 'pft' and var_site[name] == 'nosite':
            if 'indice_region' in Vars_tot.vars[name]['dim_name']:
                imap = Vars_tot.vars[name]['map']
                ireg = Site.loc[imap][isite]
                #p_len = 0
                #for ireg1 in Site.map['occupied_regions'][imap]:
                #    if ireg1 < ireg :
                #        p_len = p_len + Vars.vars['PFT']['dim_size'][imap][ireg1]
                ind = Vars_tot.vars['PFT']['indexes'][imap][ireg][isite]# + p_len
                ind = ind.tolist()

            else :
                ind = copy.copy((Vars_tot.vars['PFT_global']['indexes'][isite]).tolist())

        elif 'indice_region' in Vars_tot.vars[name]['dim_name']:
            imap = Vars_tot.vars[name]['map']
            ireg = Site.loc[imap][isite]
            ind = np.nonzero((np.array(Site.map['occupied_regions'][imap])==ireg).ravel())[0].tolist()

        elif var_pft[name] == 'pft' and var_site[name] == 'site':
            ind = Vars_tot.vars['PFT_site']['indexes'][isite].tolist()

        length = len(Opti.x[name])
        
        # Specific case of the historic variable : the indexes have to be duplicated for each
        # optimization iteration (except the first iteration)
        ind_hist = copy.copy(ind)
        if Opti.nloop >= 1:
            for i in range(Opti.nloop-1):
                #print i
                last = (np.add(ind,length*(i+1))).tolist()
                ind_hist.extend(last)
            

        #print name, length, ind, ind_hist, var_pft[name],var_site[name]
        
        ###print name, ' / dim : ',var_pft[name]
        out[name] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_time[name]), \
                     'dim_size': 2, 'value': np.take(Opti.x[name], ind, axis=0), \
                     'attr_name':['longname'], 'attr_value':['Values of '+name]}

        out[name+'_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_time[name]), \
                              'dim_size': 2, 'value': np.take(Opti.xprior[name], ind, axis=0), \
                              'attr_name':['longname'], 'attr_value':['Prior values of '+name]}
        
        
        out['hist_'+name] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop', var_pft[name],var_time[name]), \
                             'dim_size': 3, 'value': np.take(Opti.hist_x[name], ind_hist, axis=0), \
                             'attr_name':['longname'], 'attr_value':['Values of '+name]}
        
               
        out[name+'_SIG_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_time[name]), \
                                  'dim_size': 2, 'value': np.take(np.sqrt(Opti.B[name]), ind, axis=0), \
                                  'attr_name':['longname'], 'attr_value':['Prior SIGMA on '+name]}

        if Opti.Bpost_diag[name][0] >= 0:
            out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_time[name]), \
                                     'dim_size': 2, 'value': np.take(np.sqrt(Opti.Bpost_diag[name]),ind,axis=0), \
                                     'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}
        else:
            out[name+'_SIG_post'] = {'datatype': 'd', 'ndims':1, 'dim_name':(var_pft[name],var_time[name]), \
                                     'dim_size': 2, 'value': np.take(Opti.Bpost_diag[name],ind,axis=0), \
                                     'attr_name':['longname'], 'attr_value':['Posterior SIGMA on '+name]}

    # -- observation & uncertainties (prior & current)
    # -

    out['data_Rprior_diag'] = {'datatype': 'd', 'ndims':1, 'dim_name':('nobs',), \
                                   'dim_size': 1, 'value': Data.Rprior[Site.name[isite]], \
                                   'attr_name':['longname'], 'attr_value':['Prior covariance matrix on the observations (diagonal)']}


    obsnames = various.triname(Data.obsname_opti[isite], Data_def.obsnames_template)
    
    for name in obsnames:


        out[name+'_SIG_user'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                                 'dim_size': 1, 'value': (Data.vars[isite][name]['sigma_user'],), \
                                 'attr_name':['longname'], 'attr_value':['Prior user-defined SIGMA on '+name]}
        
        
        out[name+'_SIG_prior'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                                  'dim_size': 1, 'value': (Data.vars[isite][name]['sigma_prior'],), \
                                  'attr_name':['longname'], \
                                  'attr_value':['Prior SIGMA on '+name+' after modification with respect to the temporal sampling ' ]}

        out[name+'_SIG'] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                            'dim_size': 1, 'value': (Data.vars[isite][name]['sigma'],), \
                            'attr_name':['longname'], 'attr_value':['Current SIGMA on '+name]}


    # Names of the optimized parameters of this site
    out['opti_varnames'] = {'datatype': 'c', 'ndims':1, 'dim_name':('str_var',), \
                            'dim_size': 1, 'value': opti_varnames, \
                            'attr_name':['longname'], 'attr_value':['Name of the optimized parameters']}

    # -- misfit function
    # -
            
    out['nloop'] = {'datatype': 'i', 'ndims':1, 'dim_name':('parameter',), \
                    'dim_size': 1, 'value': Opti.nloop, \
                    'attr_name':['longname'], 'attr_value':['Number of iterations']}


    for name in obsnames:
        name_site = name+'_'+Site.name[isite]
        
        out['MFobs_'+name_site] = {'datatype': 'd', 'ndims':1, 'dim_name':('parameter',), \
                             'dim_size': 1, 'value': Opti.MFobs[name_site], \
                             'attr_name':['longname'], 'attr_value':['Value of the misfit function at the end of the optimization for '+name_site]}

        out['hist_MFobs_'+name_site] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop',), \
                                  'dim_size': 1, 'value': Opti.hist_MFobs[name_site], \
                                  'attr_name':['longname'], 'attr_value':['History of the misfit function values for '+name_site]}


    # -- Jacobian of the model at the minimum
    # -
    if Opti.scan_fmisfit_prior == False:
        out['Jacobian'] = {'datatype': 'd', 'ndims':2, 'dim_name':('n','nobs'), \
                           'dim_size': 2, 'value': Data.Jacobian_site[isite], \
                           'attr_name':['longname'], 'attr_value':['Local Jacobian matrix of ORCHIDEE at the minimum of the misfit function']}

        out['var_Bpost'] = {'datatype': 'd', 'ndims':2, 'dim_name':('n','n'), \
                            'dim_size': 2, 'value': Opti.Bpost_site[isite], \
                            'attr_name':['longname'], 'attr_value':['Local posterior covariance matrix on the parameters']}
        
    # -- gradient
    # -
    for name in obsnames:
        name_site = name+'_'+Site.name[isite]

        # Extract only the component related to the site
        hist_gradMF_obs = np.zeros((Opti.nloop,Opti.ns[isite]), np.float64)

        for loop in range(Opti.nloop-1):
            cnt = 0
            for ipar in Opti.indsite[isite]:
                hist_gradMF_obs[loop,cnt] = Opti.hist_gradMF['MFobs_'+name_site][loop][ipar]
                cnt=cnt+1
        
        out['hist_gradMFobs_'+name_site] = {'datatype': 'd', 'ndims':1, 'dim_name':('nloop','n'), \
                                           'dim_size': 2, 'value': hist_gradMF_obs, \
                                           'attr_name':['longname'], 'attr_value':['History of the values of the gradient of the misfit function for MFobs_'+name_site]}
        

     

    # --- Order of the parameters to write ---
    # ----------------------------------------
    var_order = ['PFT']
    for name in varnames:
        var_order.extend([name, name+'_prior', 'hist_'+name, name+'_SIG_prior', name+'_SIG_post'])

    for name in obsnames:
        var_order.extend([name+'_SIG_user',name+'_SIG_prior', name+'_SIG'])

    var_order.extend(['opti_varnames'])

    var_order.extend(['nloop'])

    var_order.extend(['data_Rprior_diag'])
    
    for name in obsnames:

        name_site = name+'_'+Site.name[isite]

        var_order.extend(['MFobs_'+name_site,'hist_MFobs_'+name_site])

        var_order.extend(['hist_gradMFobs_'+name_site])

    if Opti.scan_fmisfit_prior == False:
        var_order.extend(['Jacobian'])
        var_order.extend(['var_Bpost'])

    if Opti.scan_fmisfit_prior == True or Opti.scan_fmisfit_post == True:
        var_order = []
        for name in varnames:
            var_order.extend([name, name+'_prior', 'hist_'+name])
        var_order.extend(['nloop'])
        for name in obsnames:
            var_order.extend(['hist_MFobs_'+name])


   
    # --- Write the file ---
    # ----------------------
    
    
    # global attributes + dimensions
    io.writenc(ficname,gattr = gattr, dims = dims, dim_order = dim_order)
    for name in var_order:
        ###print name
        ###io.writenc(ficname, vars = {name:out[name]} , dim_order = dim_order, append = 1)
        io.writenc(ficname, vars = {name:out[name]} , append = 1)
                
# END write_optires
# ==============================================================================

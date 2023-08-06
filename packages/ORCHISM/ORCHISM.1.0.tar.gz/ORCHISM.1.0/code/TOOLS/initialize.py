#*******************************************************************************
# MODULE	: INITIALIZE
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 11/2007
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
Initialization of the various structures with default parameters, accounting for
 the user-defined characteristics
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import sys, os, glob
import copy
from orchis_config import Paras_def, Config, Data_def, Opti_def
import numpy as np

#from TOOLS import various, funcio, optimisation
import various, funcio, optimisation

# ==============================================================================
# Directories & exec files
# ------------------------------------------------------------------------------
def install(Site, options, file_def_assim):

    import os, io, glob, sys
    import time
    

    # - if batch mode activated
    # - will copy the data to WORKDIR, if it exists (normal case otherwise)
    if options.batch == True:
        
        WORKDIR = os.environ.get("WORKDIR")
        
        if WORKDIR != None:
            time_tag = time.strftime("%j-%H-%M-%S", time.gmtime())
            Config.PATH_MAIN_EXEC = os.path.join(WORKDIR,Site.PATH_EXEC+'_'+time_tag)
            
    else :
        Config.PATH_MAIN_EXEC = os.path.join(Config.PATH_MAIN,Site.PATH_EXEC)
        
    # --------------------------------------------------------------


    # - generate a unique pathname : year - day in year [0-366] - hour - minute
    time_tag = time.strftime("%Y-%j-%H-%M-%S", time.gmtime()) 
    
    Site.base_name={}
    Config.PATH_EXEC_SITE={}

    Config.PATH_MAIN_TMP = os.path.join(Config.PATH_MAIN_EXEC,'tmp')
    
    io.mkdir(Config.PATH_MAIN_TMP)

    for isite in range(Site.npts):
        
        Config.PATH_EXEC_SITE[isite] = os.path.join(Config.PATH_MAIN_EXEC,Site.name[isite])

        # - create the directories
        if len(glob.glob(Config.PATH_EXEC_SITE[isite])) == 0:
            io.mkdir(Config.PATH_EXEC_SITE[isite])


        # - create the symbolic links for ORCHIDEE, BFGS, and TARANTOLA_REF
        if len(glob.glob(os.path.join(Config.PATH_EXEC_SITE[isite],Config.exe_orchidee))) != 0:
            os.system('rm -f '+ os.path.join(Config.PATH_EXEC_SITE[isite],Config.exe_orchidee))
        
        os.system('ln -s '+
                  os.path.join(Config.PATH_MAIN,Config.exe_orchidee) + ' ' +
                  os.path.join(Config.PATH_EXEC_SITE[isite], Config.exe_orchidee))
            
        if options.exe_tl != None:
            if len(glob.glob(os.path.join(Config.PATH_EXEC_SITE[isite],Config.exe_orchidee_tl))) != 0:
                os.system('rm -f '+ os.path.join(Config.PATH_EXEC_SITE[isite],Config.exe_orchidee_tl))
            
            os.system('ln -s '+
                      os.path.join(Config.PATH_MAIN,Config.exe_orchidee_tl) + ' ' +
                      os.path.join(Config.PATH_EXEC_SITE[isite], Config.exe_orchidee_tl))

        
    if len(glob.glob(os.path.join(Config.PATH_MAIN_TMP,Config.exe_bfgs))) != 0:
        os.system('rm -f '+ os.path.join(Config.PATH_MAIN_TMP,Config.exe_bfgs))
    
    os.system('ln -s '+
              os.path.join(Config.PATH_MAIN,Config.exe_bfgs) + ' ' +
              os.path.join(Config.PATH_MAIN_TMP, Config.exe_bfgs))

    if len(glob.glob(os.path.join(Config.PATH_MAIN_TMP,Config.exe_tarantola))) != 0:
        os.system('rm -f '+ os.path.join(Config.PATH_MAIN_TMP,Config.exe_tarantola))

    os.system('ln -s '+
              os.path.join(Config.PATH_MAIN,Config.exe_tarantola) + ' ' +
              os.path.join(Config.PATH_MAIN_TMP, Config.exe_tarantola))


    # - copy the definition file to the output directory
    os.system('cp '+file_def_assim+'.py ' + Config.PATH_MAIN_EXEC)


    # - Print some informations -
    # ---------------------------
    
    print '\n################################################################\n'
    print '~~~~~~~~~~~~~ ORCHIS configuration parameters ~~~~~~~~~~~~~\n'
    print '# The execution directory is :'+Config.PATH_MAIN
    print '# Machine on which ORCHIS is running : '+ Config.machine
    print '# ORCHIDEE command line : '+ Config.cmde_orchidee
    if options.exe_tl != None:
        print '# ORCHIDEE_TL command line : '+ Config.cmde_orchidee_tl
    print '# BFGS command line : '+ Config.cmde_bfgs
    print '# TARANTOLA_REF command line : '+ Config.cmde_tarantola
    print
    print '# Name of the definition files for the chaining of the assimilations : '
    print '#  - '+file_def_assim
    
    print '\n\n# Processing the following sites : '
    for isite in range(len(Site.name)):
        print '  - ' + Site.name[isite] + '\n'
    print '\n'

    # --- Create the log ---
    logfile = open(os.path.join(Config.PATH_MAIN_EXEC,Config.orchis_logfile),'w',1)
    logfile.write( '\n################################################################\n')
    logfile.write( '~~~~~~~~~~~~~ ORCHIS configuration parameters ~~~~~~~~~~~~~\n')
    logfile.write( '# The execution directory is :'+Config.PATH_MAIN_EXEC+'\n')
    logfile.write( '# Machine on which ORCHIS is running : '+ Config.machine+'\n')
    logfile.write( '# ORCHIDEE command line : '+ Config.cmde_orchidee+'\n')
    if options.exe_tl != None:
        logfile.write( '# ORCHIDEE_TL command line : '+ Config.cmde_orchidee_tl+'\n')
    logfile.write( '# BFGS command line : '+ Config.cmde_bfgs+'\n')
    logfile.write( '# TARANTOLA_REF command line : '+ Config.cmde_tarantola+'\n\n')
    logfile.write( '# Name of the definition files for the chaining of the assimilations : \n')
    logfile.write( '#  - '+file_def_assim+'\n')
    
    logfile.write( '\n\n# Processing the following sites : \n')
    for isite in range(len(Site.name)):
        logfile.write( '  - ' + Site.name[isite] + '\n')
    logfile.write('\n\n')

   
    
    # - Define the name of the main output files -
    # --------------------------------------------

    site_ficout = []
    for key in dir(Site):
        if key[0:10] == 'ORCHIS_OUT': site_ficout.append(key)

    for ficname in Config.fic_out:

        if ficname in site_ficout: # name defined by user
            exec(ficname+'=os.path.join(Config.PATH_MAIN_EXEC,Site.'+ficname+')')
        else:                      # default names are used
            exec(ficname+'=os.path.join(Config.PATH_MAIN_EXEC,Config.'+ficname+')')
        
    print 'Name of the output files :'
    print ' + ORCHIS_OUT_SITES_REGIONS           :',ORCHIS_OUT_SITES_REGIONS
    print ' + ORCHIS_OUT_OPTI_RES                :',ORCHIS_OUT_OPTI_RES
    print ' + ORCHIS_OUT_OPTI_VAR                :',ORCHIS_OUT_OPTI_VAR
    print ' + ORCHIS_OUT_FLUX_POSTERIOR          :',ORCHIS_OUT_FLUX_POSTERIOR
    print ' + ORCHIS_OUT_FLUX_PRIOR              :',ORCHIS_OUT_FLUX_PRIOR
    print ' + ORCHIS_OUT_OPTI_OBSNSIM            :',ORCHIS_OUT_OPTI_OBSNSIM
    print ' + ORCHIS_OUT_RMSE_PRIOR              :',ORCHIS_OUT_RMSE_PRIOR
    print ' + ORCHIS_OUT_RMSE_POSTERIOR          :',ORCHIS_OUT_RMSE_POSTERIOR
    print ' + ORCHIS_OUT_SENSI_MF_PRIOR          :',ORCHIS_OUT_SENSI_MF_PRIOR
    print ' + ORCHIS_OUT_SENSI_MF_POST           :',ORCHIS_OUT_SENSI_MF_POST
    print ' + ORCHIS_OUT_OPTI_SCAN_FMISFIT_PRIOR :',ORCHIS_OUT_SCAN_FMISFIT_PRIOR
    print ' + ORCHIS_OUT_OPTI_SCAN_FMISFIT_POST  :',ORCHIS_OUT_SCAN_FMISFIT_POST
    print ' + ORCHIS_OUT_ERPOST_MATCOVVAR        :',ORCHIS_OUT_ERPOST_MATCOVVAR
    print ' + ORCHIS_OUT_ERPOST_MATCORVAR        :',ORCHIS_OUT_ERPOST_MATCORVAR
    print ' + ORCHIS_OUT_GRADMF_VS_EPS           :',ORCHIS_OUT_GRADMF_VS_EPS
    print 
    
    
    logfile.write('\n')
    logfile.write( 'Name of the output files :'+'\n')
    logfile.write( ' + ORCHIS_OUT_SITES_REGIONS           :'+ORCHIS_OUT_SITES_REGIONS+'\n')
    logfile.write( ' + ORCHIS_OUT_OPTI_RES                :'+ORCHIS_OUT_OPTI_RES+'\n')
    logfile.write( ' + ORCHIS_OUT_OPTI_VAR                :'+ORCHIS_OUT_OPTI_VAR+'\n')
    logfile.write( ' + ORCHIS_OUT_FLUX_POSTERIOR          :'+ORCHIS_OUT_FLUX_POSTERIOR+'\n')
    logfile.write( ' + ORCHIS_OUT_FLUX_PRIOR              :'+ORCHIS_OUT_FLUX_PRIOR+'\n')
    logfile.write( ' + ORCHIS_OUT_OPTI_OBSNSIM            :'+ORCHIS_OUT_OPTI_OBSNSIM+'\n')
    logfile.write( ' + ORCHIS_OUT_RMSE_PRIOR              :'+ORCHIS_OUT_RMSE_PRIOR+'\n')
    logfile.write( ' + ORCHIS_OUT_RMSE_POSTERIOR          :'+ORCHIS_OUT_RMSE_POSTERIOR+'\n')
    logfile.write( ' + ORCHIS_OUT_SENSI_MF_PRIOR          :'+ORCHIS_OUT_SENSI_MF_PRIOR+'\n')
    logfile.write( ' + ORCHIS_OUT_SENSI_MF_POST           :'+ORCHIS_OUT_SENSI_MF_POST+'\n')
    logfile.write( ' + ORCHIS_OUT_OPTI_SCAN_FMISFIT_PRIOR :'+ORCHIS_OUT_SCAN_FMISFIT_PRIOR+'\n')
    logfile.write( ' + ORCHIS_OUT_OPTI_SCAN_FMISFIT_POST  :'+ORCHIS_OUT_SCAN_FMISFIT_POST+'\n')
    logfile.write( ' + ORCHIS_OUT_ERPOST_MATCOVVAR        :'+ORCHIS_OUT_ERPOST_MATCOVVAR+'\n')
    logfile.write( ' + ORCHIS_OUT_ERPOST_MATCORVAR        :'+ORCHIS_OUT_ERPOST_MATCORVAR+'\n')
    logfile.write( ' + ORCHIS_OUT_GRADMF_VS_EPS           :'+ORCHIS_OUT_GRADMF_VS_EPS+'\n')




    # - Definition of output files for each site -
    # --------------------------------------------
    #  It's basically the same as above, except for the site number added at the end
    for ficname in Config.fic_out:


        exec("Config."+ficname+'='+ficname)

##         under = '_'
##         point = '.'
##         exec(ficname+'_site={}')
##         exec('tmp=len('+ficname+')')
##         exec('end='+ficname+'[tmp-3:tmp]')
##         if end == '.nc':
##             for isite in range(Site.npts):
##                 exec(ficname+'_site[isite]='+ficname+'[0:tmp-3]+under+Site.name[isite]+end')
##         elif end == 'txt':
##             for isite in range(Site.npts):
##                 exec(ficname+'_site[isite]='+ficname+'[0:tmp-4]+under+Site.name[isite]+point+end')
##         else:
##             sys.exit('Error in the name of output file :'+ficname)

        exec("Config."+ficname+'_site={}')
        for isite in range(Site.npts):
            exec('buf ='+ficname)
            buf = os.path.splitext(buf)
            buf = buf[0]+'_'+Site.name[isite]+buf[1]
            cmde= "Config."+ficname+"_site[isite]='"+buf+"'"
            exec(cmde)

    # Return
    return logfile


# END directories
# =============================================================================



# ==============================================================================
# Site informations
# ------------------------------------------------------------------------------
def sites(Site, Paras, Data):

    import glob, copy, sys
    from orchis_config import Data_def, Config
    import numpy as np
    
 
    
    # --- Default sites' name, coordinates and PFT ------
    def_name = []
    def_loc = []
    def_indice_pft = []
    def_lat = []
    def_lon = []

    fic_site = Config.fic_site_def
    if 'fic_site' in dir(Site): fic_site=Site.fic_site

    fic = open(fic_site,'ru')

    lignes = fic.readlines()

    for iligne in range(len(lignes)-1):
        data = (lignes[iligne+1].strip()).split()

        if data==[]: break
        # Site name
        def_name.append(data[0])

        # Site coordinates
        def_lat.append(float(data[2]))
        def_lon.append(float(data[3]))

        # Site PFTs
        def_indice_pft.append(eval(data[4]))

        # Site configuration and flux files
        # Format of configuration file : Config_path/Site-name_year.cfg
        #def_fic_cfg[iligne] = Site.path_config+data[5]
        #Site.path_cfg+data[1]+'_'+Site.period+'.cfg'

        # Format of configuration file : Obs_path/Site-name_year_flux_obs.nc
        #def_fic_obs[iligne] = Data.path_flux+Site.period+data[1]+'_flux_obs.nc'


    # --- Accounting for user defined site characteristics

    # - no user defined values: copy default values
    Site.name2 = def_name
    Site.indice_pft2 = def_indice_pft
    Site.lat2 = def_lat
    Site.lon2  = def_lon

    # - user defined values: fill missing informations with default values
    if 'site_names'  in dir(Site):
        keys = ['name','indice_pft','lat','lon']
        npts = len(Site.site_names)
        for key in keys : exec("Site."+key+"=[]")
        for isite in range(npts):
            site_name = Site.site_names[isite]
            if site_name in Site.name2:
                print site_name + ' found'
                ind = Site.name2.index(site_name)
                for key in keys : exec("Site."+key+".append(Site."+key+"2[ind])")
                    

    # -- Number of sites
    Site.npts = len(Site.name)

    # check compatibility with number of cases identified in the Data class

    if len(Data.case) != Site.npts: sys.exit('STOP / INITIALIZE : Coco, y a un probleme dans le nombre de sites a traiter')


    # -- forcing files & time dependency
    Site.time = {} 
    Site.fic_forc = []
    Site.fic_cfg = []

    
    sys.path.append(Data.path_defsite)
    for isite in range(len(Data.case)):
        Site.time[isite] = {}

        print "import "+Data.case[isite]
        exec("from " +Data.case[isite]+" import Data_site")

        Site.fic_cfg.append(Data_site.fic_cfg)
        Site.fic_forc.append(Data_site.fic_forc)
        Site.time[isite]['nannees']   = Data_site.nannees
        Site.time[isite]['nmois']     = Data_site.nmois
        Site.time[isite]['njours']    = Data_site.njours
        Site.time[isite]['nsemaines'] = Data_site.nsemaines



    sys.path.remove(Data.path_defsite)


    # === Regions ===================================================================

    Site.depreg = 0
    for pname in Paras.vars.keys():

        Site.depreg = Site.depreg + Paras.vars[pname]['dims']['indice_region']

    if Site.depreg > 0:

        Site.depreg = 1

        # -- Check if auto_map is specified in the definition file
        try:
            Site.auto_map
        except:
            Site.auto_map = Config.auto_map
    
        # -- Dictionary of maps of regions
        Site.map = {}
        Site.map['number_regions'] = {}
        Site.map['lon_min'] = {}
        Site.map['lon_max'] = {}
        Site.map['lat_min'] = {}
        Site.map['lat_max'] = {}
        Site.map['occupied_regions'] = {}
        Site.site_ind = {}
        Site.npts_reg = {}
        Site.loc = {}

        #print Site.auto_map
    
        # --- Automatic mode : with maps, the system build all the sites data, locations, etc.
        if Site.auto_map == 1:
        
            for imap in range(Site.nmaps):
                fic = open(Site.path_maps+'map'+str(imap+1)+'.txt','ru')
                lignes = fic.readlines()
                Site.map['number_regions'][imap] = len(lignes)-1
                Site.map['lon_min'][imap] = []
                Site.map['lon_max'][imap] = []
                Site.map['lat_min'][imap] = []
                Site.map['lat_max'][imap] = []
                for iligne in range(len(lignes)-1):
                    data = (lignes[iligne+1].strip()).split()
                    Site.map['lon_min'][imap].append(float(data[1]))
                    Site.map['lon_max'][imap].append(float(data[2]))
                    Site.map['lat_min'][imap].append(float(data[3]))
                    Site.map['lat_max'][imap].append(float(data[4]))
                    
            # Check which maps will be actually used (if there region-dependent parameters !!)
            Site.real_maps = [] # <-- this list contains only the indexes of used maps
            for imap in range(Site.nmaps):
                aru = 0
                for pname in Paras.vars.keys():
                    if Paras.vars[pname]['dims']['indice_region'] == imap+1: aru=aru+1
                if aru >= 1 : Site.real_maps.append(imap)

    
            # -- Sites indexes for each region in each map
        
            for imap in Site.real_maps:
                Site.site_ind[imap]={}
                Site.loc[imap]={}
                for ireg in range(Site.map['number_regions'][imap]):
                    Site.site_ind[imap][ireg] = []
            for isite in range(Site.npts):
                # Check if the site is in one region
                for imap in Site.real_maps:
                    check = 0
                    for ireg in range(Site.map['number_regions'][imap]):
                        if Site.lat[isite]>=Site.map['lat_min'][imap][ireg] and \
                                Site.lat[isite]<Site.map['lat_max'][imap][ireg] and \
                                Site.lon[isite]>=Site.map['lon_min'][imap][ireg] and \
                                Site.lon[isite]<Site.map['lon_max'][imap][ireg] :
                            Site.site_ind[imap][ireg].append(isite) #-memorize the index of the sites in the region
                            Site.loc[imap][isite]=ireg              #-reverse : for each site memorize which region the belong to
                                                                #-depending on the map (useful for Vars_site in orchis.py)
                            check = check + 1
                    if check == 0 :
                        print
                        print 'WARNING : The site '+Site.name[isite]+' does not belong to any region, it will be ignored'
                    if check >= 2 : sys.exit('ERROR : In the map '+str(imap+1)+', at least '+str(check)+' regions are overlapping !!')

            # Number of sites in each region
            for imap in Site.real_maps:
                Site.npts_reg[imap] = {}
                for ireg in range(Site.map['number_regions'][imap]):
                    Site.npts_reg[imap][ireg] = len(Site.site_ind[imap][ireg])
           
    
            # Check which regions are actually occupied by one or more site
            for imap in Site.real_maps:
                Site.map['occupied_regions'][imap] = []
                for ireg in range(Site.map['number_regions'][imap]):
                    if Site.npts_reg[imap][ireg] != 0 : Site.map['occupied_regions'][imap].append(ireg)


        # --- Manual mode : one map, one region (for now)
        else:
            Site.real_maps = [0]
            Site.map['number_regions'][0] = 1
            Site.loc[0]={}
            Site.site_ind[0]={}
            Site.npts_reg[0]={}
            for isite in range(Site.npts):
                Site.loc[0][isite] = 0
            Site.site_ind[0][0] = (np.arange(Site.npts)).tolist()
            Site.npts_reg[0][0] = Site.npts
            Site.map['occupied_regions'][0] = [0]


        print Site.real_maps
    
# END sites
# =============================================================================


  
# ==============================================================================
# Parameter characteristics
# ------------------------------------------------------------------------------
def paras(Site,Paras):

    print 'Je suis mesozoic'

    from orchis_config import Paras_def, Config
    from TOOLS import various
    import copy
    import numpy as np, MA

    # -- Name of the file containing background and first guess information
    # on the parameters
    # !! SK It has to be defined for all the sites, or none.
    # -- Prior values of parameters (if specified)
    if 'fic_val_xbg' not in dir(Paras):
        Paras.fic_val_xbg = Paras_def.fic_val_xbg
        #Paras.fic_val_xbg = {}
        #for isite in range(Site.npts): Paras.fic_val_xbg[isite] = Paras_def.fic_val_xbg
        

    if 'fic_val_xfg' not in dir(Paras):
        Paras.fic_val_xfg = Paras_def.fic_val_xfg
        #Paras.fic_val_xfg = {}
        #for isite in range(Site.npts): Paras.fic_val_xfg[isite] = Paras_def.fic_val_xfg


    print 'Background  values : ',Paras.fic_val_xbg
    print 'First guess values : ',Paras.fic_val_xfg

    for isite in range(Site.npts):

        #print 'Background  values, ', Site.name[isite], ' : ',Paras.fic_val_xbg[isite]
        #print 'First guess values, ',Site.name[isite],' : ',Paras.fic_val_xfg[isite]

    
        # -- Get the PFTs for which assimilation is conducted if not defined

        if Site.indice_pft[isite] == None or len(Site.indice_pft[isite]) == 0:

            # get the values in the .CFG file
            fic_cfg = open(Site.fic_cfg[isite], 'rU')
            indice_pft=[]
            veget=[]
            for ligne in fic_cfg:
                if ligne.strip()[0:12]=='SECHIBA_VEG_' :
                    buf = ligne.strip().split(':')[-1]
                    veget.extend([float(buf)])                            
            fic_cfg.close()
            map(float,veget)
            for i in range(len(veget)):
                if i> 0 and veget[i]>0: indice_pft.extend([i+1])
        
            # remove the soil-PFT
            if indice_pft[0] == 0: indice_pft.pop(0)

            Site.indice_pft[isite][:] = indice_pft[:]
            print ' #'
            print ' # WARNING : Site.indice_pft was not defined in the definition file'
            print ' # WARNING : Site.indice_pft has been infered from the .CFG file'
            print ' # WARNING : Site.indice_pft =',indice_pft
            print ' #'
            
    # -- Dimensions for the NetCDF file
    ### ORIGINAL / DEBUG : pb dimension nannees qui varie avec le site
    ### Paras.dims = {'npts':Site.npts, 'indice_pft':Site.indice_pft, 'nannees': Site.nannees}
    Paras.dims = {'npts':Site.npts, 'indice_pft':Site.indice_pft} #, 'nannees': Site.nannees}
    
    # -- Sorting of the variable names
    Paras.varname = various.triname(Paras.vars.keys(), Paras_def.parnames_template)

    # -- Check the PFT variation for some variables (Gsslope, LAIMAX, SLA, Leafage, Frespc)
    #    if no PFT dimension is provided for one of these variables, then a single multiplicative
    #    factor of the prior parameter value, for all PFTs, is estimated for the corresponding
    #    variable
    opti_varname = []
    all_varname = various.triname(Paras.vars.keys(), Paras_def.parnames_template)

    for name in Paras.varname:
        if ( name in Paras_def.varname_pft ):
            if Paras.vars[name]['dims']['indice_pft'] == 0 and Paras_def.vars[name]['pft'] == 'y':
                opti_varname.append('K'+name)
                all_varname.append('K'+name)
                             
                Paras.vars['K'+name] = {}
                Paras.vars['K'+name]['dims']=copy.deepcopy(Paras.vars[name]['dims'])
                Paras.vars[name]['dims']['indice_pft'] = 1
                
            else:
                opti_varname.append(name)
        else:
            opti_varname.append(name)

        # -- Saving the original dependence on pft
        Paras.vars[name]['pft']=copy.deepcopy(Paras_def.vars[name]['pft'])


    Paras.opti_varname = opti_varname

    # -- Bounds, sigma, eps, prior value
    keys_def = Paras_def.vars['Vcmax_opt']

    for name in all_varname:

        # - All fields
        for key_def in keys_def:

            if key_def not in Paras.vars[name].keys():
                Paras.vars[name][key_def] = Paras_def.vars[name][key_def]

                # SK : no adapted for now in multisite, later maybe...
                
                # if a value is provided => define an array with the right REGION, PFT, and SITE dimension
                #             elif key_def == 'value':
                
                #                 tmp = np.array(Paras.vars[name][key_def], np.float64)
                
                #                 # if there is more than one landpoint (even if the value is the same for all landpoints)
                #                 if 'npts' in Paras.vars[name]['dims'].keys() and Paras.vars[name]['dims']['npts'] > 1:
                #                     print Paras.vars[name]['dims'].keys()
                #                     value = np.zeros((ssize, len(Site.indice_pft), tsize), np.float64)
                #                     for ipft in range(len(Site.indice_pft)):
                #                         value[:,ipft,:] = tmp[ipft]
                #                 # if only one landpoint
                #                 else:
                #                     value = np.zeros(( len(Site.indice_pft), tsize), np.float64)
                #                     for ipft in range(len(Site.indice_pft)):
                #                         value[ipft,:] = tmp[ipft]
                
                #                 Paras.vars[name]['value'] = value

        # - Sigma : by default, sigma equal to sigma_pc % times the range of variation for each parameter
        # - Sigma is now defined in prior.detprior_paras

    # values of eps used to compute the variation of the misfit function gradiant to eps
    if 'test_gradMF_vs_eps' not in dir(Paras):    Paras.test_gradMF_vs_eps = Paras_def.test_gradMF_vs_eps
    if 'eps_val' not in dir(Paras):    Paras.eps_val = Paras_def.eps_val

# END paras
# ==============================================================================


# ==============================================================================
# Data characteristics
# ------------------------------------------------------------------------------
def data(Data, Site, logfile): ###nyears, npts):


    # --- Add temporarily the path containing the sites' definition files
    if len(glob.glob(Data.path_defsite)) == 0:
        sys.exit('INITIALIZE: the path to the definition files for the assimilations cases do not exist : '+Data.path_defsite)
    sys.path.append(Data.path_defsite)


    # --- Import global variables of the class Data (i.e. not site specific)
    for key in dir(Data_def):
        #if key[0] != '_' or key[0] != 'name' or key[0] != 'diurnal':
        if key[0] not in [ '_','name','diurnal']:
            if key != 'vars' and key not in dir(Data):
                exec('Data.'+key+'=Data_def.'+key)

    
    # ---  Site specific informations
    Data.obsname = {}
    Data.vars = {}
    Data.diurnal = {}
    #Data.time = {}
    Config.SWdown = {}

    Config.dn_diff = Data.dn_diff

    for isite in range(len(Data.case)):     

        Data.vars[isite] = {}
        #Data.time[isite] = {}

        # - Import site definition file
    
        print "import "+Data.case[isite]
        exec("from " +Data.case[isite]+" import Data_site")
        
        # - Names of the variables to assimilate
        Data.obsname[isite] =  various.triname(Data_site.obsname, Data_def.obsnames_template)

        # - Variables' characteristics
        for name in Data_site.obsname:
        
            # - default values
            if name not in Data_site.vars.keys(): 
                Data.vars[isite][name] = copy.copy(Data_def.vars[name])
                                
            # - user define values
            else:
                Data.vars[isite][name] = {}
                for elem in Data_def.vars[name].keys():
                    # - default values
                    if elem not in Data_site.vars[name].keys():
                        Data.vars[isite][name][elem] = copy.copy(Data_def.vars[name][elem])
                    # - user defined values
                    else:
                        Data.vars[isite][name][elem] = copy.copy(Data_site.vars[name][elem])

        # - Diurnal processing characteristics
        # default values
        if 'diurnal' not in dir(Data_site):
            Data.diurnal[isite] = copy.copy(Data_def.diurnal)
        # user defined values
        else:
            for elem in Data_def.diurnal.keys():
                if elem not in Data_site.diurnal.keys():
                    Data.diurnal[isite][elem] = copy.copy(Data_def.diurnal[elem])
                else:
                    Data.diurnal[isite][elem] = copy.copy(Data_site.diurnal[elem])

    # --- Remove the path containing the sites' definition files    
    sys.path.remove(Data.path_defsite)
    
    # --- Name of the observations finally accounted for in optimization
    Data.obsname_opti = copy.deepcopy(Data.obsname)

    # --- Determine the temporal windows for the diurnal cycles sampling
    #
    for isite in range(len(Data.case)):     

        # - Test if one observation processing is set to diurnal
        for name in Data.obsname[isite]:
            if 'diurnal' in Data.vars[isite][name]['processing_obs'] and 'diurnal' in Data.vars[isite][name]['processing_sim']:
                Data.diurnal[isite]['test'] = True
                break

        
        # -  Manage diurnal observations
        if Data.diurnal[isite]['test'] == False:
            Data.diurnal[isite]['start'] = None
            Data.diurnal[isite]['length'] = None

        else:
            
            nyears = Site.time[isite]['nannees']

            # - Define the unit and length for each period
            if Data.diurnal[isite]['month'] != None: # user defined sequence of months
                cycle_unit = 'm'            
                cycle_length = 1
                Data.diurnal[isite]['period'] = 1

            if Data.diurnal[isite]['month'] == None: # weekly or monthly cycles

                cycle_unit = Data.diurnal[isite]['length'][1].lower()
                cycle_length = int(Data.diurnal[isite]['length'][0])
                if cycle_unit != 'w' and cycle_unit != 'm':
                    sys.exit('# STOP. INITIALIZE : the unit for the sampling of the diurnal cycle must be W or M')

                # The cycle length must be higher than the periodicity
                if cycle_length > Data.diurnal[isite]['period']: Data.diurnal[isite]['period'] = cycle_length
            

                if cycle_unit == 'm': # if monthly cycles, define the correct month sequence
                    Data.diurnal[isite]['month'] = []
                    for im in range(0,12*nyears, Data.diurnal[isite]['period']):
                        Data.diurnal[isite]['month'].append((Config.month_name*nyears)[im])
                              
            
            # - Define the start and length for each sequence
            Data.diurnal[isite]['start'] = []  
            Data.diurnal[isite]['length'] = [] 
                

            # - Weekly cycles
            if cycle_unit == 'w':

                days_in_week = 7
           
                start_week = [0]
                for iy in range(nyears):
                    for id in range(0,365,days_in_week):
                        start_week.append(start_week[-1]+days_in_week)
                        
                for iw in range(0,nyears*53+1, Data.diurnal[isite]['period']):
                    Data.diurnal[isite]['start'].append(start_week[iw])
                    Data.diurnal[isite]['length'].append(cycle_length*days_in_week)            

             
            # - Monthly cycles
            if cycle_unit == 'm':
           
                ind_month = []
                for elem in Data.diurnal[isite]['month']: ind_month.append(Config.month_name.index(elem))
                month_name = Data.diurnal[isite]['month'][:]

                count_start = 0
                for iy in range(nyears):
                    ipos = 0
                    for im in range(12):
                        if im in ind_month:
                            Data.diurnal[isite]['start'].append(count_start)
                            
                            mlength = Config.month_length[im:im+cycle_length]
                            Data.diurnal[isite]['length'].append(sum(mlength))
                            
                            ind_month.pop(0)
                            month_name.pop(0)
                       
                        count_start = count_start+Config.month_length[im]


        # --- If separation of the fluxes wrt daytime and nighttime observations,
        test_day_vs_night = False
        for name in Data.obsname[isite]:
            if 'day_vs_night' in Data.vars[isite][name]['processing_obs']:  test_day_vs_night = True
    
        if test_day_vs_night == True:

            # - define the Data.vars structure for nighttime observations
            obsname = []
            for name in Data.obsname[isite]:
                obsname.append(name)
                if 'day_vs_night' in Data.vars[isite][name]['processing_obs']:
                    obsname.append(name+'_night')

                    if name+'_night' not in Data.vars[isite]:  Data.vars[isite][name+'_night'] = {}
                
                    #  By default : night variables have the same attributes than day variables
                    for elem in Data.vars[isite][name].keys():
                        if elem not in Data.vars[isite][name+'_night']:
                            Data.vars[isite][name+'_night'][elem] = Data.vars[isite][name][elem]

                    # Define the correction factor for sigma
                    #if isite == 0: Data.corr_sigma_obs[name+'_night'] =  Data.corr_sigma_obs[name]/Data.vars[isite][name]['coef_error_night']
                    Data.corr_sigma_obs[name+'_night'] =  Data.corr_sigma_obs[name]
            
            Data.obsname_opti[isite] = copy.deepcopy(obsname)
        
            # - reading of the forcing file
            #if Data.var_rad['SWdown']['fic_obs'] == None:  
            #    sys.exit('\n The separation of daytime vs nighttime observations is required and yet no forcing file name has been provided')

            var_rad_name = Data_def.var_rad_name

            for key in Data_def.var_rad[var_rad_name].keys():
                # default values
                if key not in Data.var_rad[var_rad_name]:
                    Data.var_rad[var_rad_name][key] = Data_def.var_rad[var_rad_name][key]
            
            info_rad = {}
            info_rad[0] = {}
            info_rad[0]['name'] = Site.fic_forc[isite]
            info_rad[0]['vars'] = [var_rad_name]
            ans = funcio.get_data(info_rad,
                                  isite,
                                  logfile,
                                  ndays = Site.time[isite]['njours'],
                                  nyears = Site.time[isite]['nannees'], 
                                  vars_info = Data.var_rad,
                                  case = 'obs')
            Config.SWdown[isite] = ans['SWdown']

            Config.SWdown_threshold = Data.var_rad['SWdown']['threshold']


        #--- Manage diurnal observations

        if Data.diurnal[isite]['test'] == True:
            obsname = []
            for name in Data.obsname[isite]:

                obsname.append(name)

                if 'diurnal' in Data.vars[isite][name]['processing_obs'] and 'diurnal' in Data.vars[isite][name]['processing_sim']:
                    
                    obsname.append(name+'_diurnal')
                    
                    if name+'_diurnal' not in Data.vars[isite]:  Data.vars[isite][name+'_diurnal'] = {}
                    
                    #  By default : diurnal variables have the same attributes than daily variables
                    for elem in Data.vars[isite][name].keys():
                        if elem not in Data.vars[isite][name+'_diurnal']:
                            Data.vars[isite][name+'_diurnal'][elem] = Data.vars[isite][name][elem]
                        
                    # Change the processing for name and name_diurnal
                    tempo_res = (Data.vars[isite][name]['processing_obs'].split('_diurnal'))[0]
                    Data.vars[isite][name]['processing_obs'] = tempo_res
                    Data.vars[isite][name]['processing_sim'] = tempo_res
                    Data.vars[isite][name+'_diurnal']['processing_obs'] = 'diurnal'
                    Data.vars[isite][name+'_diurnal']['processing_sim'] = 'diurnal'

            Data.obsname_opti[isite] = obsname

        
    # --- Copy the user defined uncertainties on observations
    for isite in range(len(Data.case)):
        for name in Data.obsname_opti[isite]:
            Data.vars[isite][name]['sigma_user'] = copy.copy(Data.vars[isite][name]['sigma'])               
    




    # --- correction coefficient to apply to each observation
    obsnames_all = []
    for isite in range(len(Data.case)):
        for name in Data.obsname_opti[isite]:
            if name not in obsnames_all: obsnames_all.append(name)

    # if not supplied in the definition file, use the default values
    for name in obsnames_all:
        if name not in Data.corr_sigma_obs: Data.corr_sigma_obs[name] = Data_def.corr_sigma_obs[name]


    

    # --- Create the dictionary "processing" regrouping the specific treatments
    #     to apply to each variable
    #
    # Data.processing[processing_name]['vars']    -> variables affected by this type of processing
    #                                 ['indices'] -> indices
    #                                 ['n_ts']    -> number of obs of this processing type


    Data.processing = {}

    for isite in range(len(Data.case)):

        Data.processing[isite] = {}
        
        Data.processing[isite]['obs'] = {} # processing for the input observation files
        Data.processing[isite]['sim'] = {} # processing for the ORCHIDEE simulation files  

        process_list_obs = []
        process_list_sim = []

        for name in Data.obsname_opti[isite]:
            if Data.vars[isite][name]['processing_obs'] not in process_list_obs:
                process_list_obs.append(Data.vars[isite][name]['processing_obs'])
            if Data.vars[isite][name]['processing_sim'] not in process_list_sim:
                process_list_sim.append(Data.vars[isite][name]['processing_sim'])


        for pname in process_list_obs:
            Data.processing[isite]['obs'][pname] = {}
            Data.processing[isite]['obs'][pname]['vars'] = []
        
        for pname in process_list_sim:
            Data.processing[isite]['sim'][pname] = {}
            Data.processing[isite]['sim'][pname]['vars'] = []
        
        
        for name in Data.obsname_opti[isite]:
            ind = process_list_obs.index(Data.vars[isite][name]['processing_obs'])
            Data.processing[isite]['obs'][process_list_obs[ind]]['vars'].append(name)
        
            ind = process_list_sim.index(Data.vars[isite][name]['processing_sim'])
            Data.processing[isite]['sim'][process_list_sim[ind]]['vars'].append(name)


#END data                                
# ==============================================================================


# ==============================================================================
# Observations and ORCHIDEE output files characteristics
#
# Create the dictionary "fic" regrouping the specific informations
#     on the input files to read
# ------------------------------------------------------------------------------
def files(Data, fileout = None):
  
    if fileout == None:

        Data.fic = {}
        
        for isite in range(len(Data.case)):

            Data.fic[isite] = {}
            
            obs_list = []
            sim_list = []
            
            for name in Data.obsname_opti[isite]:
                if Data.vars[isite][name]['fic_obs'] not in obs_list: obs_list.append(Data.vars[isite][name]['fic_obs'])
                if Data.vars[isite][name]['fic_sim'] not in sim_list: sim_list.append(Data.vars[isite][name]['fic_sim'])
            
            # observation files
            Data.fic[isite]['obs'] = {}
            icnt = 0 
            for fname in obs_list:
                Data.fic[isite]['obs'][icnt] = {}
                Data.fic[isite]['obs'][icnt]['name'] = fname
                Data.fic[isite]['obs'][icnt]['vars'] = []
                for name in Data.obsname_opti[isite]:
                    if fname in Data.vars[isite][name]['fic_obs']:
                        Data.fic[isite]['obs'][icnt]['vars'].append(name)
                        
                icnt=icnt+1
                
            # simulation files
            Data.fic[isite]['sim'] = {}
            icnt = 0 
            for fname in sim_list:
                Data.fic[isite]['sim'][icnt] = {}
                Data.fic[isite]['sim'][icnt]['name'] = os.path.join(Config.PATH_EXEC_SITE[isite],fname)
                Data.fic[isite]['sim'][icnt]['vars'] = []
                for name in Data.obsname_opti[isite]:
                    if fname in Data.vars[isite][name]['fic_sim']:
                        Data.fic[isite]['sim'][icnt]['vars'].append(name)
                        
                icnt=icnt+1



#END files                   
# ==============================================================================




# ==============================================================================
# Optimization characteristics
# ------------------------------------------------------------------------------
def opti(Opti):


    # --- Get the default parameters
    for key in dir(Opti_def):
        if key[0] != '_' and key not in dir(Opti):
            exec('Opti.'+key+'=Opti_def.'+key)

#END opti
# ==============================================================================



# ==============================================================================
# BFGS characteristics
# ------------------------------------------------------------------------------
def bfgs(Opti):

    
    # -- Define startup values of the BFGS parameters --
       
    Opti.BFGS['nbd'] = np.zeros(Opti.n,np.int32)
    for i in range(Opti.n):
        if Opti.chi_lb['all'][i] not in Config.missval and Opti.chi_ub['all'][i] not in Config.missval:
            Opti.BFGS['nbd'][i] = 2
        if Opti.chi_lb['all'][i] in Config.missval and Opti.chi_ub['all'][i] not in Config.missval:
            Opti.BFGS['nbd'][i] = 3
        if Opti.chi_lb['all'][i] not in Config.missval and Opti.chi_ub['all'][i] in Config.missval:
            Opti.BFGS['nbd'][i] = 1


    # BFGS working arrays
    Opti.BFGS['size_wa'] = (2* Opti.BFGS['m']+4)*Opti.n+12* Opti.BFGS['m']* Opti.BFGS['m']+12* Opti.BFGS['m']
    Opti.BFGS['size_iwa'] = 3*Opti.n
    
    Opti.BFGS['wa'] = np.zeros(Opti.BFGS['size_wa'],np.float64)
    Opti.BFGS['iwa'] = np.zeros(Opti.BFGS['size_iwa'],np.int32)
    Opti.BFGS['isave'] = np.zeros(Opti.BFGS['size_isave'],np.int32)
    Opti.BFGS['dsave'] = np.zeros(Opti.BFGS['size_dsave'],np.float64)
    Opti.BFGS['lsave'] = np.array([0, 0, 0, 0])

    # history of the BFGS tasks
    Opti.BFGS['task_hist'] = [Opti.BFGS['task'][:]]

    
#END bfgs
# ==============================================================================



# ==============================================================================
# Re-initialize some Optimization parameters if needed
# ------------------------------------------------------------------------------
def reboot(Opti, Vars):

    
    # - Remplace current parameter values with the a priori ones
    for name in Vars.vars['opti_varname']:
        # - Vars
        Vars.vars[name]['value'] = Vars.vars[name]['prior']
        # - Opti
        Opti.x[name]  = Opti.xprior[name]
    optimisation.transfovar(Vars, Opti, mode = 'forward', xonly = 'y')
    optimisation.initopti(Vars, Opti, cas = 'all')

    #- Misfit funtion and gradient
    Opti.MF = np.zeros(1, np.float64)
    Opti.gradMF = np.zeros(Opti.n, np.float64)


    # - BFGS parameters
    if Opti.method == 'bfgs':
        
        # save the user defined values
        if 'BFGS_user' in dir(Opti):
            BFGS_user = {}
            for key in Opti.BFGS_user:  BFGS_user[key] = Opti.BFGS[key]

        # defaut configuration
        Opti.BFGS = copy.deepcopy(Config.BFGS)

        # restore user defined values
        if 'BFGS_user' in dir(Opti):
            for key in Opti.BFGS_user: Opti.BFGS[key] = BFGS_user[key]
    
            
        bfgs(Opti)
        os.system('rm '+Opti.BFGS['input'])
        os.system('rm '+Opti.BFGS['output'])

    
#END reboot
# ==============================================================================



# ==============================================================================
# Provide informations before launching the assimilation
# ------------------------------------------------------------------------------
def info(Site, Paras, Data, Opti, logfile, ficinfo):

    
    # --- Variables 
    
    print
    print '-------------------------------------------------'
    print '-           Variable characteristics'
    print '-------------------------------------------------'

    logfile.write('\n-------------------------------------------------\n')
    logfile.write('-           Variable characteristics\n')
    logfile.write('-------------------------------------------------\n')
    
    keys = ['value','prior','sigma','min_opti','max_opti','eps','deriv']
    
    #for name in all_varname:
    #    if  Paras.vars[name]['opti'] == 'y':
    #        for key in keys:
    #            print ' + '+name+' ['+key+'] = ',Paras.vars[name][key]
    #            logfile.write(' + '+name+' ['+key+'] = ' + str(Paras.vars[name][key]) + '\n')
    #        print
    #        logfile.write('\n')
        
    # -- Specific output files to know parameters components
    f = open(ficinfo, 'w')
    
    f.write('\n \n Location of the sites depending on the map : \n')
    for imap in Site.real_maps:
        f.write('Map '+str(imap+1)+' : \n')
        for ireg in Site.map['occupied_regions'][imap]:
            f.write('       - Region '+str(ireg)+' : ')
            for isite in Site.site_ind[imap][ireg]:
                f.write(Site.name[isite])
                f.write('  ')
            f.write('\n')
        f.write('\n')
        

    buf = copy.deepcopy(Paras.vars)


    for name in Paras.vars['opti_varname']:

        for key in keys:
            if type(Paras.vars[name][key]) == type(np.zeros(1)):
                print ' + '+name+' ['+key+'] = ',Paras.vars[name][key].ravel()
                logfile.write(' + '+name+' ['+key+'] = ' + str(Paras.vars[name][key].ravel()) + '\n')
            else:
                print ' + '+name+' ['+key+'] = ',Paras.vars[name][key]
                logfile.write(' + '+name+' ['+key+'] = ' + str(Paras.vars[name][key]) + '\n')
        print
        logfile.write('\n')


        # Write some info
        f.write('************************************************ \n')
        
        f.write('\n'+ name+ '\n \n')
        
        total_comp = len(Opti.x[name].ravel())
        
        if len(buf[name]['dim_name']) == 1:
            f.write('Dependence : Time ('+buf[name]['dim_name'][0]+') \n')
            
        if len(buf[name]['dim_name']) == 2:

            
            if 'indice_pft' in buf[name]['dim_name']:
                f.write('Dependence : PFT, Time ('+buf[name]['dim_name'][1]+') \n')
                f.write('PFT : '+str(buf['PFT_global']['value'])+'\n')
                        
            if 'points_terre' in buf[name]['dim_name']:
                f.write('Dependence : Site, Time ('+buf[name]['dim_name'][1]+') \n')
                
            if 'indice_region' in buf[name]['dim_name']:
                f.write('Dependence : Region, Time ('+buf[name]['dim_name'][1]+') \n')
                map = buf[name]['map']
                regions = Site.map['occupied_regions'][map]
                f.write('Using map number : ' + str(map+1) + '\n')
                f.write('Index(es) of the occupied regions :'+str(regions)+'\n')
            
        if len(buf[name]['dim_name']) == 3:
            
            if 'indice_region' in buf[name]['dim_name']:
                f.write('Dependence : Region, PFT, Time ('+buf[name]['dim_name'][2]+') \n')
                map = buf[name]['map']
                regions = Site.map['occupied_regions'][map]
                f.write('Using map number : ' + str(map+1) + '\n')
                f.write('Index(es) of the occupied regions :'+str(regions)+'\n')
                f.write('PFT per region : \n')
                for ireg in Site.map['occupied_regions'][map]:
                    f.write('        - Region '+str(ireg)+' : '+str(buf['PFT']['value'][map][ireg])+'\n')

            if 'points_terre' in buf[name]['dim_name']:
                f.write('Dependence : Site, PFT, Time ('+buf[name]['dim_name'][2]+') \n')
                f.write('PFT per site : \n')
                for isite in range(Site.npts):
                    f.write('        - Site '+Site.name[isite]+' : '+str(Site.indice_pft[isite])+'\n')


        f.write('Total components : ' + str(total_comp) +'\n \n')

    f.close()
    
    # --- Data
    
    print
    print '----------------------------------------------------'
    print '-               Data characteristics'
    print '----------------------------------------------------'

    logfile.write('\n---------------------------------------------------- \n')
    logfile.write('-               Data characteristics \n')
    logfile.write('---------------------------------------------------- \n')

    for isite in range(Site.npts):

        print

        print '+++ Site #'+str(isite+1)+' : '+Site.name[isite]+' :'
        logfile.write('\n+++Site #'+str(isite+1)+' : '+Site.name[isite]+' : \n')
        
            
        for vname in Data.obsname_opti[isite]:

            print ' + '+vname+' : '
            logfile.write('\n\n  + '+vname+' : ')
        
            if 'daily' in Data.vars[isite][vname]['processing_sim']:
                print '   - Assimilation of DAILY data accounting for measurements between ',[Data.tdaily_d,Data.tdaily_f]
                logfile.write('\n  - Assimilation of DAILY data accounting for measurements between '+str([Data.tdaily_d,Data.tdaily_f])+'\n')
                
            elif 'diurnal' in Data.vars[isite][vname]['processing_sim']:
                print '   - Assimilation of DIURNAL data '
                logfile.write('\n\  - Assimilation of DIURNAL data')
                
                if Data.diurnal['month'] != None:
                    print '     + DIURNAL cycles are computed at months', Data.diurnal['month']
                    print '       for the following number of days ',Data.diurnal['length']
                    logfile.write('     + DIURNAL cycles are computed at months' + str(Data.diurnal['month']) + '\n')
                    logfile.write('       for the following number of days ' + str(Data.diurnal['length']) + '\n')
                else:
                    print '     + DIURNAL cycles are computed at days', Data.diurnal['start']
                    print '       for the following number of days ',Data.diurnal['length']
                    logfile.write('     + DIURNAL cycles are computed at days' + str(Data.diurnal['start']) + '\n')
                    logfile.write('       for the following number of days ' + str(Data.diurnal['length']) + '\n')
                
                
            elif 'normalize' in Data.vars[isite][vname]['processing_sim']:
                buf = Data.vars[isite][vname]['processing_sim'].split('_')
                ind = buf.index('normalize')
                min_pc = int(buf[ind+1])
                max_pc = int(buf[ind+2])
                print '    - np.rmalization of '+vname+ ' between '+str(min_pc)+ '% and '+str(max_pc)+ '% of its range of variation'
                logfile.write('    - np.rmalization of '+vname+ ' between '+str(min_pc)+ '% and '+str(max_pc)+ '% of its range of variation\n')


            elif Data.vars[isite][vname]['processing_sim'] == '':           
                print '    - Assimilation of '+ vname+' at the temporal resolution of the measurements '
                logfile.write('    - Assimilation of '+ vname +' at the temporal resolution of the measurements  \n')
                
            else:
                tempo_res =  (Data.sim[isite]['fic'][0]['time_step'])
                print '   - Assimilation of data sampled every '+str(tempo_res)+' seconds +++'
                logfile.write('   - Assimilation of data sampled every '+str(tempo_res)+' seconds +++\n')
                              
                
            if 'smooth' in Data.vars[isite][vname]['processing_sim']:
                print '   - Smoothing of simulated '+vname+' using ',
                logfile.write('\n  - Smoothing of simulated '+vname+' using ')
                if 'gauss' in Data.vars[isite][vname]['processing_sim']:
                    print ' a Gaussian filter'
                    logfile.write('a Gaussian filter')
                else:
                    print ' a Moving Average Window of '+str(Config.smooth_len_square_filter)+ ' days'
                    logfile.write('a Moving Average Window of '+str(Config.smooth_len_square_filter)+ ' days')

   
            # - errors
            print
            logfile.write('\n')

        
###        for name in Data.obsname_opti[isite]:
            keys = ['sigma_user','sigma']

            if Data.adjust_contrib_MF_obs == True:
                keys.append('contrib_MF_obs')
           
            for ekey in keys:
                print '  - error['+str(isite)+']['+vname+']['+ekey+'] = ',Data.vars[isite][vname][ekey]
                logfile.write('  - error['+str(isite)+']['+vname+']['+ekey+'] = ' + str(Data.vars[isite][vname][ekey]) + '\n')
            print

    ###ERRORS
    # --- Optimization
    
    print
    print '----------------------------------------------------'
    print '-         Optimization characteristics'
    print '----------------------------------------------------'
    print ' + Opti.method : ', Opti.method
    print ' + Opti.method_gradJ_fd : ', Opti.method_gradJ_fd
    print ' + Optimization in the space of : ', Opti.Fmisfit_space
    print ' + Opti.nloop_max : ', Opti.nloop_max
    print

    logfile.write('\n ----------------------------------------------------'+'\n')
    logfile.write('-          Optimization characteristics'+'\n')
    logfile.write('----------------------------------------------------'+'\n')
    logfile.write(' + Opti.method : ' +Opti.method +'\n')
    logfile.write(' + Opti.method_gradJ_fd : ' +str(Opti.method_gradJ_fd) +'\n')
    logfile.write(' + Optimization in the space of : ' + str(Opti.Fmisfit_space) +'\n')
    logfile.write(' + Opti.nloop_max : ' +str(Opti.nloop_max) +'\n')

    print '----------------------------------------------------'
    logfile.write('----------------------------------------------------'+'\n')
    
# ==============================================================================

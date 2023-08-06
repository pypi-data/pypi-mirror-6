#*******************************************************************************
# MODULE	: ORCHIDEE
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 08/2007
# LAST MODIF    : 07/2012
# COMPILER	: PYTHON
#
"""
ORCHIDEE-related functions
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import os,glob,sys,copy
import ConfigParser
from orchis_config import Config

#from TOOLS import funcio
import funcio, funcio_site

# =================================================================================
# Remplace les valeurs du dictionnaire de configuration par defaut par les
# nouvelles options du fichier de configuration
#
# Inputs  : - fichier contenant la configuration
#           - dictionnaire de configuration par defaut
#
# Outputs : - dictionnaire de configuration modifie
# ---------------------------------------------------------------------------------
def get_config(fileConfig,config_defaut):
    
    
    # -- Chargement de la nouvelle configuration
    if len(glob.glob(fileConfig)) == 0:
        sys.exit('STOP : the configuration file (.cfg) was not found:'+fileConfig)
    cf = ConfigParser.ConfigParser()
    cf.read(fileConfig)  

    
    # -- Definition du nouveau dictionnaire de configuration
    conf_new = {}
    
    # -- Lecture des sections et des options
    
    # -- Path des sorties et des fichiers start
    PATH_OUT = cf.get('path', 'PATH_OUT')
    PATH_START = cf.get('path', 'PATH_START')
    sections = cf.sections()
    sections.remove('path')
    
    for section in sections:  # lecture des sections sauf path
        
        for option in cf.options(section):

            val_option = cf.get(section, option)
            # on elimine les commentaires commencant par # ou ;
            val_option = val_option.split('#')[0].split(';')[0] 

            # Ajout du nom du chemin d'ecriture pour les fichiers outputs
            if section == 'outputs':
                [f_rep,f_fic] = os.path.split(val_option)
                if f_rep == '':
                    val_option = os.path.join(PATH_OUT, f_fic)

            # Ajout du nom du chemin d'acces pour les fichiers start-in
            if section == 'start':
                [f_rep,f_fic] = os.path.split(val_option)
                if f_rep == '':
                    val_option = os.path.join(PATH_START, f_fic)


            conf_new[option.upper()] = val_option
            #print ' + '+option.upper()+':'+val_option


    # --  Modifie la configuration par defaut
    conf_out = config_defaut.copy()   # Utiliser une copie evite que le dictionnaire
                                      # d'origine ne soit modifie

                                      
    # Comme ConfigParser recupere les options en majuscule, on passe
    # les champs du dictionnaire DEFAUT en minuscule   
    for key in conf_out.keys():
        if key.upper() != key:
            conf_out[key.upper()] = conf_out[key]
            del conf_out[key]
            
    keys = conf_new.keys()
    values = conf_new.values()
    for ikeys in range(len(keys)):
        conf_out[keys[ikeys]] = values[ikeys]  
        # fin boucle keys   

    # -- Retourne la configuration modifiee
    return conf_out
# ------------------------------------------------------------------------------


# ==============================================================================
# Genere l'ecriture du fichier run.def
# Lance l'execution d'ORCHIDEE
# Gere l'archivage des sorties du modele
# ==============================================================================
def text_write(string, fileout_name):
    fout = open(fileout_name, 'w')
    fout.write(string)
    fout.close()
# fin text_write
# ------------------------------------------------------------------------------



# ==============================================================================
# Generate run.def files for ORCHIDEE
# ------------------------------------------------------------------------------
def gen_rundef(ficConfig = None, 
               pathout = None, 
               for_clim = None,
               site = None, 
               time_skip = None,
               time_length = None,
               write_step = None,
               stomate_hist_dt = None,
               split_dt = None, 
               optim = None,      
               optim_para_in = None,
               optim_para_out = None,
               optim_flux_out = None,
               sech_start = None,  sech_restart = None,
               stom_start = None, stom_restart = None ,
               driv_start = None, driv_restart = None,
               sech_out = None, sech_out2 = None, stom_out = None):
    
    # Generateur de fichier run.def pour ORCHIDEE
    
    # def gen_rundef(
    #    ficConfig = ficConfig         : nom du fichier de configuration
    #    pathout=pathout               : nom du repertoire ou est genere le run.def (rep. courant par defaut)
    #    site=XX,                      : nom du site
    #    for_clim=for_clim             : path+nom du fichier de forcage meteorologique
    #    time_skip=time_skip           : nombre d'annees a sauter dans le fichier de forcage meteo
    #    time_length=time_length       : nombre total d'annees de forcage meteo
    #    split_dt=split_dt             : division du pas de temps de forcage
    #    write_step = write_step       : pas de temps d'ecriture pour sechiba
    #    stomate_hist_dt = stomate_hist_dt : pas de temps d'ecriture pour stomate
    #    optim=optim                   : (y/n) active ou nom le module d'optimisation
    #    optim_para_in=optim_para_in   : path+nom du fichier d'entree de valeur des parametres 'optimisables'
    #    optim_para_out=optim_para_out : path+nom du fichier de sortie de valeur des parametres 'optimisables'
    #    optim_flux_out=optim_flux_out : path+nom du fichier de valeur des flux assimiles
    #    sech_start=sech_start         : path+nom du fichier de condition initiales pour SECHIBA
    #    sech_restart=sech_restart     : path+nom du fichier restart pour SECHIBA
    #    stom_start=stom_start         : path+nom du fichier de condition initiales pour STOMATE
    #    stom_restart=stom_restart     : path+nom du fichier restart pour STOMATE
    #    driv_start=driv_start         : path+nom du fichier start pour le DRIVER
    #    driv_restart=driv_restart     : path+nom du fichier restart pour le DRIVER
    #    sech_out=sech_out             : path+nom du fichier history pour SECHIBA
    #    sech_out2=sech_out2           : path+nom du 2e fichier history pour SECHIBA
    #    stom_out=stom_out             : path+nom du fichier history pour STOMATE
    #    )
    # 
    #
    # Remarques :
    #    - La configuration par defaut du modele ORCHIDEE est parametree dans le
    #    fichier : 'ORCHIDEE_CFG.py'
    #    
    #    - La parametrisation specifique de la simulation a effectuer est indiquee
    #    dans le fichier : 'XX.cfg'
    #    
    


    # -----------------------------------------------------
    # --- Chemin et fichier de configuration par defaut ---
    # -----------------------------------------------------
    # Chemin d'acces de configuration
    #pathCONFIG = '/home/data02/cbacour/ORCHIDEE/config/'
    sys.path.append(Config.pathCONFIG)                             
    
    # Chargement de la configuration modele 
    if Config.orch_version == 'AR5':
        import ORCHIDEE_AR5_CFG as DEFAULT
    elif Config.orch_version == 'CAMELIA':
        import ORCHIDEE_CAMELIA_CFG as DEFAULT
    #print "PATH CONFIG = ",Config.pathCONFIG
    config_defaut = DEFAULT.config_defaut.copy()
    modele_rundef = copy.copy(DEFAULT.modele_rundef)

    # -------------------------
    # -- Gestion des options --
    # -------------------------

    # site
    if site == None and ficConfig == None:
        sys.exit('# STOP. TOOLS gen_rundef : You must provide one site name OR an input configuration file')
        
    # fic
    if ficConfig == None:
        ficConfig = os.path.join(Config.pathCONFIG,site+'.cfg')
        if len(glob.glob(ficConfig)) != 1:
            sys.exit('# STOP. TOOLS gen_rundef : No configuration file found : '+ficConfig)
        #else:
            #print
            #print '  + The default configuration file for '+site+' is used : ' + ficConfig

    #print '  + The following configuration file for '+site+' is used: ' + ficConfig
 

        
    # -----------------------------------
    # --- Creation du fichier run.def ---
    # -----------------------------------
    
    #-- Remplacement des parametrisations par defaut par les parametres specifiques de la simulation
    new_config = get_config(ficConfig, config_defaut)
    
    # annees de simulation
    if time_length != None : new_config['TIME_LENGTH'] = str(time_length) + 'Y'
    if time_skip !=None : new_config['TIME_SKIP'] = str(time_skip) + 'Y'
        
    # division du pas de temps de forcage
    if split_dt !=None : new_config['SPLIT_DT'] = str(split_dt)

    # pas de temps d'ecriture
    if write_step != None : new_config['WRITE_STEP'] = str(write_step)
    if stomate_hist_dt != None : new_config['STOMATE_HIST_DT'] = str(stomate_hist_dt)
    
    
    # fichier de forcage
    if for_clim != None : new_config['FORCING_FILE'] = for_clim

    # fichiers d'optimisation
    if optim != None          : new_config['OPTIMIZATION_ORCHIDEE'] = optim
    if optim_para_in != None  : new_config['OPTIMIZATION_FILEIN_PARAS'] = optim_para_in
    if optim_para_out != None : new_config['OPTIMIZATION_FILEOUT_PARAS'] = optim_para_out
    if optim_flux_out != None : new_config['OPTIMIZATION_FILEOUT_FLUXES'] = optim_flux_out
    
    # fichiers start-restart
    if driv_start != None : new_config['RESTART_FILEIN'] = driv_start
    #if sech_start != None : new_config['SECHIBA_restart_in'] = sech_start
    if sech_start != None : new_config['SECHIBA_RESTART_IN'] = sech_start
    if stom_start != None : new_config['STOMATE_RESTART_FILEIN'] = stom_start
    
    if driv_restart != None : new_config['RESTART_FILEOUT'] = driv_restart
    #if sech_restart != None : new_config['SECHIBA_rest_out'] = sech_restart
    if sech_restart != None : new_config['SECHIBA_REST_OUT'] = sech_restart 
    if stom_restart != None : new_config['STOMATE_RESTART_FILEOUT'] =  stom_restart
    

    # fichiers history
    if sech_out != None  : new_config['OUTPUT_FILE'] = sech_out
    if sech_out2 != None : new_config['SECHIBA_OUTPUT_FILE2'] = sech_out2
    if stom_out != None  : new_config['STOMATE_OUTPUT_FILE'] = stom_out
    
    
    #-- Ecriture du fichier run.def
    fic_rundef = 'run.def'
    if pathout !=None : fic_rundef = os.path.join(pathout,'run.def')
    text_write(modele_rundef % new_config, fic_rundef)  
    
# FIN gen_rundef
# ==============================================================================
    



# ==============================================================================
# Determine ORCHIDEE simulated fluxes from the prior parameter values
#
#
# ------------------------------------------------------------------------------
def launch(isite,
           Vars,
           Site,
           Data,
           logfile,
           check         = None,
           file_flux_out = None,
           just_getdata  = None,
           varname_tl    = None,
           value_tl      = None):
    

    
    # Read the TL variables?
    # ----------------------
    read_tl = None
#    if varname_tl != None:
    if value_tl != None:
        read_tl = True

        # --- Arrange value_tl to one site
        #tmp = MA.masked_where(not in Site.indice_pft[isite], value_tl)
        #for i in range(len(value_tl)):
        #    if value_tl[i] in Site.indice_pft[isite]:tmp.append(value_tl[i])
        #value_tl = copy.copy(tmp)
        #print value_tl
            
    # Niveau d'ecriture
    # -----------------
    # 2 et > 4 dans ce module 
    if check == None: check = 5 #DEBUG 0

    # --- Input
    file_para_in = os.path.join(Config.PATH_EXEC_SITE[isite] , 'para_in.nc')
        
    # --- If has to perform simulation

    if just_getdata == None:
        
        # --- Create the NetCDF input parameter file with the current parameter values
        funcio_site.write_paras(file_para_in, Vars, varname_tl = varname_tl , value_tl = value_tl)
        
        ###if check >=4: print '    + ORCHIDEE.LAUNCH : writting of the input parameter NetCDF file : OK'
    
        # --- Create a run.def file
    
        driv_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'driv_restart.nc')
        sech_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'sech_restart.nc')
        stom_restart = os.path.join(Config.PATH_EXEC_SITE[isite] , 'stom_restart.nc')

        flux_out = os.path.join(Config.PATH_EXEC_SITE[isite] , Config.orch_flux_out)
        sech_out = os.path.join(Config.PATH_EXEC_SITE[isite] , Config.orch_sech_out)
        if Config.orch_sech_out2 != None:  
            sech_out2 = os.path.join(Config.PATH_EXEC_SITE[isite] , Config.orch_sech_out2)
        else:
            sech_out2 = None
        stom_out = os.path.join(Config.PATH_EXEC_SITE[isite] , Config.orch_stom_out)
        
        gen_rundef(ficConfig = Site.fic_cfg[isite], 
                   pathout = Config.PATH_EXEC_SITE[isite],   
                   for_clim = Site.fic_forc[isite],
                   site = Site.name[isite],             
                   time_length = Site.time[isite]['nannees'],
                   optim = 'y',
                   optim_para_in  = file_para_in,  
                   optim_flux_out = flux_out, 
                   
                   driv_restart = driv_restart,
                   sech_restart = sech_restart,
                   stom_restart = stom_restart,
                   
                   sech_out = sech_out,
                   sech_out2 = sech_out2,
                   stom_out = stom_out,
                   )
        
        
        ###if check >=4: print'    + ORCHIDEE.LAUNCH : writting of the run.def file : OK'
    
        # --- Execute ORCHIDEE
        if check >=2:
#            if varname_tl == None:
            if value_tl == None:
                print '    + ORCHIDEE.LAUNCH : '+Config.exe_orchidee+' simulation ORCHIDEE in process ......'
            else:
                print '    + ORCHIDEE.LAUNCH : '+Config.exe_orchidee_tl+' simulation ORCHIDEE_TL in process ......'
    
        os.system('rm -f ' + driv_restart +' '+ sech_restart +' '+stom_restart)
        # - ORCHIDEE classique
        os.system('pwd')
#        if varname_tl == None:
        if value_tl == None:
            os.system(Config.cmde_orchidee + ' > orchidee.log')
        # - ORCHIDEE TL
        else:
            os.system(Config.cmde_orchidee_tl + ' > orchidee.log')
            
        os.system('rm -f ' + driv_restart)


    # --- Output files / Save prior AND posterior files
    if file_flux_out != None:

        buf = os.path.split(file_flux_out)
        
        file_sech_out = os.path.join(buf[0],buf[1].replace('flux','sech'))
        file_stom_out = os.path.join(buf[0],buf[1].replace('flux','stom'))
                                    
        os.system('cp -pR '+ flux_out +' '+file_flux_out)
        os.system('cp -pR '+ sech_out +' '+file_sech_out)
        os.system('cp -pR '+ stom_out +' '+file_stom_out)

    # --- Get the fluxes

    Data.sim[isite] = funcio.get_data(Data.fic[isite]['sim'],
                                      isite,
                                      logfile,
                                      read_tl = read_tl,
                                      tdaily = [Data.tdaily_d, Data.tdaily_f],
                                      ndays = Site.time[isite]['njours'],
                                      nyears = Site.time[isite]['nannees'], 
                                      diurnal_length = Data.diurnal[isite]['length'] ,
                                      diurnal_start = Data.diurnal[isite]['start'], 
                                      vars_info = Data.vars[isite],
                                      case = 'sim')
    
    if check >=4: print '    + ORCHIDEE.LAUNCH : reading of the simulated fluxes : OK'



# END detprior_model
# ==============================================================================

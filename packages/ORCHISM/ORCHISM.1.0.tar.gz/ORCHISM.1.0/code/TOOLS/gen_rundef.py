#*******************************************************************************
# MODULE	: GEN_RUNDEF
# AUTHOR	: C. BACOUR
# CREATION	: 08/2007
# LAST MODIF    : 05/2012
# COMPILER	: PYTHON
#
"""
Generates the run.def configuration file used for ORCHIDEE runs
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import os
import sys
import glob
import copy
import ConfigParser

#from TOOLS import *

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
# ---------------------------------------------------------------


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



# ==============================================================================
# Generate run.def files for ORCHIDEE
# ------------------------------------------------------------------------------
""" Generateur de fichier run.def pour ORCHIDEE

def gen_rundef(    
                   pathout=pathout               : nom du repertoire ou est genere le run.def (rep. courant par defaut)
                   site=XX,                      : nom du site
                   for_clim=for_clim             : path+nom du fichier de forcage meteorologique
                   time_skip                     : nombre d'annees a sauter dans le fichier de forcage meteo
                   time_length                   : nombre total d'annees de forcage meteo
                   optim=optim                   : (y/n) active ou nom le module d'optimisation
                   optim_para_in=optim_para_in   : path+nom du fichier d'entree de valeur des parametres 'optimisables'
                   optim_para_out=optim_para_out : path+nom du fichier de sortie de valeur des parametres 'optimisables'
                   optim_flux_out=optim_flux_out : path+nom du fichier de valeur des flux assimiles
                   sech_start=sech_start         : path+nom du fichier de condition initiales pour SECHIBA
                   sech_restart=sech_restart     : path+nom du fichier restart pour SECHIBA
                   stom_start=stom_start         : path+nom du fichier de condition initiales pour STOMATE
                   stom_restart=stom_restart     : path+nom du fichier restart pour STOMATE
                   driv_start=driv_start         : path+nom du fichier start pour le DRIVER
                   driv_restart=driv_restart     : path+nom du fichier restart pour le DRIVER
                   sech_out=sech_out             : path+nom du fichier history pour SECHIBA
                   stom_out=stom_out             : path+nom du fichier history pour STOMATE
                   )
                      
                      
Remarques :
 - La configuration par defaut du modele ORCHIDEE est parametree dans le
 fichier : 'orchidee_config_defaut.py'

 - La parametrisation specifique de la simulation a effectuer est indiquee
 dans le fichier : 'XXX_config.py'

     
"""
def gen_rundef(\
         ficConfig = None,\
         pathout = None, \
         for_clim = None,\
         site = None, \
         time_skip = None, time_length = None, \
         optim = None, optim_para_in = None, optim_para_out = None, optim_flux_out = None,\
         sech_start = None,  sech_restart = None,\
         stom_start = None, stom_restart = None ,\
         driv_start = None, driv_restart = None,\
         sech_out = None, stom_out = None):
    
    
    # -----------------------------------------------------
    # --- Chemin et fichier de configuration par defaut ---
    # -----------------------------------------------------
    # Chemin d'acces de configuration
    pathCONFIG = '/home/data02/cbacour/ORCHIDEE/config/'
    sys.path.append(pathCONFIG)                             
    
    # Chargement de la configuration modele 
    import ORCHIDEE_CFG as DEFAULT
    config_defaut = DEFAULT.config_defaut.copy()
    modele_rundef = copy.copy(DEFAULT.modele_rundef)
    
        
    # -------------------------
    # -- Gestion des options --
    # -------------------------

    # site
    if site == None and ficConfig == None:
        sys.exit('# STOP. TOOLS gen_rundef : You must provide one site name OR an input configuraiton file')
        
    # fic
    if ficConfig == None:
        ficConfig = os.path.join(pathCONFIG,site,'.cfg')
        if len(glob.glob(fic)) != 1:
            sys.exit('# STOP. TOOLS gen_rundef : No configuration file found')
        else:
            print '# The default configuration file for '+site+' is used'
    
 
    
    # -----------------------------------
    # --- Creation du fichier run.def ---
    # -----------------------------------

    #-- Remplacement des parametrisations par defaut par les parametres specifiques de la simulation
    new_config = get_config(ficConfig, config_defaut)
    
    # annees de simulation
    if time_length != None : new_config['TIME_LENGTH'] = str(time_length) + 'Y'
    if time_skip !=None : new_config['TIME_SKIP'] = str(time_skip) + 'Y'
        

    # fichier de forcage
    if for_clim != None : new_config['FORCING_FILE'] = for_clim

    # fichiers d'optimisation
    if optim != None          : new_config['OPTIMIZATION_ORCHIDEE'] = optim
    if optim_para_in != None  : new_config['OPTIMIZATION_FILEIN_PARAS'] = optim_para_in
    if optim_para_out != None : new_config['OPTIMIZATION_FILEOUT_PARAS'] = optim_para_out
    if optim_flux_out != None : new_config['OPTIMIZATION_FILEOUT_FLUXES'] = optim_flux_out
    
    
    # fichiers start-restart
    if driv_start != None : new_config['RESTART_FILEIN'] = driv_start
    if sech_start != None : new_config['SECHIBA_restart_in'] = sech_start
    if stom_start != None : new_config['STOMATE_RESTART_FILEIN'] = stom_start
    
    if driv_restart != None : new_config['RESTART_FILEOUT'] = driv_restart
    if sech_restart != None : new_config['SECHIBA_rest_out'] = sech_restart 
    if stom_restart != None : new_config['STOMATE_RESTART_FILEOUT'] =  stom_restart
    

    # fichiers history
    if sech_out != None : new_config['OUTPUT_FILE'] = sech_out
    if stom_out != None : new_config['STOMATE_OUTPUT_FILE'] = stom_out
    
    
    #-- Ecriture du fichier run.def
    fic_rundef = 'run.def'
    if pathout !=None : fic_rundef = os.path.join(pathout,'run.def')
    text_write((modele_rundef % new_config,fic_rundef)
    


    
# FIN gen_rundef
# ==============================================================================

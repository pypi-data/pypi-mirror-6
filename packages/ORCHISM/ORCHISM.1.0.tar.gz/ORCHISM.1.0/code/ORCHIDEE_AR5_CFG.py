#!/usr/bin/env python
#*******************************************************************************
# MODULE	: ORCHIDEE_AR5_CFG
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 06/2010
# LAST MODIF    : 02/2012
# COMPILER	: PYTHON
#
"""
Initialization and creation of the database for the default configuration of 
ORCHIDEE's parameters, so as to generate the run.def files
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

# --- Initialisation du dictionnaire ---
# --------------------------------------
config_defaut = {}


# --- Initialisation de PATH par defaut ---
# -----------------------------------------
# Remarque : ces parametres ne seront pas ecrits dans le run.def mais servent
# ou script qui lance les simulations pour definir les fichiers d'entree/sortie
config_defaut['pathFORCAGE'] = '/home/satellites7/cbacour/ORCHIDEE/forcage/'
config_defaut['pathRESTART'] = '/home/satellites7/cbacour/ORCHIDEE/startfiles/'
config_defaut['pathOUT']     = '/home/satellites7/cbacour/ORCHIDEE/outputs/'



# --- Affectation des valeurs par defaut ---
# ------------------------------------------

# -- Affichage --
config_defaut['BAVARD'] = '1'
config_defaut['DEBUG_INFO'] = 'n'
config_defaut['LONGPRINT'] = 'n'

config_defaut['ALMA_OUTPUT'] = 'y'
config_defaut['SECHIBA_reset_time'] = 'n'

# -- Fichiers d'entree/sortie --
config_defaut['VEGETATION_FILE'] = config_defaut['pathFORCAGE']+'carteveg5km.nc'
config_defaut['SLOWPROC_VEGET_OLD_INTERPOL'] = 'n'
config_defaut['SOILALB_FILE'] = config_defaut['pathFORCAGE']+'soils_param.nc'
config_defaut['SOILTYPE_FILE'] = config_defaut['pathFORCAGE']+'soils_param.nc'
config_defaut['REFTEMP_FILE'] = config_defaut['pathFORCAGE']+'reftemp.nc'
config_defaut['FORCING_FILE'] = config_defaut['pathFORCAGE']+'WG_cru.nc'

config_defaut['RESTART_FILEIN'] = 'NONE'
config_defaut['RESTART_FILEOUT'] = 'driver_rest_out.nc'
config_defaut['SECHIBA_RESTART_IN'] = 'NONE'
config_defaut['SECHIBA_REST_OUT'] = config_defaut['pathRESTART']+'sechiba_rest_out.nc'

config_defaut['STOMATE_RESTART_FILEIN'] = 'NONE'
config_defaut['STOMATE_RESTART_FILEOUT'] = config_defaut['pathRESTART']+'stomate_rest_out.nc'

config_defaut['STOMATE_FORCING_NAME'] = 'NONE'  
#stomate_forcing.nc#
config_defaut['STOMATE_FORCING_MEMSIZE'] = '50'
config_defaut['STOMATE_CFORCING_NAME'] = 'NONE' 
#stomate_Cforcing.nc#

config_defaut['ORCHIDEE_WATCHOUT'] = 'n'
config_defaut['WATCHOUT_FILE'] = 'NONE' 
#config_defaut['pathOUT']+'orchidee_watchout.nc'
config_defaut['DT_WATCHOUT'] = '1800'
config_defaut['STOMATE_WATCHOUT'] = 'n'

config_defaut['OUTPUT_FILE'] = config_defaut['pathOUT']+'sechiba_hist_out.nc'
config_defaut['SECHIBA_HISTFILE2'] = 'FALSE'
config_defaut['SECHIBA_OUTPUT_FILE2'] = 'NONE'
#config_defaut['pathOUT']+'sechiba_hist2_out.nc'
config_defaut['STOMATE_OUTPUT_FILE'] = config_defaut['pathOUT']+'stomate_hist_out.nc'

config_defaut['SECHIBA_HISTLEVEL'] = '5'
config_defaut['SECHIBA_HISTLEVEL2'] = '1'
config_defaut['STOMATE_HISTLEVEL'] = '4'

config_defaut['WRITE_STEP'] = '86400.0'
config_defaut['WRITE_STEP2'] = '1800.0'
config_defaut['STOMATE_HIST_DT'] = '1.'

# -- Optimisation de certains parametres d'ORCHIDEE --
config_defaut['NLITT'] ='2'
config_defaut['IS_PHENO_CONTI'] ='y'
config_defaut['IS_FAPAR_TRICK_TBS_C3G'] ='FALSE'
config_defaut['FAPAR_COMPUTATION'] = 'black_sky_daily'

config_defaut['IS_EXT_COEFF_CONSTANT'] ='TRUE'
config_defaut['OPTIMIZATION_ORCHIDEE'] ='n'
config_defaut['OPTIMIZATION_FILEIN_PARAS'] = 'NONE'
config_defaut['OPTIMIZATION_FILEOUT_PARAS'] = 'NONE'
config_defaut['OPTIMIZATION_FILEOUT_FLUXES'] = 'NONE'
config_defaut['OPTIMIZATION_FILEOUT_EXTCOEFF'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_NEE'] = 'n'
config_defaut['OPTIMIZATION_FILEOUT_NEET'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_QH'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_QLE'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_RN'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_FAPAR'] = 'n'
config_defaut['OPTIMIZATION_FILEOUT_FAPART'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_ABOBMT'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_WOODBMT'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_GPPT'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_RESP_HT'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_RESP_GT'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_RESP_MT'] = 'y'
config_defaut['OPTIMIZATION_FILEOUT_RESP_H'] = 'n'
config_defaut['OPTIMIZATION_FILEOUT_RESP_TER'] = 'n'
config_defaut['OPTIMIZATION_FILEOUT_RESP_TERT'] = 'y'


# -- Coordonnees du site --
config_defaut['LIMIT_WEST'] = '-180.'
config_defaut['LIMIT_EAST'] = '180.'
config_defaut['LIMIT_NORTH'] = '90.'
config_defaut['LIMIT_SOUTH'] = '-90.'

# -- Caracteristiques de la simulation --
config_defaut['RELAXATION'] = 'n'
config_defaut['RELAX_A'] = '1000.0'
config_defaut['HEIGHT_LEV1'] = '2.0'
config_defaut['HEIGHT_LEVW'] = '10.0'

# -- Generateur d'intemperies --
config_defaut['ALLOW_WEATHERGEN'] = 'n'
config_defaut['MERID_RES'] = '2.'
config_defaut['ZONAL_RES'] = '2.'
config_defaut['IPPREC'] = '0'
config_defaut['NO_INTER'] = 'y'
config_defaut['INTER_LIN'] = 'n'
config_defaut['WEATHGEN_PRECIP_EXACT'] = 'n'
config_defaut['DT_WEATHGEN'] = '1800.'
config_defaut['NETRAD_CONS'] = 'y'
config_defaut['DUMP_WEATHER'] = 'n'
config_defaut['DUMP_WEATHER_FILE'] = 'weather_dump.nc'
config_defaut['DUMP_WEATHER_GATHERED'] = 'y'

config_defaut['ECCENTRICITY'] = '0.016724'
config_defaut['PERIHELIE'] = '102.04'
config_defaut['OBLIQUITY'] = ' 23.446'

# -- Duree de la simulation --
config_defaut['TIME_LENGTH'] = 'default'
config_defaut['SPLIT_DT'] = '1'
config_defaut['FORCING_RAD_CENTER'] = 'n'
config_defaut['TIME_SKIP'] = 'default'
config_defaut['FORCESOIL_STEP_PER_YEAR'] = '12'
config_defaut['FORCESOIL_NB_YEAR'] = '1'
config_defaut['SPRED_PREC'] = '1'


## # -- Differents flags a activer/desactiver --
config_defaut['STOMATE_OK_STOMATE'] = 'y'
config_defaut['STOMATE_OK_DGVM'] = 'n'
config_defaut['STOMATE_OK_CO2'] = 'y'
config_defaut['FORCE_CO2_VEG'] = 'TRUE'

# -- CO2 atmospherique --

config_defaut['ATM_CO2'] = '350.'
config_defaut['ATM_CO2_FILE'] = '/home/satellites7/cbacour/ORCHIDEE/forcage/atm_co2_1200_2006.nc'
config_defaut['YEAR_ATMCO2_START'] = '-1'

config_defaut['STOMATE_DIAGPT'] = '1'
config_defaut['LPJ_GAP_CONST_MORT'] = 'y'
config_defaut['FIRE_DISABLE'] = 'y'

#-- nouvelles options de restart depuis version 1.9.3
config_defaut['SOILCAP'] = 'n'
config_defaut['SOILFLX'] = 'n'
config_defaut['SHUMDIAG'] = 'n'
config_defaut['RUNOFF'] = 'n'
config_defaut['DRAINAGE'] = 'n'
config_defaut['RAERO'] = 'n'
config_defaut['QSATT'] = 'n'
config_defaut['CDRAG'] = 'n'
config_defaut['EVAPOT_CORR'] = 'n'
config_defaut['TEMP_SOL_NEW'] = 'n'
config_defaut['DSS'] = 'n'
config_defaut['HDRY'] = 'n'
config_defaut['CGRND'] = 'n'
config_defaut['DGRND'] = 'n'
config_defaut['Z1'] = 'n'
config_defaut['PCAPA'] = 'n'
config_defaut['PCAPA_EN'] = 'n'
config_defaut['PKAPPA'] = 'n'
config_defaut['ZDZ1'] = 'n'
config_defaut['ZDZ2'] = 'n'
config_defaut['TEMP_SOL_BEG'] = 'n'

# -- Parametres de la surface (vegetation+sol) --
config_defaut['IMPOSE_VEG'] = 'n'

config_defaut['SECHIBA_VEG__01'] = '0.2'
config_defaut['SECHIBA_VEG__02'] = '0.0'
config_defaut['SECHIBA_VEG__03'] = '0.0'
config_defaut['SECHIBA_VEG__04'] = '0.0'
config_defaut['SECHIBA_VEG__05'] = '0.0'
config_defaut['SECHIBA_VEG__06'] = '0.0'
config_defaut['SECHIBA_VEG__07'] = '0.0'
config_defaut['SECHIBA_VEG__08'] = '0.0'
config_defaut['SECHIBA_VEG__09'] = '0.0'
config_defaut['SECHIBA_VEG__10'] = '0.8'
config_defaut['SECHIBA_VEG__11'] = '0.0'
config_defaut['SECHIBA_VEG__12'] = '0.0'
config_defaut['SECHIBA_VEG__13'] = '0.0'

config_defaut['SECHIBA_VEGMAX__01'] = '0.2'
config_defaut['SECHIBA_VEGMAX__02'] = '0.0'
config_defaut['SECHIBA_VEGMAX__03'] = '0.0'
config_defaut['SECHIBA_VEGMAX__04'] = '0.0'
config_defaut['SECHIBA_VEGMAX__05'] = '0.0'
config_defaut['SECHIBA_VEGMAX__06'] = '0.0'
config_defaut['SECHIBA_VEGMAX__07'] = '0.0'
config_defaut['SECHIBA_VEGMAX__08'] = '0.0'
config_defaut['SECHIBA_VEGMAX__09'] = '0.0'
config_defaut['SECHIBA_VEGMAX__10'] = '0.8'
config_defaut['SECHIBA_VEGMAX__11'] = '0.0'
config_defaut['SECHIBA_VEGMAX__12'] = '0.0'
config_defaut['SECHIBA_VEGMAX__13'] = '0.0'

config_defaut['SECHIBA_LAI__01'] = '0'
config_defaut['SECHIBA_LAI__02'] = '8'
config_defaut['SECHIBA_LAI__03'] = '8'
config_defaut['SECHIBA_LAI__04'] = '4'
config_defaut['SECHIBA_LAI__05'] = '4.5'
config_defaut['SECHIBA_LAI__06'] = '4.5'
config_defaut['SECHIBA_LAI__07'] = '4'
config_defaut['SECHIBA_LAI__08'] = '4.5'
config_defaut['SECHIBA_LAI__09'] = '4'
config_defaut['SECHIBA_LAI__10'] = '2'
config_defaut['SECHIBA_LAI__11'] = '2'
config_defaut['SECHIBA_LAI__12'] = '2'
config_defaut['SECHIBA_LAI__13'] = '2'

config_defaut['SLOWPROC_HEIGHT__01'] = '0.'
config_defaut['SLOWPROC_HEIGHT__02'] = '50.'
config_defaut['SLOWPROC_HEIGHT__03'] = '50.'
config_defaut['SLOWPROC_HEIGHT__04'] = '30.'
config_defaut['SLOWPROC_HEIGHT__05'] = '30.'
config_defaut['SLOWPROC_HEIGHT__06'] = '30.'
config_defaut['SLOWPROC_HEIGHT__07'] = '20.'
config_defaut['SLOWPROC_HEIGHT__08'] = '20.'
config_defaut['SLOWPROC_HEIGHT__09'] = '20.'
config_defaut['SLOWPROC_HEIGHT__10'] = '.2'
config_defaut['SLOWPROC_HEIGHT__11'] = '.2'
config_defaut['SLOWPROC_HEIGHT__12'] = '.4'
config_defaut['SLOWPROC_HEIGHT__13'] = '.4'

config_defaut['SOIL_FRACTIONS__01'] = '0.28'
config_defaut['SOIL_FRACTIONS__02'] = '0.52'
config_defaut['SOIL_FRACTIONS__03'] = '0.20'

config_defaut['SLOWPROC_LAI_TEMPDIAG'] = '280.'
config_defaut['SECHIBA_ZCANOP'] = '0.5'
config_defaut['SECHIBA_FRAC_NOBIO'] = '0.0'
config_defaut['CLAY_FRACTION'] = '0.2'
config_defaut['IMPOSE_AZE'] = 'n'
config_defaut['CONDVEG_EMIS'] = '1.0'
config_defaut['CONDVEG_ALBVIS'] = '0.25'
config_defaut['CONDVEG_ALBNIR'] = '0.25'
config_defaut['Z0CDRAG_AVE'] = 'y'
config_defaut['CONDVEG_Z0'] = '0.15'
config_defaut['ROUGHHEIGHT'] = '0.0'
config_defaut['CONDVEG_SNOWA'] = 'default'
config_defaut['ALB_BARE_MODEL'] = 'FALSE'
config_defaut['HYDROL_SNOW'] = '0.0'
config_defaut['HYDROL_SNOWAGE'] = '0.0'
config_defaut['HYDROL_SNOW_NOBIO'] = '0.0'
config_defaut['HYDROL_SNOW_NOBIO_AGE'] = '0.0'
config_defaut['HYDROL_HDRY'] = '0.0'
config_defaut['HYDROL_HUMR'] = '1.0'
config_defaut['HYDROL_SOIL_DEPTH'] = '2.0'
config_defaut['HYDROL_HUMCSTE'] = '5., .8, .8, 1., .8, .8, 1., 1., .8, 4., 4., 4., 4.'
config_defaut['HYDROL_BQSB'] = 'default'
config_defaut['HYDROL_GQSB'] = ' 0.0'
config_defaut['HYDROL_DSG'] = '0.0'
config_defaut['HYDROL_DSP'] = 'default'
config_defaut['HYDROL_QSV'] = '0.0'
config_defaut['HYDROL_MOISTURE_CONTENT'] = '0.3'
config_defaut['US_INIT'] = '0.0'
config_defaut['FREE_DRAIN_COEF'] = '1.0, 1.0, 1.0'
config_defaut['EVAPNU_SOIL'] = '0.0'
config_defaut['ENERBIL_TSURF'] = '280.'
config_defaut['ENERBIL_EVAPOT'] = '0.0'
config_defaut['THERMOSOIL_TPRO'] = '280.'
config_defaut['DIFFUCO_LEAFCI'] = '233.'
config_defaut['CDRAG_FROM_GCM'] = 'n'
config_defaut['RVEG_PFT'] = '1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.'
config_defaut['SECHIBA_QSINT'] = '0.1'

# -- LAI --
config_defaut['LAI_MAP'] = 'n'
config_defaut['LAI_FILE'] = 'lai2D.nc'
config_defaut['SLOWPROC_LAI_OLD_INTERPOL'] = 'n'

# -- Land Use --
config_defaut['LAND_USE'] = 'n'
config_defaut['VEGET_YEAR'] = '133'
config_defaut['VEGET_REINIT'] = 'n'
config_defaut['VEGET_LENGTH'] = '1Y'
config_defaut['VEGET_UPDATE'] = '1Y'
config_defaut['LAND_COVER_CHANGE'] = 'n'

# -- Agriculture --
config_defaut['AGRICULTURE'] = 'y'
config_defaut['HARVEST_AGRI'] = 'n' #'y'
config_defaut['HERBIVORES'] = 'n'
config_defaut['TREAT_EXPANSION'] = 'n'

# -- Pas de temps --
config_defaut['SECHIBA_DAY'] = '0.0'
config_defaut['DT_SLOW'] = '86400.'

# -- Hydrologie --
config_defaut['CHECK_WATERBAL'] = 'n'
config_defaut['HYDROL_CWRR'] = 'n'
config_defaut['CHECK_CWRR'] = 'n'
config_defaut['HYDROL_OK_HDIFF'] = 'n'
config_defaut['HYDROL_TAU_HDIFF'] = '86400.'
config_defaut['PERCENT_THROUGHFALL'] = '30.'
config_defaut['PERCENT_THROUGHFALL_PFT'] = '30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30.'
config_defaut['RIVER_ROUTING'] = 'n'
config_defaut['ROUTING_FILE'] = 'routing.nc'
config_defaut['ROUTING_TIMESTEP'] = '86400'
config_defaut['ROUTING_RIVERS'] = '50'
config_defaut['DO_IRRIGATION'] = 'n'
config_defaut['IRRIGATION_FILE'] = 'irrigated.nc'
config_defaut['DO_FLOODPLAINS'] = 'n'


# Modele du fichier run.def lu par ORCHIDEE
# -----------------------------------------
modele_rundef = """
#
#**************************************************************************
#                  Liste des parametres de ORCHIDEE
#**************************************************************************
#
#
#**************************************************************************
#          LISTE D'OPTIONS NON ACTIVEES dans cette simulation
#**************************************************************************
#
#
#**************************************************************************
#      Gestion des affichages au cours du run de ORCHIDEE
#**************************************************************************

# Niveau de 'bavardage' du modele 
# (plus le chiffre est grand plus le modele est bavard)
BAVARD = %(BAVARD)s
# defaut = 1

# Flag pour les informations de debogage
# Cette option permet d'afficher les informations de debogage
#   sans recompiler le code.
DEBUG_INFO = %(DEBUG_INFO)s
#defaut = n

# ORCHIDEE imprimera plus de messages.
#  Il permet d'afficher beaucoup plus de messages sur le deroulement du 
# programme.
LONGPRINT = %(LONGPRINT)s
#defaut = n


#---------------------------------------------------------------------

# Indique si les sorties doivent respecter la convention ALMA
# Si cette option est activee, les sorties du modeles respecteront
#   la convention du projet ALMA. C'est recommande pour ecrire des donnee
#   en sortie d'ORCHIDEE.
ALMA_OUTPUT = %(ALMA_OUTPUT)s
# defaut = n

# Surchage de la variable de temps indiquee dans le forcage de SECHIBA
# Cette option permet d'utilise le temps de redemarrage indique par le GCM
#   et non pas celui donne dans le fichier de restart de SECHIBA.
#   Ce drapeau permet de boucler plusieurs fois sur la meme annee
SECHIBA_reset_time = %(SECHIBA_RESET_TIME)s
# defaut = n

#**************************************************************************
#          Fichiers d'entee / forcages / restart /outputs
#**************************************************************************
# Fichiers divers :
#---------------------------------------------------------------------

# Nom du fichier de vegetation
# Si !IMPOSE_VEG
# Si LAND_USE 
#   defaut = pft_new.nc
#   Le nom du fichier de la carte de vegetation (en pft)
#   doit etre indique ici.
# Si !LAND_USE
#   defaut = ../surfmap/carteveg5km.nc
# C'est le nom du fichier ouvert pour la lecture de la 
#   carte de vegetation. Habituelleemnt, SECHIBA tourne avec
#   une carte 5km x 5km qui vient de celle de IGBP. On suppose que
#   l'on a une classification de 87 types de vegetation. 
#   C'est celle de Olson modifiee par Viovy.
VEGETATION_FILE = %(VEGETATION_FILE)s

# Flag to use old ""interpolation"" of vegetation map.
# IF NOT IMPOSE_VEG and NOT LAND_USE
#  If you want to recover the old (ie orchidee_1_2 branch) 
#   ""interpolation"" of vegetation map.
# default = n
SLOWPROC_VEGET_OLD_INTERPOL = %(SLOWPROC_VEGET_OLD_INTERPOL)s


# Nom du fichier de l'albedo sur sol nu.
# Si !IMPOSE_AZE
# Ce fichier sert a la lecture des types de sol desquels on tire
#   les albedos sur sol nu. Ce fichier est precis au 1x1 degres
#   et base sur les couleurs de sol definies par Wilson et Henderson.
SOILALB_FILE = %(SOILALB_FILE)s
# defaut = ../surfmap/soils_param.nc

# Nom du fichier de types de sol
# Si !IMPOSE_VEG
# C'est le nom du fichier ouvert pour le lecture des types de sol.
#   Les donnees de ce fichier seront interpollees sur la grille du modele.
#   Le but est d'obtenir les fractions de "sand loam" et de "clay" pour chaque 
#   boite de la grille. Cette information est utilisee pour l'hydrologie du sol et
#   la respiration.
SOILTYPE_FILE = %(SOILTYPE_FILE)s
# defaut = ../surfmap/soils_param.nc

# Nom du fichier de reference de temperature
# Ce fichier sert a lire la temperature de reference 
#   la surface. Les donnees sont interpollees sur la 
#   grille du modele. Le but est d'obtenir une temperature
#   aussi bien pour initialiser les variables de pronostique
#   correspondantes du modele correctement (ok_dgvm = TRUE), que 
#   de l'imposer comme une condition aux limite (ok_dgvm = FALSE).
REFTEMP_FILE = %(REFTEMP_FILE)s
# defaut = reftemp.nc

# Fichier de forcage
# Nom du fichier de forcage
# Permet de lire les donnees pour le modele dim0.
# Le format de ce fichier est compatible avec les normes
# NetCDF et COADS. Cabauw.nc, islscp_for.nc, WG_cru.nc, islscp2_for_1982.nc
FORCING_FILE = %(FORCING_FILE)s
# defaut = islscp_for.nc

# lecture et ecriture des fichiers de restart du driver
#---------------------------------------------------------------------

# Nom du fichier de forcage pour les conditions initiales.
#  Ce fichier sera ouvert par le lanceur pour extraire les donnees 
#  en entree du modele. Ce fichier doit etre compatible avec la norme NetCDF, 
#  mais peut ne pas l'etre completement avec la norme COADS. 
#  NONE signifie qu'aucun fichier de forcage n'est lu.
RESTART_FILEIN = %(RESTART_FILEIN)s
# defaut = NONE

# Nom du fichier de restart qui sera cree par le lanceur
RESTART_FILEOUT = %(RESTART_FILEOUT)s
# defaut = driver_rest_out.nc

# lecture et ecriture des fichiers de restart de SECHIBA :
#---------------------------------------------------------------------

# Nom des conditions initiales de redemarrage pour SECHIBA
# C'est le nom du fichier qui est ouvert pour recuperer les valeurs
#   initiales de toutes les variables en entree de SECHIBA.
SECHIBA_restart_in = %(SECHIBA_RESTART_IN)s
# defaut = NONE

# Nom du fichier de restart cree par SECHIBA
# C'est le nom du fichier qui est cree pour ecrire en sortie de SECHIBA
#         les valeurs initiales de toutes les variables en entree de SECHIBA. 
SECHIBA_rest_out = %(SECHIBA_REST_OUT)s
# defaut = sechiba_rest_out.nc

# lecture et ecriture des fichiers de restart de STOMATE :
#---------------------------------------------------------------------

# Nom du fichier de restart pour LIRE les conditions initiales de STOMATE
# Si STOMATE_OK_STOMATE || STOMATE_WATCHOUT
# C'est le nom du fichier qui est ouvert pour recuperer les valeurs
#   initiales de toutes les variables en entree de STOMATE.
STOMATE_RESTART_FILEIN = %(STOMATE_RESTART_FILEIN)s
# defaut = NONE

# Nom du fichier de restart cree par STOMATE
# Si STOMATE_OK_STOMATE || STOMATE_WATCHOUT
# C'est le nom du fichier qui est cree pour ecrire en sortie de STOMATE
#         les valeurs initiales de toutes les variables en entree de STOMATE.
STOMATE_RESTART_FILEOUT = %(STOMATE_RESTART_FILEOUT)s
# defaut = stomate_restart.nc


# lecture et ecriture des fichiers de restart de TESTSTOMATE et FORCESOIL 
# (equilibrage du carbone dans le sol) :
#---------------------------------------------------------------------

# Nom du fichier de forcage de STOMATE
STOMATE_FORCING_NAME = %(STOMATE_FORCING_NAME)s
# defaut = NONE

# Taille de la memoire de STOMATE (en MO)
# Cette taille determine combien de variables de
#  forcage seront conservees en memoire. 
#  Cela donne un compromis entre la memoire et 
#  la frequence des acces disque.
STOMATE_FORCING_MEMSIZE = %(STOMATE_FORCING_MEMSIZE)s
# defaut = 50

# Nom du fichier de forcage du carbone dans STOMATE
# Nom passe a STOMATE pour lire les donnees de carbone en entree
STOMATE_CFORCING_NAME = %(STOMATE_CFORCING_NAME)s
# defaut = NONE


# ecriture des fichiers de forcage (SECHIBA puis STOMATE) :
#---------------------------------------------------------------------

# ORCHIDEE ecrit ses forcages en sortie dans ce fichier.
# Ce drapeau impose l'ecriture d'un fichier (cf WATCHOUT_FILE)
#   contenant les variables de forcage du terrain. 
ORCHIDEE_WATCHOUT = %(ORCHIDEE_WATCHOUT)s
# defaut = n

# Nom du fichier de forcage de ORCHIDEE
# Si ORCHIDEE_WATCHOUT
#   Ce fichier a exactement le meme format qu'un fichier de forcage off-line
#   et peut etre utiliser pour forcer ORCHIDEE en entree (RESTART_FILEIN).
WATCHOUT_FILE = %(WATCHOUT_FILE)s
# defaut = orchidee_watchout.nc

# Le watchout est ecrit a cette frequence
# Si ORCHIDEE_WATCHOUT
# Indique la frequence d'ecriture du fichier watchout.
DT_WATCHOUT = %(DT_WATCHOUT)s
# defaut = dt

# STOMATE effectue un minimum de taches.
# Avec cette option, STOMATE lit et ecrit ses fichiers de demarrage
#   et conserve une sauvegarde des variables biometeorologiques.
#   C'est utile lorsque STOMATE_OK_STOMATE est a no et que l'on desire 
#   activer STOMATE plus tard. Dans ce cas, ce premier calcul sert de
#   constructeur de donnees biometeorologiques a long terme.
STOMATE_WATCHOUT = %(STOMATE_WATCHOUT)s
# defaut = n

# ecriture des fichiers d'outputs (SECHIBA puis STOMATE) :
#---------------------------------------------------------------------
# Nom du fichier dans lequel sont ecrites les donnees historiques
# Ce fichier est cree par le modele pour sauver l'historique des
#   sorties. Il respecte completement les convention COADS et NetCDF.
#   Il est genere par le packqge hist de IOIPSL.
OUTPUT_FILE = %(OUTPUT_FILE)s
# defaut = cabauw_out.nc

# Drapeau pour sauver le fichier histoire 2 de SECHIBA (a haute-frequence ?)
# The drapeau permet d'utiliser la seconde sauvegarde de SECHIBA pour ecrire 
#  les sorties a haute (ou basse frequence). Cette sortie est donc optionnelle
#  et n'est pas activee par defaut.
SECHIBA_HISTFILE2 = %(SECHIBA_HISTFILE2)s
# defaut  = FALSE

# Nom du second fichier de sortie
# Si SECHIBA_HISTFILE2
# The fichier est le second fichier de sortie ecrit par le modele.
SECHIBA_OUTPUT_FILE2 = %(SECHIBA_OUTPUT_FILE2)s
# defaut  = sechiba_out_2.nc

# Nom du fichier histoire de STOMATE
# Le format de ce fichier est compatible avec les normes
#  NetCDF et COADS. 
STOMATE_OUTPUT_FILE = %(STOMATE_OUTPUT_FILE)s
# defaut = stomate_history.nc

# niveaux d'ecriture sur les fichiers de sortie (nombre de variables) :
#---------------------------------------------------------------------

# Niveau d'ecriture pour SECHIBA (entre 0 et 10)
# Choisit la liste des variables ecrites dans le fichier histoire de SECHIBA.
#   Les valeurs vont de 0 (rien n'est ecrit) a 10 (on ecrit tout).
SECHIBA_HISTLEVEL = %(SECHIBA_HISTLEVEL)s
# defaut = 5

# Niveau d'ecriture pour la seconde sortie de SECHIBA (entre 0 et 10)
# Si SECHIBA_HISTFILE2
# Choisit la liste des variables ecrites dans le fichier histoire de SECHIBA.
#   Les valeurs vont de 0 (rien n'est ecrit) a 10 (on ecrit tout).
# Le niveau 1 contient uniquement les sorties de ORCHIDEE.
SECHIBA_HISTLEVEL2 = %(SECHIBA_HISTLEVEL2)s
# defaut = 1

# Niveau des sorties historiques pour STOMATE (0..10)
#  0: rien n'est ecrit; 10: tout est ecrit
STOMATE_HISTLEVEL = %(STOMATE_HISTLEVEL)s
# defaut = 10

# frequences d'ecriture des fichiers d'histoire (en secondes pour SECHIBA et
# en minutes pour STOMATE
#---------------------------------------------------------------------

# Frequence d'ecriture sur les fichiers de sortie (pour SECHIBA en secondes) :
# Cela ne modifie pas la frequence des operations sur les donnees (les moyennes par exemple).
WRITE_STEP = %(WRITE_STEP)s
# defaut = 86400.0

# Frequence en secondes d'ecriture des secondes sorties
# Si SECHIBA_HISTFILE2
# Les variables de la seconde sortie de SECHIBA que le modele
#   ecrira au format netCDF si le drapeau SECHIBA_HISTFILE2 est a TRUE.
WRITE_STEP2 = %(WRITE_STEP2)s
# defaut = 1800.0

# Pas de temps des sauvegardes historiques de STOMATE (d)
# Pour STOMATE, c'est en jours
# Attention, cette variable doit etre plus grande que le DT_SLOW.
STOMATE_HIST_DT = %(STOMATE_HIST_DT)s
# defaut = 10.



#****************************************************************************************
# Optimisation de certains parametres d'ORCHIDEE
#****************************************************************************************

#  Number of levels for the litter: metabolic, structural, and woody (optional)
# default : 2
NLITT = %(NLITT)s

# Active le schema de phenologie + continu dans le temps
# implementation Diego Santaren
IS_PHENO_CONTI = %(IS_PHENO_CONTI)s

# Active l'augmentation de la fraction de C3G en hiver, pour le calcul du fAPAR, 
# lorsque le couvert est compose de PFT6+PFT10
# default = FALSE
IS_FAPAR_TRICK_TBS_C3G = %(IS_FAPAR_TRICK_TBS_C3G)s

# Calcul le fAPAR BLACK SKY ou WHITE SKY
# Black Sky : fAPAR pour SZA a 10h heure locale
# White Sky : fAPAR integre sur la journee
# default = black_sky
FAPAR_COMPUTATION = %(FAPAR_COMPUTATION)s


# Active la prise en compte du calcul du coefficient d'extinction en fonction
# de l'angle solaire et de la structure du couvert
# default = True <=> ext_coeff = 0.5
IS_EXT_COEFF_CONSTANT = %(IS_EXT_COEFF_CONSTANT)s

# Active le module 'parametres optimisables' d'ORCHIDEE
# (y | n)
OPTIMIZATION_ORCHIDEE = %(OPTIMIZATION_ORCHIDEE)s

# Fichier NetCDF d'entree des parametres optimisables
OPTIMIZATION_FILEIN_PARAS = %(OPTIMIZATION_FILEIN_PARAS)s

# Fichier NetCDF de sortie des parametres optimisables.
# >>> Met fin a l'execution d'ORCHIDEE
OPTIMIZATION_FILEOUT_PARAS = %(OPTIMIZATION_FILEOUT_PARAS)s

# Fichier NetCDF de sortie des flux optimises (H,LE,Rn,CO2)
OPTIMIZATION_FILEOUT_FLUXES = %(OPTIMIZATION_FILEOUT_FLUXES)s

# Les flux sont-ils contenus (y/n) dans le fichier de sortie (y par defaut) ?
OPTIMIZATION_FILEOUT_EXTCOEFF = %(OPTIMIZATION_FILEOUT_EXTCOEFF)s
OPTIMIZATION_FILEOUT_NEE = %(OPTIMIZATION_FILEOUT_NEE)s
OPTIMIZATION_FILEOUT_NEET = %(OPTIMIZATION_FILEOUT_NEET)s
OPTIMIZATION_FILEOUT_QH = %(OPTIMIZATION_FILEOUT_QH)s
OPTIMIZATION_FILEOUT_QLE = %(OPTIMIZATION_FILEOUT_QLE)s
OPTIMIZATION_FILEOUT_RN = %(OPTIMIZATION_FILEOUT_RN)s
OPTIMIZATION_FILEOUT_FAPAR = %(OPTIMIZATION_FILEOUT_FAPAR)s
OPTIMIZATION_FILEOUT_FAPART = %(OPTIMIZATION_FILEOUT_FAPART)s
OPTIMIZATION_FILEOUT_ABOBMT = %(OPTIMIZATION_FILEOUT_ABOBMT)s
OPTIMIZATION_FILEOUT_WOODBMT = %(OPTIMIZATION_FILEOUT_WOODBMT)s
OPTIMIZATION_FILEOUT_GPPT = %(OPTIMIZATION_FILEOUT_GPPT)s
OPTIMIZATION_FILEOUT_RESP_HT = %(OPTIMIZATION_FILEOUT_RESP_HT)s
OPTIMIZATION_FILEOUT_RESP_GT = %(OPTIMIZATION_FILEOUT_RESP_GT)s
OPTIMIZATION_FILEOUT_RESP_MT = %(OPTIMIZATION_FILEOUT_RESP_MT)s
OPTIMIZATION_FILEOUT_RESP_H = %(OPTIMIZATION_FILEOUT_RESP_H)s
OPTIMIZATION_FILEOUT_RESP_TER = %(OPTIMIZATION_FILEOUT_RESP_TER)s
OPTIMIZATION_FILEOUT_RESP_TERT = %(OPTIMIZATION_FILEOUT_RESP_TERT)s



#**************************************************************************
#                             Coordonnees du site
#**************************************************************************
#  Le modele utilisera la plus petite des regions entre celle-ci et
#  celle donnee par le fichier de forcage.

# Limite Ouest de la region
# La limite Ouest de la region doit etre comprise en -180. et +180. degres.
LIMIT_WEST = %(LIMIT_WEST)s
# defaut = -180.

# Limite Est de la region
# La limite Est de la region doit etre comprise en -180. et +180. degres.
LIMIT_EAST = %(LIMIT_EAST)s
# defaut = 180.

# Limite Nord de la region
# La limite Nord de la region doit etre comprise en -90. et +90. degres.
LIMIT_NORTH = %(LIMIT_NORTH)s
# defaut = 90.

# Limite Sud de la region
# La limite Sud de la region doit etre comprise en -90. et +90. degres.
LIMIT_SOUTH = %(LIMIT_SOUTH)s
# defaut = -90.

##**************************************************************************
#                       Caracteristiques de la simulation
#**************************************************************************

# Methode de forcage
# Permet d'utiliser la methode dans laquelle le premier niveau
# de donnees atmospheriques n'est pas directement force par des
# observations, mais relaxe ces observations par une constante en temps.
# Pour le moment, la methode tend a trop lisser le cycle diurne et 
# introduisent un decalage en temps. Une methode plus complete est necessaire.
RELAXATION = %(RELAXATION)s
# defaut = n

# Constante de temps pour la methode de relaxation.
# La constante de temps associee a la relaxation 
#  des donnees atmospheriques. Pour eviter trop de ????? 
#  la valeur doit etre superieure a 1000.0
RELAX_A = %(RELAX_A)s
# defaut = 1000.0

# Hauteur a laquelle T et Q sont mesures.
# Les variables atmospheriques (temperature et 
#  humidite specifique) sont mesurees au niveau d'une certaine hauteur.
#  Cette hauteur est necessaire pour calculer correctement les coefficients
#  de transfert turbulent. Regardez dans la description des donnees de
#  forcage pour indiquer la valeur correcte.
HEIGHT_LEV1 = %(HEIGHT_LEV1)s
# defaut = 2.0

# Hauteur a laquelle le vent est donne.
# Cette hauteur est necessaire pour calculer correctement 
#  les coefficients de transfert turbulent. 
HEIGHT_LEVW = %(HEIGHT_LEVW)s
# defaut = 10.0

#---------------------------------------------------------------------
# Generateur d'intemperies :
#---------------------------------------------------------------------

# Generateur d'intermperies
# Cette option declanche le calcul de donnees d'intemperies 
#  si il n'y a pas assez de donnees dans le fichier de forcage
#  par rapport a la resolution temporelle du modele.
ALLOW_WEATHERGEN = %(ALLOW_WEATHERGEN)s
# defaut = n

# Resolution Nord-Sud
# Si l'option ALLOW_WEATHERGEN est activee,
#  indique la resolution Nord-Sud utilisee, en degres.
MERID_RES = %(MERID_RES)s
# defaut = 2.

# Resolution Est-Ouest
# Si l'option ALLOW_WEATHERGEN est activee,
#  indique la resolution Est-Ouest utilisee, en degres.
ZONAL_RES = %(ZONAL_RES)s
# defaut = 2.

# Mode du generateur d'intemperies
# Si ALLOW_WEATHERGEN
# Si cette option vaut 1, on utilise les quantites
#  moyennees par mois pour chaque jour, si il vaut
#  0, alors, on utilise un generateur de nombres
#  aleatoire pour creer les donnees journalieres a
#  partir des donnees mensuelles.
IPPREC = %(IPPREC)s
# defaut = 0

# Interpolation ou pas SI on a un decoupage superieur a 1
# Choisit si vous desirez une interpolation lineaire ou pas.
NO_INTER = %(NO_INTER)s
INTER_LIN = %(INTER_LIN)s
# defaut :
#  NO_INTER = y
#  INTER_LIN = n

# Precipitations mensuelles exactes
# Si ALLOW_WEATHERGEN
# Si cette option est activee, les precipitations mensuelles
#  obtenues avec le generateur aleatoire sont corrigees afin
#  de preserver la valeur moyenne mensuelle.
#  Dans ce cas, on a un nombre constant de jours de precipitations
#   pour chacun des mois. La quantite de precipitations pour ces 
#   jours est constante.
WEATHGEN_PRECIP_EXACT = %(WEATHGEN_PRECIP_EXACT)s
# defaut = n

# Frequence d'appel du generateur d'intemperies
# Cela determine le pas de temps (en secondes) entre deux
#  appels du generateur d'intemperies. Il doit etre superieur
#  au pas de temps de SECHIBA.
DT_WEATHGEN = %(DT_WEATHGEN)s
# defaut = 1800.


# Conservation de la radiation nette pour le forcage.
# Lorsque l'interpolation (INTER_LIN = y) est utilisee, la radiation nette
#  donnee par le forcage n'est pas conservee.
#  Cela peut-etre evite en indiquant y pour cette option.
#  Cette option n'est pas utilisee pour les short-wave si le pas de
#  temps du forcage est superieur a une heure.
#  Cela n'a plus de sens d'essayer de reconstruire un cycle diurne et
#  en meme temps de reconstruire des radiations solaires conservatives en temps.
NETRAD_CONS = %(NETRAD_CONS)s
# defaut = y

# ecriture des resultats du generateur dans un fichier de forcage
# Cette option active la sauvegarde du temps genere dans un fichier
#  de forcage. Cela fonctionne correctement en tant que fichier de restart
#  et non comme condition initiale (dans ce cas, le premier pas de temps
#  est legerement faux) 
DUMP_WEATHER = %(DUMP_WEATHER)s
# defaut = n

# Nom du fichier de forcage des intemperies
# Si DUMP_WEATHER
DUMP_WEATHER_FILE = %(DUMP_WEATHER_FILE)s
# defaut = 'weather_dump.nc'

# Compression des donnees d'intemperies
# Cette option active la sauvegarde du generatuer de temps
#  uniquement pour les points de terre (mode gathered)
# Si DUMP_WEATHER
DUMP_WEATHER_GATHERED = %(DUMP_WEATHER_GATHERED)s
# defaut = y


# Parametres orbitaux

# Effet d'excentricite
# Utilisez la valeur predefinie
# Si ALLOW_WEATHERGEN
ECCENTRICITY = %(ECCENTRICITY)s
# defaut = 0.016724

# Longitude de la perihelie
# Utilisez la valeur predefinie
# Si ALLOW_WEATHERGEN
PERIHELIE = %(PERIHELIE)s
# defaut = 102.04

# oblicite
# Utilisez la valeur predefinie
# Si ALLOW_WEATHERGEN
OBLIQUITY = %(OBLIQUITY)s
# defaut = 23.446

#**************************************************************************
# duree de la simulation :
#---------------------------------------------------------------------
# Duree de la simulation en temps.
# Duree de la simulation. Par defaut, la duree complete du forcage. 
#     Le FORMAT de ce temps peut etre :
# n   : pas de temps n dans le fichier de forcage.
# nS  : n secondes apres le premier pas de temps dans le fichier
# nD  : n jours apres le premier pas de temps
# nM  : n mois apres le premier pas de temps (annees de 365 jours)
# nY  : n annees apres le premier pas de temps (annees de 365 jours)
#        Or combinations :
# nYmM: n years and m month
TIME_LENGTH = %(TIME_LENGTH)s
# defaut  = depend de la duree et du nombre de pas de temps indiques par le
#           fichier de forcage.

# division du pas de temps :
#---------------------------------------------------------------------

# Decoupe le pas de temps donne par le forcage
# Cette valeur divise le pas de temps donne par le fichier de forcage.
#  En principe, on peut l'utiliser pour des calculs en mode explicite
#  mais il est fortement recommande de ne l'utiliser qu'en mode
#  implicite pour que les forcage atmospheriques aient une evolution reguliere.
SPLIT_DT = %(SPLIT_DT)s
# defaut = 12

# Les donnees de forcage meteo sont elles centrees ou non ?
# Les champs meteo sont-ils fournis tous les dt ou bien tous les dt+dt/2 ?
# defaut = n
FORCING_RAD_CENTER = %(FORCING_RAD_CENTER)s

# Decalage en temps de depart par rapport aux donnees de forcage.
# Ce temps est le decalage en temps par rapport au point de depart du fichier 
# de forcage que devrait prendre le modele.
# Si on utilise un fichier de redemarrage, c'est sa date que l'on prend.
# Le FORMAT de ce temps peut etre :
# n   : pas de temps n dans le fichier de forcage.
# nS  : n secondes apres le premier pas de temps dans le fichier
# nD  : n jours apres le premier pas de temps
# nM  : n mois apres le premier pas de temps (annees de 365 jours)
# nY  : n annees apres le premier pas de temps (annees de 365 jours)
#     Ou des combinations :
# nYmM: n annees et m mois
TIME_SKIP = %(TIME_SKIP)s
# defaut = 0

# Decoupage d'une annee pour l'algorithme de convergence du carbone.
FORCESOIL_STEP_PER_YEAR = %(FORCESOIL_STEP_PER_YEAR)s
# defaut = 12

# Nombre d'annees sauvegardees dans le fichier de forcage pour
# pour l'algorithme de convergence du carbone.
FORCESOIL_NB_YEAR = %(FORCESOIL_NB_YEAR)s
# default = 1

# Utilisation des precipitation
# Indique le nombre de fois ou l'on utilise les precipitations
#  pendant le decoupage du pas de temps du forcage.
#  C'est utilise uniquement lorsque le pas de temps de forcage est decoupe (SPLIT_DT).
#  Si on indique un nombre plus grand que SPLIT_DT, il est mis a cette valeur.
SPRED_PREC = %(SPRED_PREC)s
# defaut = 1 



#---------------------------------------------------------------------
# flags a activer selon les cas :
#---------------------------------------------------------------------

# STOMATE active
STOMATE_OK_STOMATE = %(STOMATE_OK_STOMATE)s
# defaut = n

# DGVM active
# Active la vegetation dynamique
STOMATE_OK_DGVM = %(STOMATE_OK_DGVM)s
# defaut = n

# CO2 active
# Active la photosynthese
STOMATE_OK_CO2 = %(STOMATE_OK_CO2)s
# defaut = n

# Drapeau logique pour forcer la valeur du CO2 atmospherique pour la vegetation.
# Si ce drapeau est sur TRUE, le parametre suivant ATM_CO2 indique
#  la valeur utilisee par ORCHIDEE pour le CO2 atmospherique.
# Ce flag n'est utilise qu'en mode couple.
FORCE_CO2_VEG = %(FORCE_CO2_VEG)s
# defaut = FALSE


# CO2 atmospherique
# ---------------------------------------------------------------------------------------

# Valeur du CO2 atmospherique prescrit.
# Si FORCE_CO2_VEG (uniquement en mode couple)
# Cette veleur donne le CO2 atm prescrit.
#  Pour les simulations pre-industriellles, la valeur est 286,2.
#  Pour l'annee 1990 la valeur est 348.
ATM_CO2 = %(ATM_CO2)s
# defaut = 350.

# Fichier NetCDF de valeur pour le CO2 atmospherique.
#  Si !=NONE, les valeurs seront lues dans ce fichier et varieront annuellement,
#  plutot que d'etre assignees a la valeur constante ATM_CO2 definie precedemment
ATM_CO2_FILE = %(ATM_CO2_FILE)s

# Annee de depart du vecteur des valeurs de CO2 atmospherique a lire dans le fichier
# ATM_CO2_FILE
# -1 par defaut => gestion automatique en fonction des annees de forcage meteorologique
YEAR_ATMCO2_START = %(YEAR_ATMCO2_START)s


# Index du point de grille des diagnostics on-line
# Donne la longitude et la latitude du point de terre dont l'indice
#   est donne par ce parametre.
STOMATE_DIAGPT = %(STOMATE_DIAGPT)s
# defaut = 1

# Constante de mortalite des arbres
# Si cette option est activee, une mortalite constante des arbres est
#   imposee. Sinon, la mortalite est une fonction de la vigueur des arbres
#   (comme dans le LPJ).
LPJ_GAP_CONST_MORT = %(LPJ_GAP_CONST_MORT)s
# defaut = y

# Pas de feux
# Avec cette variable, on peut ou non estimer la quantite de CO2 
#   produite par un feu.
FIRE_DISABLE = %(FIRE_DISABLE)s
# defaut = n

#
#**************************************************************************
#     Nouvelles options pour les restarts a partir de la version 1.9.3
#**************************************************************************
#
## sechiba
soilcap=%(SOILCAP)s
soilflx=%(SOILFLX)s
shumdiag=%(SHUMDIAG)s
runoff=%(RUNOFF)s
drainage=%(DRAINAGE)s

## diffuco
raero=%(RAERO)s
qsatt=%(QSATT)s
cdrag=%(CDRAG)s

## enerbil
evapot_corr=%(EVAPOT_CORR)s
temp_sol_new=%(TEMP_SOL_NEW)s

## hydrolc
dss=%(DSS)s
hdry=%(HDRY)s

## thermosoil
cgrnd=%(CGRND)s
dgrnd=%(DGRND)s
z1=%(Z1)s
pcapa=%(PCAPA)s
pcapa_en=%(PCAPA_EN)s
pkappa=%(PKAPPA)s
zdz1=%(ZDZ1)s
zdz2=%(ZDZ2)s
temp_sol_beg=%(TEMP_SOL_BEG)s

# parametres decrivant la surface (vegetation + sol) :
#---------------------------------------------------------------------
#
# La vegetation doit-elle etre imposee ?
# Cette option permet d'imposer la distribution de la vegetation 
#   quand on travaille sur un seul point. Sur le globe, cela n'a
#   pas de sens d'imposer la meme vegetation partout.
IMPOSE_VEG = %(IMPOSE_VEG)s
# defaut = n

# A enlever du code !!! calcul impose par la lai (cf slowproc_veget) et veget_max
# Distribution de la vegetation par rapport au maillage
# Si IMPOSE_VEG
# Parametres prescrits pour la vegetation dans les cas 0-dim.
#   Les fractions de vegetation (PFTs) sont lus dans le fichier de restart 
#   ou imposees par ces valeurs.
#   Fraction de VEGET_MAX (parametre par la LAI donc).
SECHIBA_VEG__01 = %(SECHIBA_VEG__01)s
SECHIBA_VEG__02 = %(SECHIBA_VEG__02)s
SECHIBA_VEG__03 = %(SECHIBA_VEG__03)s
SECHIBA_VEG__04 = %(SECHIBA_VEG__04)s
SECHIBA_VEG__05 = %(SECHIBA_VEG__05)s
SECHIBA_VEG__06 = %(SECHIBA_VEG__06)s
SECHIBA_VEG__07 = %(SECHIBA_VEG__07)s
SECHIBA_VEG__08 = %(SECHIBA_VEG__08)s
SECHIBA_VEG__09 = %(SECHIBA_VEG__09)s
SECHIBA_VEG__10 = %(SECHIBA_VEG__10)s
SECHIBA_VEG__11 = %(SECHIBA_VEG__11)s
SECHIBA_VEG__12 = %(SECHIBA_VEG__12)s
SECHIBA_VEG__13 = %(SECHIBA_VEG__13)s
# defaut = 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0

# Distribution du maximum de vegetation par rapport au maillage
# Si IMPOSE_VEG
#   Parametres prescrits pour la vegetation dans les cas 0-dim.
#   Les fractions maximum de vegetation (PFTs) sont lus dans le fichier de restart 
#   ou imposees par ces valeurs.
SECHIBA_VEGMAX__01 = %(SECHIBA_VEGMAX__01)s
SECHIBA_VEGMAX__02 = %(SECHIBA_VEGMAX__02)s
SECHIBA_VEGMAX__03 = %(SECHIBA_VEGMAX__03)s
SECHIBA_VEGMAX__04 = %(SECHIBA_VEGMAX__04)s
SECHIBA_VEGMAX__05 = %(SECHIBA_VEGMAX__05)s
SECHIBA_VEGMAX__06 = %(SECHIBA_VEGMAX__06)s
SECHIBA_VEGMAX__07 = %(SECHIBA_VEGMAX__07)s
SECHIBA_VEGMAX__08 = %(SECHIBA_VEGMAX__08)s
SECHIBA_VEGMAX__09 = %(SECHIBA_VEGMAX__09)s
SECHIBA_VEGMAX__10 = %(SECHIBA_VEGMAX__10)s
SECHIBA_VEGMAX__11 = %(SECHIBA_VEGMAX__11)s
SECHIBA_VEGMAX__12 = %(SECHIBA_VEGMAX__12)s
SECHIBA_VEGMAX__13 = %(SECHIBA_VEGMAX__13)s
# defaut = 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0

# Distribution du LAI pour tous les types de vegetation (0-dim)
# Si IMPOSE_VEG
# C'est la LAI maximale utilisee dans les cas 0-D. Ces valeurs sont 
#   utilisees si elles ne sont pas dans le fichier de restart.
#   Les nouvelles valeurs de la LAI sont quand meme calculees a la fin du 
#   premier jour. On a besoin de ces valeurs si le modele s'arrete avant la fin
#   du jour et que l'on n'ai pas passe par les procedures calculant ces valeurs
#   pour obtenir les nouvelles conditions de surface.
SECHIBA_LAI__01 = %(SECHIBA_LAI__01)s
SECHIBA_LAI__02 = %(SECHIBA_LAI__02)s
SECHIBA_LAI__03 = %(SECHIBA_LAI__03)s
SECHIBA_LAI__04 = %(SECHIBA_LAI__04)s
SECHIBA_LAI__05 = %(SECHIBA_LAI__05)s
SECHIBA_LAI__06 = %(SECHIBA_LAI__06)s
SECHIBA_LAI__07 = %(SECHIBA_LAI__07)s
SECHIBA_LAI__08 = %(SECHIBA_LAI__08)s
SECHIBA_LAI__09 = %(SECHIBA_LAI__09)s
SECHIBA_LAI__10 = %(SECHIBA_LAI__10)s
SECHIBA_LAI__11 = %(SECHIBA_LAI__11)s
SECHIBA_LAI__12 = %(SECHIBA_LAI__12)s
SECHIBA_LAI__13 = %(SECHIBA_LAI__13)s
# defaut = 0., 8., 8., 4., 4.5, 4.5, 4., 4.5, 4., 2., 2., 2., 2.

# Hauteur pour tous les types de vegetation (0-dim)
# Si IMPOSE_VEG
# C'est la hauteur utilisee dans les cas 0-D. Ces valeurs sont 
#   utilisees si elles ne sont pas dans le fichier de restart.
#   Les nouvelles valeurs de la hauteur sont quand meme calculees a la fin du 
#   premier jour. On a besoin de ces valeurs si le modele s'arrete avant la fin
#   du jour et que l'on n'ai pas passe par les procedures calculant ces valeurs
#   pour obtenir les nouvelles conditions de surface.
SLOWPROC_HEIGHT__01 = %(SLOWPROC_HEIGHT__01)s
SLOWPROC_HEIGHT__02 = %(SLOWPROC_HEIGHT__02)s
SLOWPROC_HEIGHT__03 = %(SLOWPROC_HEIGHT__03)s
SLOWPROC_HEIGHT__04 = %(SLOWPROC_HEIGHT__04)s
SLOWPROC_HEIGHT__05 = %(SLOWPROC_HEIGHT__05)s
SLOWPROC_HEIGHT__06 = %(SLOWPROC_HEIGHT__06)s
SLOWPROC_HEIGHT__07 = %(SLOWPROC_HEIGHT__07)s
SLOWPROC_HEIGHT__08 = %(SLOWPROC_HEIGHT__08)s
SLOWPROC_HEIGHT__09 = %(SLOWPROC_HEIGHT__09)s
SLOWPROC_HEIGHT__10 = %(SLOWPROC_HEIGHT__10)s
SLOWPROC_HEIGHT__11 = %(SLOWPROC_HEIGHT__11)s
SLOWPROC_HEIGHT__12 = %(SLOWPROC_HEIGHT__12)s
SLOWPROC_HEIGHT__13 = %(SLOWPROC_HEIGHT__13)s
# defaut = 0., 30., 30., 20., 20., 20., 15., 15., 15., .5, .6, 1.0, 1.0

# Fraction des 3 types de sol (0-dim mode)
# Si IMPOSE_VEG
# Determine la fraction des 3 types de sol
#  dans le maillage selon l'ordre : sand loam and clay.
SOIL_FRACTIONS__01 = %(SOIL_FRACTIONS__01)s
SOIL_FRACTIONS__02 = %(SOIL_FRACTIONS__02)s
SOIL_FRACTIONS__03 = %(SOIL_FRACTIONS__03)s
# defaut = 0.28, 0.52, 0.20


# Temperature utilisee pour l'initialisation de la LAI
# Si il n'y a pas de LAI dans le fichier de redemarrage,
#  c'est cette temperature qui est utilisee  pour la LAI initial.
SLOWPROC_LAI_TEMPDIAG = %(SLOWPROC_LAI_TEMPDIAG)s
# defaut = 280.

# Niveau de sol (en m) utilise pour les calculs de canopee 
# Si STOMATE n'est pas active
# La temperature a une profondeur du sol est utilisee pour 
#   determiner la LAI lorsque STOMATE n'est pas active.
SECHIBA_ZCANOP = %(SECHIBA_ZCANOP)s
# defaut = 0.5

# Fraction des autres types de surface dans le maillage (0-D)
# Si IMPOSE_VEG
# Indique la fraction de glace, lacs, etc... si elle n'est pas donnee
#   dans le fichier de redemarrage. Pour l'instant, il n'y a que de la 
#   glace.
#   Q :laisser ca tant qu'il n'y a que la glace. Pb avec setvar?????
SECHIBA_FRAC_NOBIO = %(SECHIBA_FRAC_NOBIO)s
# defaut = 0.0

# Fraction de l'argile (0-D)
# Si IMPOSE_VEG
# Determine la fraction de l'argile dans la case
CLAY_FRACTION = %(CLAY_FRACTION)s
# defaut = 0.2

# Les parametres de surface doivent etre donnes.
# Cette option permet d'imposer les parametres de surface
#   (albedo, rugosite, emission). C'est surtout utilise
#   pour les simulations sur un point. Sur le globe, cela n'a
#   pas de sens d'imposer les memes parametres partout.
IMPOSE_AZE = %(IMPOSE_AZE)s
# defaut = n

# Emission des radiations ondes longues.
# Si IMPOSE_AZE
# L'emissivite de surface sont utilisees pour calculer les emissions _LE_ ??
#   de la surface dans les calculs sur un point. Les valeurs doivent 
#   etre comprises entre 0.97 et 1. Le GCM utilise 0.98.
CONDVEG_EMIS = %(CONDVEG_EMIS)s
# defaut = 1.0

# Albedo de surface dans la gamme du visible.
# Si IMPOSE_AZE
# L'albedo de surface dans la gamme de longueur d'ondes 
#   du visible pour les tests sur un point. 
#   Regardez dans un fichier de forcage pour imposer une valeur correcte.
CONDVEG_ALBVIS = %(CONDVEG_ALBVIS)s
# defaut = 0.25

# Albedo de surface dans la gamme des infrarouges.
# Si IMPOSE_AZE
# L'albedo de surface dans la gamme de longueur d'ondes 
#   des infrarouges pour les tests sur un point. 
#   Regardez dans un fichier de forcage pour imposer une valeur correcte.
CONDVEG_ALBNIR = %(CONDVEG_ALBNIR)s
# defaut = 0.25

# Methode de moyennage pour la rugosite de surface z0
# Si ce drapeau est place a 'y', alors le __Cdrag neutre__?? est moyenne
#   plutot que le log(z0). Il est preferable d'utiliser cette premiere 
#   methode. 
Z0CDRAG_AVE = %(Z0CDRAG_AVE)s
# defaut = y 

# Rugosite de surface z0 (m)
# Si IMPOSE_AZE
# La rugosite de surface pour les tests sur un point. 
#   Regardez dans un fichier de forcage pour imposer une valeur correcte.
CONDVEG_Z0 = %(CONDVEG_Z0)s
# defaut = 0.15

# Hauteur a ajouter a la hauteur du premier niveau (en m)
# Si IMPOSE_AZE
# ORCHIDEE suppose que la hauteur du niveau atmospherique est egale
#   au niveau 0 du vent. Aussi, pour prendre en compte la rugosite 
#   due a la vegetation, on doit la corriger par une fraction de la hauteur 
# de vegetation. On l'appelle hauteur de rugosite.
ROUGHHEIGHT = %(ROUGHHEIGHT)s
# defaut = 0.0

# Nom du fichier de l'albedo de sol 
# L'albedo de la neige utilise dans SECHIBA
# Avec cette option, on peut impose l'albedo de la neige.
#   Lorsque l'on prend la valeur par defaut, on utilise
#   le modele d'albedo de neige developpe par Chalita en 1993.
CONDVEG_SNOWA = %(CONDVEG_SNOWA)s
# defaut = modele de Chalita.


# Permet de chifter entre les formulation du calcul de l'albedo du sol nu.
# Si ce parametre est a TRUE, c'est l'ancien modele qui est utilise. L'albedo du
#  sol nu dependra alors de l'humidite du sol. Si il est mis a FALSE, 
#  l'albedo du sol nu sera uniquement fonction de la couleur du sol.
ALB_BARE_MODEL = %(ALB_BARE_MODEL)s
# defaut = FALSE

# Masse de neige initiale si pas dans le fichier de redemarrage.
# La valeur initiale de la masse de neige lorsque l'on a pas de 
#  fichier de restart.
HYDROL_SNOW = %(HYDROL_SNOW)s
# defaut = 0.0

# L'age de la neige initiale si pas dans le fichier de redemarrage.
# La valeur initiale de l'age de la neige lorsque l'on a pas de 
#  fichier de restart.
HYDROL_SNOWAGE = %(HYDROL_SNOWAGE)s
# defaut = 0.0

# Le taux de neige initiale sur la glace, les lacs, etc ...
# La valeur initiale du taux de neige sur la glace, les lacs
#  lorsque l'on a pas de fichier de restart.
HYDROL_SNOW_NOBIO = %(HYDROL_SNOW_NOBIO)s
# defaut = 0.0

# L'age de la neige initiale sur la glace, les lacs ...
# La valeur initiale de l'age de la neige sur la glace, les lacs,
#   lorsque l'on a pas de fichier de restart.
HYDROL_SNOW_NOBIO_AGE = %(HYDROL_SNOW_NOBIO_AGE)s
# defaut = 0.0

# Hauteur initiale du sol sec dans les Tags ORCHIDEE_1.3 a 1.5.
# La valeur hauteur initiale du sol sec lorsque l'on a pas de 
# fichier de restart.
HYDROL_HDRY = %(HYDROL_HDRY)s
# defaut = 0.0

# Contrainte d'humidite initiale du sol
# C'est la valeur initiale de la contrainte d'humidite du sol
#   si elle n'est pas dans le fichier de redemarrage.
HYDROL_HUMR = %(HYDROL_HUMR)s
# defaut = 1.0


# Profondeur totale du reservoir du sol
HYDROL_SOIL_DEPTH = %(HYDROL_SOIL_DEPTH)s
# defaut = 2.

# Profondeur racinaire
HYDROL_HUMCSTE = %(HYDROL_HUMCSTE)s
# defaut =  5., .8, .8, 1., .8, .8, 1., 1., .8, 4., 4., 4., 4.

# Humidite initiale profonde du sol
# C'est la valeur initiale de l'humidite profonde du sol
#   si elle n'est pas dans le fichier de redemarrage.
#   La valeur par defaut est le sol sature.
HYDROL_BQSB = %(HYDROL_BQSB)s
# defaut = Maximum quantity of water (Kg/M3) * Total depth of soil reservoir = 150. * 2

# Humidite initiale superficielle du sol
# C'est la valeur initiale de l'humidite superficielle du sol
#   si elle n'est pas dans le fichier de redemarrage.
HYDROL_GQSB = %(HYDROL_GQSB)s
# defaut = 0.0

# Profondeur initiale du reservoir superficiel
# C'est la valeur initiale de la profondeur du reservoir superficiel
#   si elle n'est pas dans le fichier de redemarrage.
HYDROL_DSG = %(HYDROL_DSG)s
# defaut = 0.0

# Assechement initial au dessus du reservoir superficiel
# C'est la valeur initiale de l'assechement au dessus du reservoir superficiel
#   si elle n'est pas dans le fichier de redemarrage.
#   La valeur par defaut est calculee d'apres les grandeurs precedentes.
#   Elle devrait etre correcte dans la plupart des cas.
HYDROL_DSP = %(HYDROL_DSP)s
# defaut = Total depth of soil reservoir - HYDROL_BQSB / Maximum quantity of water (Kg/M3) = 0.0

# Quantite initiale de l'eau dans la canopee
#  si elle n'est pas dans le fichier de redemarrage.
HYDROL_QSV = %(HYDROL_QSV)s
# defaut = 0.0

# Humidite du sol sur chaque carreau et niveau
# La valeur initiale de mc si elle n'est pas dans le fichier
#   de redemarrage.
HYDROL_MOISTURE_CONTENT = %(HYDROL_MOISTURE_CONTENT)s
# defaut = 0.3

# US_NVM_NSTM_NSLM
# La valeur initiale de l'humidite relative 
#   si elle n'est pas dans le fichier de redemarrage.
US_INIT = %(US_INIT)s
# defaut = 0.0

# Coefficients du drainage libre en sous-sol
# Indique les valeurs des coefficients du drainage libre.
FREE_DRAIN_COEF = %(FREE_DRAIN_COEF)s
# defaut = 1.0, 1.0, 1.0

# evaporation sur sol brut pour chaque sol
#   si elle n'est pas dans le fichier de redemarrage.
EVAPNU_SOIL = %(EVAPNU_SOIL)s
# defaut = 0.0

# Temperature de surface initiale
#   si elle n'est pas dans le fichier de redemarrage.
ENERBIL_TSURF = %(ENERBIL_TSURF)s
# defaut = 280.

# Potentiel initial d'evaporation du sol
#   si elle n'est pas dans le fichier de redemarrage.
ENERBIL_EVAPOT = %(ENERBIL_EVAPOT)s
# defaut = 0.0

# Profil initial de temperature du sol si il n'est pas dans le restart
# La valeur initiale du profil de temperarure du sol. Cela ne devrait etre 
#   utilise qu'en cas de redemarrage du modele. On ne prend qu'une valeur ici
#   car on suppose la temperature constante le long de la colone.
THERMOSOIL_TPRO = %(THERMOSOIL_TPRO)s
# defaut = 280.

# Niveau initial du CO2 dans les feuilles
#   si il n'est pas dans le fichier de redemarrage.
DIFFUCO_LEAFCI = %(DIFFUCO_LEAFCI)s
# defaut = 233.

# Conservation du cdrag du gcm.
# Placer ce parametre a .TRUE. si vous desirez conserver le q_cdrag calcule par le GCM.
#  Conservation du coefficient cdrag du gcm pour le calcul des flux de chaleur latent et sensible..
#  TRUE si q_cdrag vaut zero a l'initialisation (et FALSE pour les calculs off-line).
CDRAG_FROM_GCM = %(CDRAG_FROM_GCM)s
# defaut =  SI q_cdrag == 0 ldq_cdrag_from_gcm = .FALSE. SINON .TRUE.

# Bouton articificiel pour regler la croissance ou decroissance de la resistance de la canopee.
# Ajout de Nathalie - 28 Mars 2006 - sur les conseils de Frederic Hourdin.
# Par PFT.
RVEG_PFT = %(RVEG_PFT)s
# defaut = 1.

# Coefficient de reservoir d'interception.
# Ce coefficient indique la quantite de LAI transforme en taille du reservoir  ????
#  d'interception pour slowproc_derivvar ou stomate. ????
SECHIBA_QSINT = %(SECHIBA_QSINT)s
# defaut = 0.1



#**************************************************************************
# LAI
#**************************************************************************

# Lecture de la carte de LAI
# Permet la lecture d'une carte de LAI
#  Si n => modele impose entre LAI_min et LAI_max, 
#  suivant le tableau type_of_lai (dans constantes_veg.f90)
#     - mean    : lai(ji,jv) = undemi * (llaimax(jv) + llaimin(jv))
#     - inter   : llaimin(jv) + tempfunc(stempdiag(ji,lcanop)) * (llaimax(jv) - llaimin(jv))
# la carte n'est pas lue si un seul point ??
LAI_MAP = %(LAI_MAP)s
# defaut = n

# Nom du fichier de LAI
# Si LAI_MAP
# C'est le nom du fichier ouvert pour la lecture de la 
#   carte de LAI. Habituelleemnt, SECHIBA tourne avec
#   une carte 5km x 5km qui vient de celle de Nicolas Viovy.
LAI_FILE = %(LAI_FILE)s
# defaut = ../surfmap/lai2D.nc

# Drapeau pour utiliser la vieille "interpolation" de la LAI.
# Si LAI_MAP
#  Si vous desirez reproduire des resultats obtenus avec l'ancienne "interpolation"
#  de la carte de LAI, activez ce drapeau.
SLOWPROC_LAI_OLD_INTERPOL = %(SLOWPROC_LAI_OLD_INTERPOL)s
# defaut = n

#**************************************************************************

#**************************************************************************
# LAND_USE
#**************************************************************************

# Lecture d'une carte de vegetation pour le land_use
# On modifie les proportions des differentes pft
LAND_USE = %(LAND_USE)s
# defaut = n

# Annee de lecture de la carte de vegetation pour le land_use
# Decalage en annee de la lecture de la carte de land_use
# Pour un fichier de vegetation avec une seule annee, sans axe de temps,
# on indique ici VEGET_YEAR=0.
# La valeur par defaut est 133 pour designer l'annee 1982  
# (car 1982 - 1850 + 1 = 133)
# Si LAND_USE
# If LAND_USE
VEGET_YEAR = %(VEGET_YEAR)s
# defaut = 133

# Ce logique indique qu'une nouvelle carte de LAND USE va etre utilisee (depuis 1.9.5 version).
# Ce parametre sert a eviter le compteur veget_year present dans 
# le restart de SECHIBA et permet de le reinitialiser a une nouvelle valeure indiquee 
# par le parametre VEGET_YEAR.
# Il ne doit donc etre utilise que lors d'un changement de fichier de LAND USE.
# If LAND_USE
VEGET_REINIT = %(VEGET_REINIT)s
# defaut = n

# Frequence de mise a jour de la carte de vegetation (jusqu'a la version 1.9)
# Les donnees veget seront mises a jour avec ce pas de temps
# Si LAND_USE
VEGET_LENGTH = %(VEGET_LENGTH)s
# defaut = 1Y

# Frequence de mise a jour de la carte de vegetation (a partir de la version 2.0)
# Les donnees veget seront mises a jour avec ce pas de temps
# Si LAND_USE
VEGET_UPDATE = %(VEGET_UPDATE)s
# defaut = 1Y

# Utilisation des sols et deforestation
# Prend en compte les modifications dues a l'utilisation des sols,
# notament l'impact de la deforestation.          
# Si LAND_USE
LAND_COVER_CHANGE = %(LAND_COVER_CHANGE)s
# defaut = n


#**************************************************************************

# Calcule-t-on l'agriculture ?
# On determine ici si l'on calcule l'agriculture.
AGRICULTURE = %(AGRICULTURE)s
# defaut = y

# Modele de moisson pour les PFTs agricoles.
# Traite la reorganisation de la biomasse apres les moissons pour l'agriculture.
# Change les turnover journaliers. 
HARVEST_AGRI = %(HARVEST_AGRI)s
# defaut = y

# Modelise-t-on les herbivores ?
# Cette option declanche la modelisation des effets des herbivores.
HERBIVORES = %(HERBIVORES)s
# defaut = n

# L'expansion des PFTs peut-elle depasser d'une maille ?
# L'activation de cette option autorise les expansions des PFTs
#   a traverser les mailles.
TREAT_EXPANSION = %(TREAT_EXPANSION)s
# defaut = n

#**************************************************************************

# Compteur de jour de simulation
# Cette variable est utilisee par les processus a calculer une
#   seule fois par jour.
SECHIBA_DAY = %(SECHIBA_DAY)s
# defaut = 0.0

# Pas de temps de STOMATE et les autres processus lents
# Pas de temps (en s) de la mise a jour de la couverture 
#   de vegetation, du LAI, etc.  C'est aussi le pas de temps de STOMATE
DT_SLOW = %(DT_SLOW)s
# defaut = un_jour = 86400.

#**************************************************************************

# Flag pour tester le bilan de l'eau
# Ce parametre active la verification
#  du bilan d'eau entre deux pas de temps.
CHECK_WATERBAL = %(CHECK_WATERBAL)s
# defaut = n

# Permet l'utilisation du modele hydrologique multi-couches de Patricia De Rosnay
# Cette option declanche l'utilisation du modeles 11 couches pour l'hydrologie verticale.
#   Cette modelisation utilise une diffusion verticale adapte de CWRR de Patricia De Rosnay.
#   Sinon, on utilise l'hydrologie standard dite de Choisnel.
HYDROL_CWRR = %(HYDROL_CWRR)s
# defaut = n

# Verifie le bilan d'eau pour le modele CWRR.
# Ce parametre permet de tester en detail le bilan
#  d'eau entre chaque pas de temps pour le modele d'hydrologie CWRR.
CHECK_CWRR = %(CHECK_CWRR)s
# defaut = n

# Faire de la diffusion horizontale ?
# Si TRUE, alors l'eau peut diffuser dans les directions horizontales
#  en les reservoirs d'eau des PFT.
HYDROL_OK_HDIFF = %(HYDROL_OK_HDIFF)s
# defaut = n

# Temps de latence (en s) pour la diffusion horizontale de l'eau
# Si HYDROL_OK_HDIFF
# Definit la vitesse de diffusion horizontale entre chaque
#  reservoirs d'eau des PFT. Une valeur infinie indique que 
#  l'on a pas de diffusion.
HYDROL_TAU_HDIFF = %(HYDROL_TAU_HDIFF)s
# default = 86400.

# Pourcentage des precipitations qui ne sont pas interceptees par la canopee (seulement pour le TAG 1.6).
# Pendant un evenement pluvieux PERCENT_THROUGHFALL pourcentage de la pluie va directement 
#  au sol sans etre intercepte par les feuilles de la vegetation.
PERCENT_THROUGHFALL = %(PERCENT_THROUGHFALL)s
# defaut = 30.

# Pourcentage par PFT des precipitations qui ne sont pas interceptees par la canopee (a partir du TAG 1.8).
# Pendant un evenement pluvieux PERCENT_THROUGHFALL_PFT pourcentage de la pluie va directement 
#  au sol sans etre intercepte par les feuilles de la vegetation, pour chaque PFT.
PERCENT_THROUGHFALL_PFT = %(PERCENT_THROUGHFALL_PFT)s
# defaut = 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30.


# Option pour la transmission des rivieres
# Cette option declanche l'ecoulement et le drainage de l'eau
#   jusqu'aux oceans et vers les __rivieres souterraines__ ??
RIVER_ROUTING = %(RIVER_ROUTING)s
# defaut = n

# Nom du fichier qui contient les informations de routage.
# Le fichier permet au module du routage de lire les grilles
#   a resolution haute frequence des bassins et les directions 
#   d'ecoulement d'un maillage a l'autre.
ROUTING_FILE = %(ROUTING_FILE)s
# defaut = routing.nc

# Pas de temps du routage
# Si RIVER_ROUTING
# Indique le pas de temps en secondes pour le schema de routage.
#   Ce nombre doit etre un mutliple du pas de temps d'ORCHIDEE.
#   Un jour est une bonne valeur.
ROUTING_TIMESTEP = %(ROUTING_TIMESTEP)s
# defaut = 86400

# Nombre de rivieres
# Si RIVER_ROUTING
# Ce parametre donne le nombre de rivieres dans les grands bassins.
#   Ces rivieres seront traites separement et ne diffuseront pas ensembles
#   vers les cotes et les oceans.
ROUTING_RIVERS = %(ROUTING_RIVERS)s
# defaut = 50

# Doit-on calculer les flux d'irrigation ?
# En cas de routage, on calcule les flux d'irrigation. 
#   C'est fait avec une hypothese simple : on souhaite avoir une carte
#   correcte des zones d'irrigation et on a une fonction simple qui
#   estime les besoins en irrigation.
DO_IRRIGATION = %(DO_IRRIGATION)s
# defaut = n

# Nom du fichier qui contient la carte des zones irriguees.
# Si IRRIGATE
# Le nom du fichier qui est ouvert pour lire un champ
#   avec une zone en m^2 des zones irriguees a l'interieur de 
#   chaque maille 0.5 par 0.5 degres de la grille. La carte courrante
#   est celle utilisee par le ""Center for Environmental Systems Research"" 
#  in Kassel (1995).
IRRIGATION_FILE = %(IRRIGATION_FILE)s
# defaut = irrigated.nc

# Doit-on calculer les inondations en plaine ?
# Ce drapeau force le modele a ternir compte des inondations en plaine.
#   Et l'eau 
DO_FLOODPLAINS = %(DO_FLOODPLAINS)s
# defaut = n

#**************************************************************************

"""

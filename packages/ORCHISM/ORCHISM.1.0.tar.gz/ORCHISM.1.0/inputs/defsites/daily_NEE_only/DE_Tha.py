# ==============================================================================
# FI_Hyy 1997
# ==============================================================================
class Data_site:  

    # -- Fluxes and data on which assimilation is performed
    obsname = ['NEEt']

    nannees   = 3
    nmois     = nannees * 12
    njours    = nannees * 365
    nsemaines = nannees * 52
    
    # -- Initialize dictionary
    vars = {}
    for name in obsname :  vars[name] = {}


    # -- Forcing file 
    fic_forc = '/your/working/directory/ORCHISM/inputs/forcing/DE-Tha1997-1999.nc'
    
    # -- Configuration file
    fic_cfg = '/your/working/directory/ORCHISM/inputs/config/daily/DE-Tha.cfg'
    
    # -- Observation files 
    fic_obs = '/your/working/directory/ORCHISM/inputs/fluxes/DE-Tha_flux_1997-1999.nc'
      
    for name in obsname :
        vars[name]['fic_obs'] = fic_obs

        #vars[name]['fic_sim'] = None

        #vars[name]['name_obs'] = name           # name of variable in the input observation file
        #vars[name]['name_sim'] = name           # name of the variable in the ORCHIDEE output file

        #vars[name]['time_counter_obs'] = 'time_counter'
        #vars[name]['time_counter_sim'] = 'time_counter'


    # -- Processing
    for name in obsname :
        vars[name]['processing_obs'] = 'daily'
        vars[name]['processing_sim'] = ''
    
    
    # -- Errors
    vars['NEEt']['sigma'] = 2
    #vars['Qh']['sigma'] =  21
    #vars['Qle']['sigma'] =  10 / 1.5
    
  
# ==============================================================================

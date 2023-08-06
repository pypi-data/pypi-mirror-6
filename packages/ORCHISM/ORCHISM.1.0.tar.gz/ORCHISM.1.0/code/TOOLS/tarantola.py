#!/usr/bin/env python
#*******************************************************************************
# MODULE	: TARANTOLA
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 11/2007
# LAST MODIF    : 08/2012
# COMPILER	: PYTHON
#
"""
Posterior information on the observations and parameters
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import os
from orchis_config import Config
import numpy as np

#from TOOLS import io
import io

# ==============================================================================
# 1. Determine the posterior uncertainties on parameters
# 2. Determine the n+1 estimation of the parameter set according to Tarantola
#    (p195 - eq 4.19)
# based on the TARANTOLA_REF written by P. Peylin & C. Carouge
#
# The algorithm compute the vector of estimated parameters m as well as the
# posterior covariance matrix on parameters according to Tarantola (eq 4.26a & 4.26b) :
#
# The posterior covariance matrix on parameters is defined as B' = [B^-1 + G^t*R^-1+G ]^-1
# with B : the prior covariance matrix on the parameters
#      R : the prior covariance matrix on observations
#      G : the jacobian matrix of the model at the solution
# 
# The routine is written in F90 and require as input :
#  - a text file specifying the various options
#  - a binary file (BIG ENDIAN)
# ------------------------------------------------------------------------------

def detpost_paras(Data, Site, Opti, logfile, 
                  file_matcov_out = None,
                  file_matcor_out = None,
                  case            = None,
                  opti_varname    = None):
    
    
    # ------------------------------------------------------------
    # --- Writing of the input text file for tarantola_ref.f90 ---
    # ------------------------------------------------------------
    f = open( os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['input_file_dat']),'w')
    f.write("'"+os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['input_file_bin'])+"'\n")
    f.write("'"+os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['output_file_bin'])+"'\n")
    f.write("'"+os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['tempo_file_bin'])+"'\n")
    f.write("0\n0\n0\n1\n0\n0\n0\n0\n' '\n0\n1\n' '\n")
    f.close()

    # --------------------------------------------------------------
    # --- Writing of the input binary file for tarantola_ref.f90 ---
    # --------------------------------------------------------------
    swapendian = 0
    if Config.endian == 'little': swapendian = 1
    
    ncpb = 30 # size of written blocks
     
    #-- Definition of the Observation et Simulation vectors (fake ones)
    obs = np.zeros(Data.nobs, np.float64)
    sim = np.zeros(Data.nobs, np.float64)             
    i0 = 0

    for isite in range(Site.npts):
        for name in Data.obsname_opti[isite]:
            nts = len(Data.obs[isite][name].ravel())
            obs[i0:i0+nts] = Data.obs[isite][name].ravel()
            sim[i0:i0+nts] = Data.sim[isite][name].ravel()
            i0 = i0+nts


    #-- Writting
    f = open( os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['input_file_bin']) ,'wb')

    # number of optimized parameters + total number of observations + size of written blocks ncpb = 30
    io.var_writefor(f, swapendian, np.array((Opti.n, Data.nobs, ncpb), np.int32))
    
    io.var_writefor(f, swapendian, Opti.xprior['all'])            # prior parameter vector
    io.var_writefor(f, swapendian, Opti.x['all'])                 # estimated parameter vector
    io.var_writefor(f, swapendian, np.sqrt(Opti.B['all']))         # diagonal (standard deviation) of the prior covariance error matrix on parameters   
    io.var_writefor(f, swapendian, obs)                           # observation vector
    io.var_writefor(f, swapendian, np.sqrt(Data.R['all']))         # diagonal (standard deviation) of the prior covariance error matrix on observations
    io.var_writefor(f, swapendian, sim)                           # simulation vector

    # Jacobian matrix of the model
    for i in range(0, Opti.n, ncpb):
        io.var_writefor(f, swapendian, Data.Jacobian[i:i+min([ncpb,Opti.n-i]),:])
        ###buf = Data.Jacobian[i:i+min([ncpb,Opti.n-i])][:]
        ###io.var_writefor(f, swapendian,buf)
        
   
    f.close()


    # ---------------------------------
    # --- CALL to tarantola_ref.f90 ---
    # ---------------------------------
    print Config.cmde_tarantola + ' < ' + os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['input_file_dat']) + \
              ' > ' + os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['log_file'])

    os.system(Config.cmde_tarantola +
              ' < ' +
              os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['input_file_dat']) + \
              ' > ' + os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['log_file']) )

    # --- Reading of the output binary file of tarantola_ref.f90 ---
    # - If file not present (meaning that TARANTOLA has crashed), continues with dummy values
    #f = open( os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['output_file_bin']) ,'rb')
    try:
        f = open( os.path.join(Config.PATH_MAIN_TMP,Config.TARANTOLA['output_file_bin']) ,'rb')
        # Estimated parameters
        xest = io.var_readfor(f, swapendian, np.zeros(Opti.n, np.float64) )
        test_tarantola = True 
    except:
        xest = np.ones((Opti.n)) * Config.missval[0]
        test_tarantola = False
        print
        print 'WARNING '*5
        print "'TARANTOLA.DETPOST_PARAS : Tarantola has crashed => no computation of Pb'"
        logfile.write('\n'+' WARNING'*5+'\n'+"'TARANTOLA.DETPOST_PARAS : Tarantola has crashed => no computation of Pb'\n")

    # -----------------------------------------------------------
    # --- Compute the set of optimized parameters iteratively ---
    # -----------------------------------------------------------
    if case == 'Opti_iter':
        
        # Modify the Opti structure
        ind = [-1]
        for name in opti_varname:
            n = Opti.xmask[name].count()
            if n>0:
                ind = np.arange(ind[len(ind)-1]+1, ind[len(ind)-1]+n+0.1)
                ind = ind.astype(np.int32).tolist()
                idxOK = np.ma.masked_array(range(len(Opti.xmask[name])),Opti.xmask[name].mask).compressed()
                np.put(Opti.x[name], idxOK, np.take(xest, ind) )
            else:
                Opti.x[name] = np.array(Config.missval[0], np.float64)

    
    # -------------------------------------------------------------
    # --- Compute the posterior covariance matrix on parameters ---
    # -------------------------------------------------------------

    if case == 'Bpost':

        if test_tarantola == True:
        
            # Diagonal elements of B (variances)
            Bdiag = io.var_readfor(f, swapendian, np.zeros(Opti.n, np.float64) )
            
            # Full B matrix (covariances)
            Bfull = np.zeros((Opti.n, Opti.n), np.float64)
            
            lectpar = np.zeros((ncpb,Opti.n), np.float64)
            for i in range(0,Opti.n,ncpb):
                if (Opti.n-i < ncpb):
                    lectpar = np.zeros((Opti.n-i,Opti.n), np.float64)
                    lectpar = io.var_readfor(f, swapendian, lectpar)
                    Bfull[i:Opti.n,:] = lectpar
                else:
                    lectpar = io.var_readfor(f, swapendian, lectpar)
                    Bfull[i:i+ncpb,:] = lectpar
                    
            f.close()

        else:
            # Diagonal elements of B (variances)
            Bdiag = np.ones((Opti.n)) * Config.missval[0]
            # Full B matrix (covariances)
            Bfull = np.ones((Opti.n, Opti.n)) * Config.missval[0]
            
        # --- Write the Covariance Matrix in a txt file ---
        fdata = '%10.10f'
        format_data = fdata
        for i in range(Opti.n-1):
            format_data = format_data + ','+ fdata 
        format_data = '%11s  |  ' + format_data + '\n'
        
        f = open(file_matcov_out,'w')
        
        print
    
        for ip in range(Opti.n):
            buf = [Opti.xname[ip]]+ Bfull[ip,:].tolist()
            f.write(format_data % tuple(buf) )
        
        f.close()
        

        # --- Calcul a la main ---
        # #import LinearAlgebra as LA
        # #iR = np.zeros((Data.nobs,Data.nobs), np.float64)
        # #for i in range(Data.nobs):
        # #    iR[i][i] =  1./Data.R['all'][i]
        # #
        # #iB = np.zeros((Opti.n, Opti.n), np.float64)
        # #for i in range(Opti.n):
        # #    iB[i][i] = 1./Opti.B['all'][i]
        # #
        # #A = np.matrixmultiply(Data.Jacobian,iR)
        # #C = np.matrixmultiply(A,np.transpose(Data.Jacobian)) + iB
        # #Bp = LA.inverse( C )
        # #
        # #fdata = '%10.10f'
        # #format_data = fdata
        # #for i in range(Opti.n-1):
        # #    format_data = format_data + ','+ fdata 
        # #format_data = '%11s  |  ' + format_data + '\n'
        # #
        # #f = open( os.path.join(Config.PATH_EXEC,'opti_erpost_matcovparas2.txt'),'w')
        # #
        # #for ip in range(Opti.n):
        # #    buf = [Opti.xname[ip]]+ Bp[ip,:].tolist()
        # #    f.write(format_data % tuple(buf) )
        # #    
        # #f.close()
        # -------------------------------------------------
    
        

        # --- Save the results in the class Opti ---
        # full Bpost matrix
        Opti.Bpost = Bfull[:]

#        print 'DEBUG / Bpost', Opti.Bpost
        
        # diagonal elements to be save in opti.res.nc
        icnt = 0
        for name in Opti.name:
            for i in range(Opti.xmask[name].count()):
            #for i in range(len(Opti.xmask[name])):
                #if Opti.xmask[name].mask[i]==True:
                #    Opti.Bpost_diag[name][i] = Config.missval[0]
                #else:
                Opti.Bpost_diag[name][i] = Bdiag[icnt]
                icnt+=1


#        print 'DEBUG / Bpost_diag', Opti.Bpost_diag
        
        # --- Write the Correlation Matrix in a txt file ---
        fdata = '%10.10f'
        format_data = fdata
        for i in range(Opti.n-1):
            format_data = format_data + ','+ fdata 
        format_data = '%11s  |  ' + format_data + '\n'

        f = open(file_matcor_out,'w')

        # computation
        if test_tarantola == True:
            MatCor = np.zeros((Opti.n, Opti.n), np.float64)
            for i in range(Opti.n):
                for j in range(Opti.n):
                    MatCor[i][j] = Bfull[i][j]/( np.sqrt(Bdiag[i])*np.sqrt(Bdiag[j]) )
                    MatCor[j][i] = MatCor[i][j]
        else:
            MatCor = np.ones((Opti.n, Opti.n))*Config.missval[0]
            
        # writing
        for ip in range(Opti.n):
            buf = [Opti.xname[ip]]+ MatCor[ip,:].tolist()
            f.write(format_data % tuple(buf) )
        
        f.close()

        # Compute Bpost site by site
        for isite in range(Site.npts):
            i=0
            for k in Opti.indsite[isite]:
                j=0
                for l in Opti.indsite[isite]:
                    Opti.Bpost_site[isite][i][j] = Opti.Bpost[k][l]
                    j=j+1
                i=i+1
        
    return test_tarantola
# END detpost_paras
# ==============================================================================



# ==============================================================================
# Determine the posterior uncertainties on observations
#
# The algorithm compute the posterior covariance matrix on observation data
# according to Tarantola (eq 4.51) :
#
# The posterior covariance matrix on data is defined as R' = [G * B' * Gt]
# with B' : the posterior covariance matrix on the parameters
#      R' : the posterior covariance matrix on observations
#      G  : the jacobian matrix of the model at the solution
# 
# ------------------------------------------------------------------------------

def detpost_Robs(Data, Opti, logfile, test_tarantola):
    

    print
    print '# Calculation of posterior covariance  matrix on observations...'
    logfile.write('\n # Calculation of posterior covariance matrix on observations...\n')

    
    #-DEBUG : test if the Jacobian contains NaN elements
    buf = np.ma.masked_values(Data.Jacobian, Config.missval[0])
    buf = np.ma.masked_values(buf, Config.missval[1])

    
    if buf.mask.all() != False: 
        
        print '---------'*15
        print 'WARNING '*15
        print 'WARNING '*15
        print 'TARANTOLA : Presence de valeurs NaN dans le Jacobien pour le calcul de la matrice de covariance d''erreur a posteriori sur les obs'
        print "            total number of elements ",len(Data.Jacobian.ravel())
        print "            total number of unmasked elements ",buf.count()
        print "            total number of masked elements ",len(Data.Jacobian.ravel())-buf.count()
        print 'WARNING '*15
        print 'WARNING '*15
        print '---------'*15

        
        logfile.write('\n'+'---------'*15)
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'TARANTOLA : Presence de valeurs NaN dans le Jacobien pour le calcul de la matrice de covariance d''erreur a posteriori sur les obs')
        logfile.write('\n                total number of elements' +str(len(Data.Jacobian.ravel())))
        logfile.write('\n                total number of unmasked elements '+str(buf.count()))
        logfile.write('\n                total number of masked elements '+str(len(Data.Jacobian.ravel())-buf.count()))
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'WARNING '*15)
        logfile.write('\n'+'---------'*15+'\n')
    #    
    #-

    # -------------------
    # --- Computation ---
    # -------------------                
    if test_tarantola == True:
        ## buf   = np.matrixmultiply(np.transpose(Data.Jacobian), Opti.Bpost)
        ## Rpost = np.matrixmultiply(buf, Data.Jacobian)
        buf   = np.dot(np.transpose(Data.Jacobian), Opti.Bpost)
        Opti.Rpost = np.dot(buf, Data.Jacobian)
    else:
        Opti.Rpost = np.ones((Data.nobs, Data.nobs))*Config.missval[0]

    
    # ------------------------------------------
    # --- Save the results in the class Opti ---
    # ------------------------------------------
    # full Rpost matrix
    #Opti.Rpost = Rpost[:]
    
##    # -------------------------------------------------
##    # --- Write the Covariance Matrix in a txt file ---
##    # -------------------------------------------------
##     fdata = '%10.10f'
##     format_data = fdata
##     for i in range(Opti.n-1):
##         format_data = format_data + ','+ fdata 
##         format_data = '%11s  |  ' + format_data + '\n'

##     f = open(file_matcov_out,'w')   
            
##     # writing
##     for ip in range(Data.nobs):
##         buf = [Data.obsname[ip]]+ Opti.Rpost[ip,:].tolist()
##         f.write(format_data % tuple(buf) )
        
##     f.close()

    
##     # -------------------------------------------------
##     # --- Write the Correlation Matrix in a txt file ---
##     # -------------------------------------------------
##     fdata = '%10.10f'
##     format_data = fdata
##     for i in range(Opti.n-1):
##         format_data = format_data + ','+ fdata 
##     format_data = '%11s  |  ' + format_data + '\n'

##     f = open(file_matcor_out,'w')
    
##     MatCor = np.zeros((Opti.n, Opti.n), np.float64)

##     # computation
##     for i in range(Opti.n):
##         for j in range(Opti.n):
##             MatCor[i][j] = Rfull[i][j]/( np.sqrt(Rdiag[i])*np.sqrt(Rdiag[j]) )
##             MatCor[j][i] = MatCor[i][j]
            
##     # writing
##     for ip in range(Opti.n):
##         buf = [Opti.xname[ip]]+ MatCor[ip,:].tolist()
##         f.write(format_data % tuple(buf) )
        
##     f.close()

             
    # --- Free some memory...
    del(buf)
     

# END detpost_obs
# ==============================================================================


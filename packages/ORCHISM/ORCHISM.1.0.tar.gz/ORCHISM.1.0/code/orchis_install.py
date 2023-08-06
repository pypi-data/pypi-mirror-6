#!/usr/bin/env python
#*******************************************************************************
# MODULE	: ORCHIS_INSTALL
# AUTHORS	: C. BACOUR & S. KUPPEL
# CREATION	: 02/2008
# LAST MODIF    : 02/2012
# COMPILER	: PYTHON
# 
"""
Creates the symbolic links for ORCHIS in the current directory
"""
#
# ------------------------------------------------------------------------------
# This source code is governed by the CeCILL licence
#
#*******************************************************************************

import os, glob

#PATH_ORCHIS = '/home/users/cbacour/LIB/PYTHON/ORCHIS'
PATH_ORCHIS = os.path.abspath(__file__)
PATH_ORCHIS = os.path.split(PATH_ORCHIS)[0]

PATH_CURRENT = os.getcwd()

# pys_orchis
file = 'orchis.py'
if len(glob.glob(file)) !=0: os.system('rm '+file)
os.symlink(os.path.join(PATH_ORCHIS,'orchis.py'),file)

# liens symboliques
files = os.listdir(PATH_ORCHIS)
fileLN = []
for file in files:
    file = file.lower()
    if len(file) >= 8:
        if file[0:8] == 'orchidee' or file[0:8] == 'tarantol':
            fileLN.append(file)


for file in fileLN:
    print file
    if len(glob.glob(file)) !=0: os.system('rm '+file)
    os.symlink(os.path.join(PATH_ORCHIS,file),file)

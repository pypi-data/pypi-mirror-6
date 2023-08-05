#§/usr/bin/env sh
# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
export PYTHONPATH=${C3POPALMINSTALL}/lib/python2.7/site-packages
mpirun -up 4 -np 1 palm_main

# --- last line


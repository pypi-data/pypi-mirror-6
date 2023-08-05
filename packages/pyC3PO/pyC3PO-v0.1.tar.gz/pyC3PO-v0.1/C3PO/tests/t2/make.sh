#§/usr/bin/env sh
# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
export PREPALMMPDIR
PREPALMMPDIR=${C3POPREPALMINSTALL}

function prepalm {
${PREPALMMPDIR}/prepalm_MP.tcl $* 
}

prepalm --c test_capsule.ppl
make

# --- last line


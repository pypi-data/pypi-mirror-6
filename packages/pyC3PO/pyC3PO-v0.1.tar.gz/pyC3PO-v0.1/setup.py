# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
from setuptools import setup
from distutils.core import Extension
import sys


try:
    import palm
except ImportError:
    pass

# export C3POPALMINSTALL
# export C3POPALMINSTALL_MPI1
# export C3POPREPALMINSTALL
#
# C3POPALMINSTALL=/tmp_user/tiamat/poinot/COSMOS+/I2
# C3POPALMINSTALL_MPI1=/tmp_user/tiamat/poinot/COSMOS+/I1
# C3POPREPALMINSTALL=/tmp_user/tiamat/poinot/COSMOS+/PrePALM_MP
#
# python setup.py install --prefix=${C3POPALMINSTALL}
# (cd build/lib/C3PO/tests/t1; chmod 777 make.sh test.sh; make.sh; test.sh)
# (cd build/lib/C3PO/tests/t2; chmod 777 make.sh test.sh; make.sh; test.sh)
# ...
# python setup.py install --prefix=${C3POPALMINSTALL_MPI1}
# (cd build/lib/C3PO/tests/t6; chmod 777 make.sh test.sh; make.sh; test.sh)

# -------------------------------------------------------------------------
setup (
name         = "C3PO",
version      = '0.1',
description  = "Coupling Capsule using CGNS/Python for OpenPalm",
author       = "marc Poinot",
author_email = "marc.poinot@onera.fr",
license      = "LGPL 2",
packages     = ['C3PO'],
package_data = {'C3PO': \
                ['tests/t%d/*'%n for n in xrange(1,7)] +\
                ['tests/e%d/*'%n for n in xrange(1,2)] 
                },
)

# --- last line

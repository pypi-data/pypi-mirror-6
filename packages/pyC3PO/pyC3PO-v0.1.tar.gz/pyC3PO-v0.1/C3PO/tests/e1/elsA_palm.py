#PALM_UNIT   -name elsA_palm\
#            -functions {python elsA_palm}\
#            -parallel mpi\
#            -minproc 1\
#            -maxproc 100000\
#            -comment {Capsule CGNS/Python}
#
#PALM_SPACE -name CGNSPYTHON\
#           -shape (:)\
#           -element_size PL_CHARACTER\
#           -comment {CGNS/Python sub-tree serialization}
#
#PALM_SPACE -name double_array\
#           -shape (:)\
#           -element_size PL_DOUBLE_PRECISION\
#           -comment {CGNS/Python double array}
#
#PALM_OBJECT -name Tnode\
#            -space CGNSPYTHON\
#            -intent OUT\
#            -comment {CGNS/Python node data out}
#
#PALM_OBJECT -name SYNC\
#            -space one_integer\
#            -intent OUT\
#            -comment {CGNS/Python sync integer out}
#
#PALM_OBJECT -name Dtable\
#            -space double_array\
#            -intent OUT\
#            -comment {CGNS/Python double array out}
#
#

# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import sys
import numpy
import palm
from   mpi4py    import MPI
from   elsA.CGNS import core
import CGNS.MAP
from elsA_user import *
sys.path.append('/home/poinot/Tools/Dist/lib/py/elsA/Compat')
import elsAxdt  as E
import time

T=CGNS.MAP.load('SquaredNozzle-08-R_Inj1.hdf')

file_out='SquaredNozzle-result.hdf'
baseName='SquaredNozzle'
surfaceName='INJ1'
count=0

# start OpenPalm
palm.init('NONE')
local_communicator=MPI.Comm()
palm.get_mycomm(local_communicator)

# elsA interface initialized
sys.argv=['elsA_palm.py','-C','BndSubInj',
          '-P','elsA_exchange_script.py','-X','16',
          '--','elsA_main_script.py']
__e=core.elsA()
__e.initialize(sys.argv,local_communicator)
__e.parse(T)
__e.compute()
#__e.finalize()

# --- last line


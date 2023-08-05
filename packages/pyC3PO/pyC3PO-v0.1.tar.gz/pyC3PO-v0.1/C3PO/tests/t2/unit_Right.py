#PALM_UNIT   -name unit_Right\
#            -functions {python unit_Right}\
#            -parallel mpi\
#            -minproc 1\
#            -maxproc 100000\
#            -comment {Capsule CGNS/Python}
#
#PALM_OBJECT -name Inode\
#            -space one_integer\
#            -intent IN\
#            -comment {CGNS/Python single integer in}
#
import palm
from C3PO import capsule

palm.init('NONE')
palm.write('CAPSULE CGNS/Python')
v=capsule.nodeRetrieveAsInteger("Inode")
palm.write('niter is %f'%v)
palm.finalize()

# --- last line

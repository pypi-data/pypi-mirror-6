#PALM_UNIT   -name unit_Right\
#            -functions {python unit_Right}\
#            -parallel mpi\
#            -minproc 1\
#            -maxproc 100000\
#            -comment {Capsule CGNS/Python}
#
#PALM_OBJECT -name Inode\
#            -space NULL\
#            -intent IN\
#            -comment {CGNS/Python double array in}
#
#PALM_OBJECT -name SYNC\
#            -space one_integer\
#            -intent IN\
#            -comment {CGNS/Python double array out}
#
import palm
from C3PO import capsule

palm.init('NONE')
palm.write('CAPSULE CGNS/Python')
v=capsule.nodeRetrieveAsDoubleArray("Inode")
palm.write('CoordinateX are is %s'%v)
palm.finalize()

# --- last line

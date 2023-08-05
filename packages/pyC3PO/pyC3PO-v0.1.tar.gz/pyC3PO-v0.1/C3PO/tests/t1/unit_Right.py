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
#            -comment {CGNS/Python node data in}
#
import palm
from mpi4py import MPI
from C3PO import capsule

err = palm.init('NONE')
err = palm.write('CAPSULE CGNS/Python')

z=MPI.Comm()
palm.get_mycomm(z)
T=capsule.treeRetrieve("Inode")

err = palm.finalize()

#PALM_UNIT   -name unit_Left\
#            -functions {python unit_Left}\
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
#PALM_OBJECT -name Onode\
#            -space CGNSPYTHON\
#            -intent OUT\
#            -comment {CGNS/Python node data out}
#
import palm
from mpi4py import MPI
import T
from C3PO import capsule

err=palm.init('NONE')
err=palm.write('CAPSULE CGNS/Python')
z=MPI.Comm()
palm.get_mycomm(z) # to be used as elsA init input
capsule.treePublish("Onode","CGNSPYTHON.unit_Left",1,T.data)
err=palm.finalize()

# --- last line

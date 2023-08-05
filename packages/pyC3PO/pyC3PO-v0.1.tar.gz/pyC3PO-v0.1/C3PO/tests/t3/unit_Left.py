#PALM_UNIT   -name unit_Left\
#            -functions {python unit_Left}\
#            -parallel mpi\
#            -minproc 1\
#            -maxproc 100000\
#            -comment {Capsule CGNS/Python}
#
#PALM_OBJECT -name Onode\
#            -space one_double\
#            -intent OUT\
#            -comment {CGNS/Python single double out}
#
import palm
import T
from C3PO import capsule

palm.init('NONE')
palm.write('CAPSULE CGNS/Python')
path='/CGNSTree/Cylindre/ReferenceState/Reynolds'
capsule.nodePublishAsDouble("Onode",1,T.data,path)
palm.write('Publish %s'%path)
palm.finalize()

# --- last line


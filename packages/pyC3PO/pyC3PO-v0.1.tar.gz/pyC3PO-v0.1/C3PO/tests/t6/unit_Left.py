#PALM_UNIT   -name unit_Left\
#            -functions {python unit_Left}\
#            -parallel mpi\
#            -minproc 1\
#            -maxproc 100000\
#            -comment {Capsule CGNS/Python}
#
#PALM_SPACE -name double_array\
#           -shape (:)\
#           -element_size PL_DOUBLE_PRECISION\
#           -comment {CGNS/Python double array}
#
#PALM_OBJECT -name Onode\
#            -space double_array\
#            -intent OUT\
#            -comment {CGNS/Python double array out}
#
#PALM_OBJECT -name SYNC\
#            -space one_integer\
#            -intent OUT\
#            -comment {CGNS/Python sync integer out}
#
import palm
import T
from C3PO import capsule

palm.init('NONE')
palm.write('CAPSULE CGNS/Python')
path='/CGNSTree/Cylindre/cyl0/GridCoordinates/CoordinateX'
capsule.nodePublishAsDoubleArray("Onode",'double_array.unit_Left',1,T.data,path)
palm.write('Publish %s'%path)
palm.finalize()

# --- last line


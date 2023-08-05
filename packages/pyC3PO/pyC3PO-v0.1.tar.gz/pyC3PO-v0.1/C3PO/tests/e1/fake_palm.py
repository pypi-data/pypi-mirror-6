#PALM_UNIT   -name fake_palm\
#            -functions {python fake_palm}\
#            -parallel mpi\
#            -minproc 1\
#            -maxproc 100000\
#            -comment {Capsule CGNS/Python}
#
#PALM_OBJECT -name Dtable\
#            -space NULL\
#            -intent IN\
#            -comment {CGNS/Python double array in}
#
#PALM_OBJECT -name SYNC\
#            -space one_integer\
#            -intent IN\
#            -comment {CGNS/Python sync integer in}
#
#PALM_OBJECT -name Tnode\
#            -space NULL\
#            -intent IN\
#            -comment {CGNS/Python node data in}
#
import palm
import numpy 
import CGNS.MAP

T=CGNS.MAP.load('SquaredNozzle-08-R_Inj1.hdf')

baseName='SquaredNozzle'
surfaceName='INJ1'
count=0

palm.init('NONE')
local_communicator=MPI.Comm()
palm.get_mycomm(local_communicator)

local_data=numpy.ones((cpl.located,),dtype='d')*1.3
first_data=numpy.copy(local_data)
it=1

while (it<50):
  print "fake process: Couplage Stop iteration : %i" %it
  remote_data=cpl.publishAndRetrieve(local_data,iteration=it)
  local_data+=remote_data*.5
  if (not it%20):
    fwk.trace('fake total: %.3d=%e'%(it,local_data.sum()))
    local_delta=local_data-first_data
    fwk.attribute.local_delta=local_delta.max()
  it+=1
    
fwk.trace('leave fake')
del cpl

# --- last line

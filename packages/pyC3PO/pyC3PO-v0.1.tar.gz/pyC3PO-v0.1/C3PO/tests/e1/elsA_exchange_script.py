# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import sys

sys.path.append('/home/poinot/Tools/Dist/lib/py/elsA/Compat')

import elsAxdt as X
import numpy   as N
import copy    as C
from   math import *
from   C3PO import capsule

#############################################
def indg2D(i,j,Imax):
    """2D global indice located on nodes"""
    return i + ((j-1) * Imax)
#############################################

it     = X.iteration()
state  = X.state()
cname  = X.ccname()
(rank,size)=X.ranksize()

##for mpi : ######
if (rank == 0) :
    listZone=[1,2]
else :
    listZone=[3,4]
##################

if it>1:
    outputTree=C.deepcopy(X.get(X.OUTPUT_TREE))
else:
    outputTree=None

if (outputTree==[] or outputTree==None):
    outputTree= None ##[None,None,[],None]
elif(it>1) :
    dataNameList=['Pi','vx','vy','vz']
    ## Dictionary translating extracted variable with CGNS formulation ##
    parserDict={'Pi':'PressureStagnation','vx':'VelocityX','vy':'VelocityY','vz':'VelocityZ'}

    for iz in listZone:
        dataName='Pi'
        Path='/SquaredNozzle/Zone-%03i/ZoneBC/InflowSubsonic:West/BCDataSet/DirichletData/%s' %(iz,dataName)
        underTree=X.retrieve(Path,outputTree)
        NumArray=underTree[1]
        dim=NumArray.shape[0]
        ArraySend=N.ones([dim],'float')
        
        underTree[0]=parserDict[dataName]
        
        if (dataName == 'Pi') :
            for i in range(dim):
                ArraySend[i]=NumArray[i]+0.01
                
        if (iz==1):
          if (it>48):
              m=-1
          else:
              m=numpy.mean(ArraySend)
        
          capsule.nodePublishAsDoubleArray("Onode",'double_array.unit_Left',1,T.data,path)
          print "elsA process: Couplage Stop iteration : %i" %it
          local_data=numpy.ones((cpl.located,),dtype='d')*m
          remote_data=cpl.publishAndRetrieve(local_data,iteration=i)

        underTree[1]=ArraySend
        X.free(X.RUNTIME_TREE)
        X.free(X.OUTPUT_TREE)

    X.xdt(X.PYTHON,(X.RUNTIME_TREE,outputTree,1))    

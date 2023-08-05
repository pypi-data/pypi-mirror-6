# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
from elsA_user import *
import sys

sys.path.append('/home/poinot/Tools/Dist/lib/py/elsA/Compat')
import elsAxdt  as E
import time

elsAPB=cfdpb(name='elsAPB') ## For migration mode...

mytree=E.XdtCGNS("SquaredNozzle-08-R_Inj1.hdf")
mytree.action=E.TRANSLATE


(rank,size)=E.ranksize()
mytree.distribution={
    'SquaredNozzle/Zone-001':0,
    'SquaredNozzle/Zone-002':0,
    'SquaredNozzle/Zone-003':1,
    'SquaredNozzle/Zone-004':1,
    'SquaredNozzle/Zone-005':1,
    'SquaredNozzle/Zone-006':1,
    'SquaredNozzle/Zone-007':0,
    'SquaredNozzle/Zone-008':0
    }
mytree.compute()

##Migration mode##
R=sequence("blockName_%3d=mytree.e_getBlockInternalName('SquaredNozzle/Zone-%3d')", 1, 4)
R=sequence("blk_%3d=getBlock(blockName_%3d)", 1, 4)

#elsAPB.set('mpi_block2proc','procDict')

R=sequence("blk_%3d.show()", 1, 4)

## Extraction
R=sequence("ext_%3d=extractor(blockName_%3d,name='ext_%3d')", 1, 4)
R=sequence("ext_%3d.setDict({\
'var'        :'xyz conservative pgen',\
'file'       :'./Output/InletField_Inj1_blk%3d.tp',\
'format'     :'fmt_tp',\
'loc'        :'cellfict',\
'period'     : 50,\
'writingmode': 3,\
})", 1, 4)


elsAPB.compute()
elsAPB.extract() ##...ended migration mode

mytree.save("./Output/SquaredNozzle_OutMPI_#%03d.cgns" %rank)
#mytree.save("./Output/SquaredNozzle_CouplageNref.adf")



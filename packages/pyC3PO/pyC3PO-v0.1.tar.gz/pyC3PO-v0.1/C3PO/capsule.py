# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import CGNS.PAT.cgnskeywords  as CGK
import CGNS.PAT.cgnsutils     as CGU
import CGNS.PAT.cgnslib       as CGL

import pickle
import numpy
import palm

def syncEmit(localname):
  nd=numpy.ones((1,),dtype='i')*92322
  po=palm.PalmObject(object=localname,space='one_integer')
  po.put(nd)
  return nd[0]
  
def syncWait(localname):
  po=palm.PalmObject(object=localname,space='one_integer')
  po.object_get_spacename()
  po.space_get_rank()
  po.space_get_shape()
  dt=numpy.empty(po.shape,dtype='i')
  po.get(dt)
  return dt[0]

def nodePublish(localname,space,rank,tree,path):
  nd=CGU.getNodeByPath(tree,path)
  treePublish(localname,space,rank,nd)
  
def nodeRetrieve(localname):
  return treeRetrieve(localname)

def nodePublishAsInteger(localname,rank,tree,path):
  nd=CGU.getNodeByPath(tree,path)
  po=palm.PalmObject(object=localname,space='one_integer')
  po.put(nd[1])
  
def nodePublishAsDouble(localname,rank,tree,path):
  nd=CGU.getNodeByPath(tree,path)
  po=palm.PalmObject(object=localname,space='one_double')
  po.put(nd[1])
  
def nodePublishAsDoubleArray(localname,space,rank,tree,path):
  nd=CGU.getNodeByPath(tree,path)
  po=palm.PalmObject(object=localname,space=space)
  po.shape=[nd[1].size]
  po.space=space
  po.rank=rank
  po.space_set_shape()
  f=syncEmit('SYNC.unit_Left')
  dd=numpy.array(nd[1].ravel(),dtype='d')
  po.put(dd)
  
def nodeRetrieveAsInteger(localname,tree=None,path=None):
  po=palm.PalmObject(object=localname,space='one_integer')
  po.object_get_spacename()
  po.space_get_rank()
  po.space_get_shape()
  dt=numpy.empty(po.shape,dtype='i')
  po.get(dt)
  if ((tree is None) or (path is None)):
    return dt[0]
  else:
    nd=CGU.getNodeByPath(tree,path)
    nd[1]=dt
 
def nodeRetrieveAsDouble(localname,tree=None,path=None):
  po=palm.PalmObject(object=localname,space='one_double')
  po.object_get_spacename()
  po.space_get_rank()
  po.space_get_shape()
  dt=numpy.empty(po.shape,dtype='d')
  po.get(dt)
  if ((tree is None) or (path is None)):
    return dt[0]
  else:
    nd=CGU.getNodeByPath(tree,path)
    nd[1]=dt
    

def nodeRetrieveAsDoubleArray(localname):
  po=palm.PalmObject(object=localname,space='NULL')
  po.object_get_spacename()
  po.space_get_rank()
  f=syncWait('SYNC.unit_Right')
  po.space_get_shape()
  dt=numpy.empty(po.shape,dtype='d')
  po.get(dt)
  return dt

def treePublish(localname,space,rank,tree):
  po=palm.PalmObject(object=localname,space=space)
  st=pickle.dumps(tree)
  padding=(4-len(st)%4)
  dt=numpy.array(st+' '*padding)
  po.shape=[len(st)+padding]
  po.space=space
  po.rank=rank
  po.space_set_shape()
  po.put(dt)

def treeRetrieve(localname):
  po=palm.PalmObject(object=localname,space="NULL")
  po.object_get_spacename()
  po.space_get_rank()
  po.space_get_shape()
  dt=numpy.empty(po.shape,dtype='c')
  po.get(dt)
  st=pickle.loads(dt.tostring().rstrip())
  return st

# --- last line

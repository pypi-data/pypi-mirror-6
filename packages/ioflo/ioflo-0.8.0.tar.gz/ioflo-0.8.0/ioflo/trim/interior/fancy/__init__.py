""" fancy package

"""
#print "\nPackage at%s" % __path__[0]

__all__ = ['cloning', 'salting']

for m in __all__:
    exec "from . import %s" % m  #relative import

#used by CreateAllInstances                 
_InstanceModules = [cloning, salting]

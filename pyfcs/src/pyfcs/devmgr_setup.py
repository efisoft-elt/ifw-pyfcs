from . import devices # make sure it is imprted first 
from pyfcs.core.api import BaseDevMgrSetup, DevMgrFactories

## #
# All specific methods are generated automaticaly from device Setup classes 
# devtypes list can be specified to generate only functions of given devtypes 
#   by default all known devtype are taken 
class DevMgrSetup(BaseDevMgrSetup, DevMgrFactories, devtypes="all", generate_methods=True):
    ...

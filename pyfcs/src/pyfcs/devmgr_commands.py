from . import devices # make sure it is imprted first 
from pyfcs.core.api import BaseDevMgrCommands, DevMgrFactories
from .devmgr_setup import DevMgrSetup


## #
# All specific methods are generated automaticaly from device Setup classes 
# devtypes list can be specified to generate only functions of given devtypes 
#   by default all known devtype are taken (devtypes="all") 
#  e.g. FcsDevMgrCommands( BaseDevMgrCommands, devtypes=('lamp', 'actuator') )
class DevMgrCommands(BaseDevMgrCommands, DevMgrFactories, devtypes="all", generate_methods=True):
    """ A default DevMgrCommands class 

    It contains all method related to registered devices
    """
    Setup = DevMgrSetup



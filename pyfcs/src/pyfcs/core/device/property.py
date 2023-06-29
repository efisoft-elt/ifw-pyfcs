"""
@copyright EFISOFT 
"""
from __future__ import annotations

class DeviceProperty:
    """ A device property to be include in a DevMgrSetup or DevMgrCommands class definition 

    Exemple::
        
        from pyfcs import devices
        from pyfcs.core.api import BaseDevMgrSetup,  DeviceProperty 

        class Fcs1Setup(BaseDevMgrSetup, generate_methods=True):
            lamp1 = DeviceProperty('lamp')
            lamp2 = DeviceProperty('lamp') 

            motor1 = DeviceProperty('motor')

        fcs1 = Fcs1Setup.from_dummy()
        fcs1.lamp1.switch_on(40, 10)

    """
    def __init__(self, devtype: str, devname: str|None = None):
        self._devname = devname 
        self._devtype = devtype 
    
    @property
    def devname(self):
        return self._devname 
    @property 
    def devtype(self):
        return self._devtype 

    def copy(self):
        return self.__class__( self._devtype, self._devname)

    def __set_name__(self, owner, name):
        if self._devname is None:
            self._devname = name 
    
    def __get__(self, parent, owner):
        if parent is None:
            return self
        return parent._get_device( self._devname, self._devtype)


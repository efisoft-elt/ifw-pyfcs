from __future__ import annotations
from typing import Any
""" Base classes for a Custom Device """
from ModFcfif.Fcfif import DeviceUnion
from ModFcfif.Fcfif import CustomDevice

from pyfcs.core.api import BaseMalIf, BaseDeviceSetup

class CustomMalIf(
        BaseMalIf, 
        Device=CustomDevice, 
        getter=DeviceUnion.getCustom, 
        setter=DeviceUnion.setCustom
    ):

    def set_values(self, values:dict[str,Any])->None:
        self.device.setParameters( str(values) )
    
    def get_values(self)->None:
        sparams: str = self.device.getParameters().strip()
        if sparams:
            return eval(sparams)
        else:
            return {}


class BaseCustomDeviceSetup(BaseDeviceSetup):
    """ A basic DeviceSetup for a Custom Device """
    MalIf = CustomMalIf 



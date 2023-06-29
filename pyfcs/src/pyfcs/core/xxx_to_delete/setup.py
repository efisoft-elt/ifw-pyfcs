from __future__ import annotations

from .payload import PayloadHolder

from .setup_command import SetupCommandGroup

from .fcs_register import get_fcs_setup_factory

from .device.setup import BaseDeviceSetup
from .setup_buffer import BaseDevMgrSetup

class Setup:
    def __init__(self):
        self._buffer = []    
    
    def new_fcs(self, name: str)->BaseDevMgrSetup:
        factory = get_fcs_setup_factory(name) 
        return factory.create()

    def new_device(self, fcstype, devname, devtype: str| type[BaseDeviceSetup]):
        fcs = self.new_fcs( fcstype )
        device = fcs.new( devname, devtype)
        return device 
    
    def _add_one(self, obj: BaseDeviceSetup | BaseDevMgrSetup,  override: bool = False)-> BaseDeviceSetup | BaseDevMgrSetup:
        found = 0
        if override:
            if obj.id is not None:
                for i,item in enumerate(self._buffer):
                    if obj.id == item.id:
                        self._buffer[i] = obj 
                        foun+=1 
        
        if not found:
            self._buffer.append( obj )
        return found 
    
    def add(self, *objs: tuple[BaseDeviceSetup | BaseDevMgrSetup], override: bool = False):
        for obj in objs:
            self._add_one( obj, override=override)

    def create_setup_command(self, froze: bool = True):
        if froze: 
            payloads = [PayloadHolder(obj.interface, obj.get_payload()) for obj in self._buffer]
            return SetupCommandGroup( payloads )
        else:
            return SetupCommandGroup( self._buffer )

    def setup(self):
        return self.create_setup_command().exec()

    async def async_setup(self):
        return await self.create_setup_command().async_exec()


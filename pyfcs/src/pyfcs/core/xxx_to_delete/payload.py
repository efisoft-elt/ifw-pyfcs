from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from .setup_command import SetupCommand

from .parameter import ParamProperty
from .device.register import get_device_classes

from .define import ClientInterfacer

from ModFcfif.Fcfif import SetupElem
from ModFcfif.Fcfif import VectorfcfifSetupElem


class BasePayloadHolder:
    def get_buffer(self)->VectorfcfifSetupElem:
        raise NotImplementedError

    def setup(self):
        return SetupCommand(self.interface, self.get_buffer()).exec()

    async def async_setup(self):
        s = SetupCommand(self.interface, self.get_buffer())
        return await s.async_exec()


def create_element_buffer( interface, payload):
    id = payload['id']
    try:
        devtype, params_payload = next( payload['param'].items().__iter__() )
    except StopIteration:
        raise ValueError("payload has no parameters")
    
    cls = get_device_classes( devtype ).Setup 

    setup = cls(interface, id)
    setup.set( params_payload )
    return setup.get_element_buffer()


@dataclass
class DevicePayloadHolder(BasePayloadHolder):
    interface: ClientInterfacer
    payload: dict[str,Any]
    
    def get_element_buffer(self):
        return create_element_buffer(self.interface, self.payload) 

    def get_buffer(self)->VectorfcfifSetupElem:
        buffer= VectorfcfifSetupElem()
        buffer.append( self.get_element_buffer())
        return buffer

@dataclass
class PayloadHolder(BasePayloadHolder):    
    interface: ClientInterfacer
    payload: list[dict[str,Any]]
    
    def get_buffer(self):
        buffer = VectorfcfifSetupElem()

        for payload_element in self.payload:
            buffer.append(
                create_element_buffer( self.interface, payload_element)
            )
        return buffer

    

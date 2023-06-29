""" 
Define Assembly Setup, Command and AsyncCommand methods
Assembly mimics a single device in its payload setup but 
however handles the setup of several devices in ones

"""
from __future__ import annotations
from abc import abstractmethod
from functools import partial
from typing import Any, Iterator

from ifw.fcf.clib import log
from ModFcfif.Fcfif import VectorfcfifSetupElem

from pyfcs.core.define import  BufferGetter, ClientInterfacer,  DeviceClassGetter
from pyfcs.core.device import DeviceProperty, BaseDeviceSetup,  create_schema, register

from pyfcs.core.devmgr import BaseDevMgrSetup 


DeviceSetupMeta = type(BaseDeviceSetup)

def _collect_device_properties( bases, namespace):
    device_properties = set()
    for base in bases:
        try:
            device_properties.update( base.__device_properties__ )
        except AttributeError:
            pass 
    for key, obj in namespace.items():
        if isinstance(obj, DeviceProperty):
            device_properties.add(key)
    namespace['__device_properties__'] = device_properties 


def _collect_register( bases ):
    for sub in bases:
        try:
            return sub.__register__ 
        except AttributeError:
            pass             
    return register 

class AssemblySetupMeta(DeviceSetupMeta):
    def __new__(mcs, clsname, bases, namespace, register: DeviceClassGetter|None = None, **kwargs):  
        if register is None:
            register = _collect_register( bases ) 
        _collect_device_properties( bases, namespace)  
        
        namespace['__schema__'] = None # force None Will be build from get_schema 
        namespace['__register__']= register
        
        return super().__new__( mcs, clsname, bases, namespace, **kwargs)


class BaseAssemblySetup( metaclass=AssemblySetupMeta): # must follow SetupEntity and RegistrableSetup Protocol
    """ Assembly is a high level grouping of devices 

    It receive Payload with parameter in the assembly namespace parameter 
    and apply accordingly the actions to several devices. 
    
    For instance a filter name can be the input of an assembly while the output is 
    a setup of two filter wheel motors.

    One can add 'child' devices inside an assembly class with the DeviceProperty object.

    """
    devtype = None
    Setup = BaseDevMgrSetup 

    def __init__(self, interface: ClientInterfacer, id: str | None =None):
        self.interface = interface 
        self.id = id
        self._params_buffer = {} # contain buffer parameters
        self._device_cash = {} # to Store eventual SetupDevice instance (from DeviceProperties)

    @abstractmethod
    def apply(self, setup: BaseDevMgrSetup)->None:
        """ Apply the buffer into (newly made) setup buffer """
        raise NotImplementedError

    @classmethod
    def get_devtype(cls):
        return cls.devtype
        
    @classmethod
    def get_schema(cls)->dict[str,Any]:
        """ClassMethod:  Build the json schema definition for the class 
        
        Returns:
            schema_definition (dict): the schema definition of the class  
        """
        # store the schema in the class so it is built only ones 
        if cls.__schema__ is None:
            cls.__schema__ = create_schema(cls)
        return cls.__schema__ 
    
    def get_devnames(self)->list[str]:
        """ List the device name of this assembly 

        By default it is all class DeviceProperty
        """
        cls = self.__class__ 
        return [getattr(cls, p).devname for p in self.__device_properties__]

    def _get_device(self, devname, devtype: str):
        """ Private method to create a device from DeviceProperty """
        # ! This method is used by DeviceProperty  
        try: 
            # Try if it is in the cash 
            return self._device_cash[devname] 
        except KeyError:
            # create it and cash it 
            
            DeviceSetupClass = self.__register__.setup_class(devtype)
            self._device_cash[devname] = DeviceSetupClass(self.interface, devname) 
        return self._device_cash[devname]

    def clear(self):
        """ Clear the current buffer """
        self._params_buffer.clear()
            
    def _clear_callback(self, err=None):
        """ A clear callback for the command executor 
        Clear is executed only if no error 
        """
        if err is None:
            self.clear()
        else:
            log.info("setup command execution failed, buffer wasn't cleaned")
    
    def get_buffer(self) -> VectorfcfifSetupElem:
        """ Build and return the buffer 
        
        Return:
            buffer: VectorfcfifSetupElem ready to be sent by Mal client Setup method    
        """
        return self.get_setup().get_buffer()
        
    def get_setup(self)-> BufferGetter:
        setup = self.Setup(self.interface)
        self.apply( setup )
        return setup 

    def set(self, __payload_dict__={}, **payload):
        """ Set the parameters  payload add it to the assembly setup buffer  
        
        ..note::

            in the context of a full payload, parameter payload is, e.g : 
                [{'id':'mylamp', 'param':{'lamp': --> {} <-- This Guy }}]
        
        ..note::
            
            ``dev.set( payload)``
            Is strictely equivalent to 
            ``dev.set( **payload )``

        Raises:
            ValueError, TypeError: if the param payload is not valid 
        """
        payload = {**__payload_dict__, **payload}
        sd = self.__setup_definition__ 
        context_keys, validator = sd.find_payload_parser_method(payload) 
        
        if validator is None:
            for key, value in payload.items():
                # Use setattr: The value needs to be parsed  
                setattr(self, key, value)
        else: 
            # remove context parameter from the payload 
            for key in context_keys:
                payload.pop(key)
            # use partial in order to deal with positional argument 
            # expected that validator is applying the setup 
            partial(getattr(self, validator), **payload )()
    
    def load_buffer(self, element):
        raise NotImplementedError("Assembly has no default load_buffer method")

    # copy all necessary method from DeviceSetup 
    # because Assembly is kind of a mix between DeviceSetup and DevMgrSetup
    # it is safer to copy method instead of subclassing from DeviceSetup 
    # Maybe at one point a Base class for both can be made 
    is_action_set = BaseDeviceSetup.is_action_set
    is_setup_valid = BaseDeviceSetup.is_setup_valid 
    is_param_set  = BaseDeviceSetup.is_param_set 

    get_element_payload = BaseDeviceSetup.get_element_payload 
    get_parameter_payload = BaseDeviceSetup.get_parameter_payload
    get_payload = BaseDeviceSetup.get_payload 
    
    setup = BaseDeviceSetup.setup 
    create_setup_command = BaseDeviceSetup.create_setup_command
    async_setup = BaseDeviceSetup.async_setup
    __repr__ = BaseDeviceSetup.__repr__






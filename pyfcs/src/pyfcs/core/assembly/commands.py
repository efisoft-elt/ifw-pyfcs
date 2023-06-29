from __future__ import annotations
from typing import Any


from pyfcs.core.device import DeviceProperty,  BaseDeviceCommand, BaseDeviceAsyncCommand, DevicesAppCommands, DevicesAppAsyncCommands, register
from pyfcs.core.tools import StatusHandler, StatusWaiter 
from pyfcs.core.define import DeviceClassGetter, SetupEntity, ClientInterfacer
from pyfcs.core.devmgr import BaseDevMgrSetup

from .setup import BaseAssemblySetup , _collect_device_properties, _collect_register


DeviceCommandMeta = type(BaseDeviceCommand)
DeviceAsyncCommandMeta = type(BaseDeviceAsyncCommand)

def _add_setup_device_properties(Setup: BaseAssemblySetup, namespace: dict)->None:
    for attr in dir(Setup):
        try:
            obj = getattr(Setup, attr)
        except AttributeError:
            pass 
        if isinstance( obj, DeviceProperty):
            namespace.setdefault( attr, obj.copy())

def _collect_status(bases:tuple[type], namespace:dict[str,Any], default=BaseDevMgrSetup)->type[BaseDevMgrSetup]:
    try:
        return namespace['Status']
    except KeyError:
        pass 

    for sub in bases:
        try:
            return sub.Status 
        except AttributeError:
            pass 
    return default


class AssemblyCommandMeta(DeviceCommandMeta):
    def __new__(mcs, clsname, bases, namespace, generate_methods=True, register: DeviceClassGetter|None = None): 
        
        if register is None:
            register = _collect_register( bases ) 
        
        Status = _collect_status(bases, namespace, BaseAssemblySetup)
        _add_setup_device_properties( Status, namespace)
        _collect_device_properties( bases, namespace) 
        
        namespace['__register__']= register

        return super().__new__(
                        mcs, clsname, bases, namespace,
                        generate_methods=generate_methods
                    )

class BaseAssemblyCommand(DevicesAppCommands, metaclass=AssemblyCommandMeta, generate_methods=False):
    Setup: SetupEntity = BaseAssemblySetup
    
    def __init__(self, interface: ClientInterfacer, id: str|None=None):
        self.interface = interface 
        self.id = id
    
    def _get_device(self, devname, devtype: str):
        # needed by DeviceProperty  
        DeviceCommandClass = self.__register__.command_class(devtype)
        return  DeviceCommandClass(self.interface, devname) 
    
    def _get_devnames(self)->list[str]:
        """ Return a list of device names for this assembly """
        # needed for all commands in DevicesAppCommands
        cls = self.__class__ 
        return [getattr(cls, p).devname for p in self.__device_properties__]
           
    def new_setup(self)->Setup:
        """ Return a new setup buffer for this assembly """
        return self.Setup(self.interface, self.id)
    
    def devstatus_handler(self)->StatusHandler:
        """ Executes a DevStatus Command on device assembly 

        Wrap result in a handy object
        
        Result is returned in a StatusHandler object which is used to 
        manipulate the returned status payload.
        """ 
        return StatusHandler( self.devstatus() )
        
    def wait( self, key:str, value:Any,  **kwargs):
        """ Wait for a given status rule to be true on these assembly devices 

        Args: 
            key (str): status key suffix, e.g.: 'lcs.substate' 
            value (Any): if a callable must be of signature f(data)
                where data is the retrieved status data.
                Otherwise value are compared with `==` 
                    
        Kwargs (same as StatusWaiter):
            timeout (int): timeout in ms after which a RuntimeError is raised 
            period  (int): the cycle period in ms to retrieve hardware status (default is 500)
            operator (Callable): Operator to treat several values of several devices into one 
                boolean var. Default is the function ``all``

        """
        waiter =  StatusWaiter(self.interface,  key, value, **kwargs)
        return waiter.wait( *self._get_devnames() )


class AssemblyAsyncCommandMeta(DeviceAsyncCommandMeta):
    def __new__(mcs, clsname, bases, namespace, generate_methods=True, register: DeviceClassGetter|None = None,): 
        
        if register is None:
            register = _collect_register( bases ) 

        Status = _collect_status(bases, namespace, BaseAssemblySetup)
        _add_setup_device_properties( Status, namespace)
        _collect_device_properties( bases, namespace) 

        namespace['__register__']= register
  
        return super().__new__(
                        mcs, clsname, bases, namespace,
                        generate_methods=generate_methods
                    )


class BaseAssemblyAsyncCommand(DevicesAppAsyncCommands, 
                              metaclass=AssemblyAsyncCommandMeta,
                              generate_methods=False
                            ):
    Setup = BaseAssemblySetup 

    def __init__(self, interface: ClientInterfacer, id: str|None=None):
        self.interface = interface 
        self.id = id
    
    def _get_device(self, devname, devtype: str):
        # function required by DeviceProperty 
        DeviceAsyncCommandClass = self.__register__.async_command_class(devtype)
        return  DeviceAsyncCommandClass(self.interface, devname) 

    def _get_devnames(self)->list[str]:
        """ Return a list of device names for this assembly """
        # needed for all commands in DevicesAppCommands
        cls = self.__class__ 
        return [getattr(cls, p).devname for p in self.__device_properties__]


    async def new_setup(self)->Setup:
        """ Async Return a new setup buffer for this assembly """
        return self.Setup(self.interface, self.id)
    
   
    async def devstatus_handler(self)->StatusHandler:
        """ Async Executes a DevStatus Command on assembly devices

        Wrap result in a handy object
        
        Result is returned in a StatusHandler object which is used to 
        manipulate the returned status payload.
        """ 
        return StatusHandler(await self.devstatus() )

    async def wait(self, key:str, value:Any,  **kwargs):
        """ Async Wait for a given status rule to be true on these assembly devices 

        Args: 
            key (str): status key suffix, e.g.: 'lcs.substate' 
            value (Any): if a callable must be of signature f(data)
                where data is the retrieved status data.
                Otherwise value are compared with `==` 
                    
        Kwargs (same as StatusWaiter):
            timeout (int): timeout in ms after which a RuntimeError is raised 
            period  (int): the cycle period in ms to retrieve hardware status (default is 500)
            operator (Callable): Operator to treat several values of several devices into one 
                boolean var. Default is the function ``all``

        """
        waiter =  StatusWaiter(self.interface,  key, value, **kwargs)
        return await waiter.async_wait( self._get_devnames() )


def generate_command_class(Setup: type):
    """ private classmethod, use to generate a new Command class for this Assembly """
    return AssemblyCommandMeta(
            Setup.devtype.capitalize()+"Command",  
            (BaseAssemblyCommand,), {'Setup':Setup}, 
            generate_methods= True, 
            register = Setup.__register__
        )
# this is needed for the register 
BaseAssemblySetup.__generate_command_class__ = classmethod( generate_command_class ) 


def generate_async_command_class(Setup: type)->type:
    """ private classmethod, use to generate a new Async Command class for this Assembly """
    return AssemblyAsyncCommandMeta(
            Setup.devtype.capitalize()+"AsyncCommand",  
            (BaseAssemblyAsyncCommand,), {'Setup':Setup}, 
            generate_methods= True,
            register = Setup.__register__
        )
# this is needed for the register 
BaseAssemblySetup.__generate_async_command_class__ = classmethod(generate_async_command_class)



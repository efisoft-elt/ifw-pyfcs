from __future__ import annotations
from typing import Any


from pyfcs.core.define import ClientInterfacer
from pyfcs.core.tools import StatusHandler , StatusWaiter

from .setup import  BaseDeviceSetup
from .app_commands import DevicesAppCommands, DevicesAppAsyncCommands 
from .factories import DeviceFactoryMethods

class DeviceCommandMeta(type):
    def __new__(mcs, clsname, bases, namespace, generate_methods=True):  
        cls =  type.__new__( mcs, clsname, bases, namespace)
        if generate_methods: 
            from ..generator import AllDeviceCommandGenerator # nasty but to avoid cyclick import # populate all setup_methods inside the DeviceCommand class   
            AllDeviceCommandGenerator.static_populate(cls)
        return cls    


# WARNING keep generate_methods=False  for the base class 
class BaseDeviceCommand(DeviceFactoryMethods, DevicesAppCommands, metaclass=DeviceCommandMeta, generate_methods=False):
    Setup = BaseDeviceSetup # to be implemented in subclass  

    def __init__(self, interface: ClientInterfacer, device_id: str):
        self.interface = interface 
        self.id = device_id
    
    @classmethod
    def get_devtype(cls):
        return cls.Setup.get_devtype()
   
    def _get_devnames(self):
        # needed for DeviceAppCommands 
        return [self.id] 
    
    def new_setup(self)->Setup:
        """ Return a new setup buffer for this device """
        return self.Setup(self.interface, self.id)
    
    def devstatus_handler(self)->StatusHandler:
        """ Executes a DevStatus Command and wrap result in a handy object
        
        Result is returned in a StatusHandler object which is used to 
        manipulate the returned status payload.
        """ 
        return StatusHandler( self.devstatus() )
    
       
    def wait( self, key:str, value:Any,  **kwargs):
        """ Wait for a given status rule to be true on this devices 

        Args: 
            key (str): status key suffix, e.g.: 'lcs.substate' 
            value (Any): if a callable must be of signature f(data)
                where data is the retrieved status data.
                Otherwise value is compared with == to the targeted status 
                    
        Kwargs (same as StatusWaiter):
            timeout (int): timeout in ms after which a RuntimeError is raised 
            period  (int): the cycle period in ms to retrieve hardware status (default is 500)
            operator (Callable): Operator to treat several values of several devices into one 
                boolean var. Default is the function ``all``

        """

        waiter =  StatusWaiter(self.interface,  key, value, **kwargs)
        return waiter.wait( self.id )
    


class DeviceAsyncCommandMeta(type):
    def __new__(mcs, clsname, bases, namespace, generate_methods=True):  
        cls =  type.__new__( mcs, clsname, bases, namespace)
        if generate_methods: 
            from ..generator import AllDeviceAsyncCommandGenerator # nasty but to avoid cyclick import # populate all setup_methods inside the DeviceCommand class   
            AllDeviceAsyncCommandGenerator.static_populate(cls)
        return cls    

class BaseDeviceAsyncCommand(DeviceFactoryMethods, DevicesAppAsyncCommands,  metaclass=DeviceAsyncCommandMeta, generate_methods=False):
    Setup = BaseDeviceSetup # to be implemented in subclass  
    

    def __init__(self, interface: ClientInterfacer, device_id: str):
        self.interface = interface 
        self.id = device_id
    
    
    @classmethod
    def get_devtype(cls):
        return cls.Setup.get_devtype()
    
    def _get_devnames(self):
        # needed for DeviceAppCommands 
        return [self.id] 
    
    async def new_setup(self)->Setup:
        """ Return a new setup buffer for this device """
        return self.Setup(self.interface, self.id)
    
    async def devstatus_handler(self)->StatusHandler:
        """ Executes a DevStatus Command and wrap result in a handy object
        
        Result is returned in a StatusHandler object which is used to 
        manipulate the returned status payload.
        """ 
        return StatusHandler(await self.devstatus() )

    async def wait(self, key:str, value:Any,  **kwargs):
        """ Async Wait for a given status rule to be true on this devices 

        Args: 
            key (str): status key suffix, e.g.: 'lcs.substate' 
            value (Any): if a callable must be of signature f(data)
                where data is the retrieved status data.
                Otherwise value is compared with == to the targeted status 
                    
        Kwargs (same as StatusWaiter):
            timeout (int): timeout in ms after which a RuntimeError is raised 
            period  (int): the cycle period in ms to retrieve hardware status (default is 500)
            operator (Callable): Operator to treat several values of several devices into one 
                boolean var. Default is the function ``all``

        """
        waiter =  StatusWaiter(self.interface,  key, value, **kwargs)
        return await waiter.async_wait( self.id )
    
      
def generate_command_class(Setup: type)->type:
    """ classmethod, use to generate a new Command class for this device """
    return DeviceCommandMeta(
            Setup.devtype.capitalize()+"Command",  
            (BaseDeviceCommand,), {'Setup':Setup}, 
            generate_methods= True
        )
# needed for the register 
BaseDeviceSetup.__generate_command_class__ = classmethod( generate_command_class )

def generate_async_command_class(Setup: type)->type:
    return DeviceAsyncCommandMeta(
            Setup.devtype.capitalize()+"AsyncCommand",  
            (BaseDeviceAsyncCommand,), {'Setup':Setup}, 
            generate_methods= True
        )
BaseDeviceSetup.__generate_async_command_class__ = classmethod( generate_async_command_class )





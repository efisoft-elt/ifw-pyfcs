from __future__ import annotations
from enum import Enum
from typing import Any, Callable, Coroutine
from typing_extensions import Protocol, runtime_checkable
from elt.pymal.rr import ClientModule
from ModFcfif.Fcfif import VectorfcfifSetupElem, SetupElem



class ClientKind(str, Enum):
    """ Client Kind accepted by Interface """
    App = "App"
    Std = "Std"
    Daq = "Daq"


class ClientInterfacer(Protocol):
    """ Standard Protocol for a Interface object """
    # must have a timeout property (for error logs)  
    timeout: int 
    # must have an uri property 
    uri: str  
    
    def __hash__(self):
        """ interface object must be hashable because used as dictionary key """
    
    def get_mal(self, client_kind: str):
        """ Must implement a get_mal method """

    def get_client(self, client_kind: str, asynchronous: bool=False)->ClientModule.Client:
        """ Must implement a get_client method with args :
        
            - client_kind One off ClientKind enumerator ('App', 'Std', 'Daq')
            - asynchronous (bool): if true the client is asynchronous 

        Returns a Mal Client 
        """        
    
    def command(self, client_kind, method_name, callback=None)->CommandExecutor:
        """ Must have a command method with args 
            
            - client_kind One off ClientKind enumerator ('App', 'Std', 'Daq')
            - method_name (str) : name of the client Method (e.g 'Init') 
            - callback  (optional, callable):  A callback function with signature f(exc) where 
                    exc is None or a raise Exception during Command 

        Returns a Command object 
        """

        
@runtime_checkable
class ClientInterfaceCommander(Protocol):
     def command(self, client_kind, method_name, callback=None)->CommandExecutor:
        """ Most of application just needs the command methods """

@runtime_checkable
class CommandExecutor(Protocol):
    method: Callable  # Property returning the synchronous method 
    async_method:  Callable # Property returning the synchronous method 
    
    def exec(self, *arg, **kwargs):
        """ Must have a method to execute the command synchronously """
    def async_exec(self, *args, **kwargs):
        """ Must have a method to execute the command asynchronously """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __enter__(self)->Callable:
        """ Must have a context handler """
    def __exit__(self, *args):
        """ Must have a context handler """ 
    def __aenter__(self)->Coroutine:
        """ Must have an asynchronous context handler """
    def __aexit__(self, *args):
        """ Must have a context handler for async commands  """ 

@runtime_checkable
class SetupMember( CommandExecutor, Protocol):
    """ Protocol to group Setups """
    interface: ClientInterfacer

    def get_buffer(self)->VectorfcfifSetupElem:
        """ Must have a get_buffer method  it shall return a VectorfcfifSetupElem """
    

@runtime_checkable
class BufferGetter(Protocol):
    """ Object holding a a Mal buffer  ( VectorfcfifSetupElem )"""
    
    def get_buffer(self)->VectorfcfifSetupElem:
        """ Must have a get_buffer method  it shall return a VectorfcfifSetupElem """

@runtime_checkable
class SetupEntity(Protocol):
     
    def __init__(self, interface: ClientInterfacer, device_id: str):
        """ Must be iniitialised with interface and device name """
    
    @classmethod
    def get_devtype(cls)->str:
        """ Must have a class method to return a device type string  """

    @classmethod
    def get_schema(cls)->dict:
        """ Must have a class Method which return a Json schema for validation  """

    def set(self, **kwargs):
        """ Must define a set method to set the payload parameters """
    
    def get_buffer(self)->VectorfcfifSetupElem:
        """ Must have a get_buffer method return a Mal Vector Fcf If Setup Element """

    def get_payload(self)->list[dict[str,Any]]:
        """ Must have a get_payload method to retrive element payload in a list """
    
    def load_buffer( self, element: SetupElem):
        """ Must have a load_buffer method to load a Mal Element """

class RegistrableSetup(Protocol):
    """ What a Setup entity should have to be registered """

    @classmethod
    def get_devtype(cls)->str:
        """ Must have a class method to return a device type string  """
    # Two Internal method defined in base class 
    @classmethod
    def __generate_command_class__(cls):
        """ Used by the device register to generate command class """

    @classmethod
    def __generate_async_command_class__(cls):
        """ Used by the device register generate async command class """

@runtime_checkable
class CommandEntity(Protocol):
    """ A Command class (Device, Assembly) must define these functions """
    def __init__(self, interface:ClientInterfacer, device_id:str):
        """ __init__ must have these two arguments """

    def new_setup(self)->SetupEntity:
        """ A new_setup must return a new Setup object related to this entity (Device, Assembly, etc )"""

@runtime_checkable
class AsyncCommandEntity(Protocol):
    """ A Async Command class (Device, Assembly) must define these functions """
    
    def __init__(self, interface:ClientInterfacer, device_id:str):
        """ __init__ must have these two arguments """

    async def new_setup(self)->SetupEntity:
        """ A new_setup must return a new Setup object related to this entity (Device, Assembly, etc )
        This shall be an async method 
        """



class DeviceInterfacer(Protocol):
    """ Interface between Mal Device and parameter space (a map of param->value) """
    def create_device(self):
        """ Must be abble to create Mal Device

        e.g. self.interface.get_mal().createDataEntity( LampDevice )
        """
    
    def get_device(self):
        """ Must return a curent Mal Device instance 
        e.g. self.element.getDevice().getLamp()
        """

    def set_device(self, device):
        """ Must be abble to save an incoming Mal Device Instance inside its container 
        e.g. self.container.setDevice( device )
        """

    def set_id(self, id:str):
        """ must be abble to change element id """ 

    def get_id(self)->str:
        """ must be abble to return an element id """

    def set_values(self, values: dict):
        """ must be abble to receive a dictionary of values and set them to Mal Device Instance """
    
    def get_values(self)->dict:
        """ must ba abble to extract parameters values from the Mal Device Instance """

@runtime_checkable
class DeviceClassGetter(Protocol):
    """ an object that can get registered devices class from string devtype """
    
    def get_devtypes(self)->list[str]:
        """ must return a list of devtype string  """

    def setup_class(self, devtype:str)->type:
        """ Must return setup class """
    
    def command_class(self, devtype:str)->type:
        """ Must return device command class """
    
    def async_command_class(self, devtype:str)->type:
        """ Must return async device command class """



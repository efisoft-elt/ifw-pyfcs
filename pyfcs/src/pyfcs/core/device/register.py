"""
functions to register device setup class and device command classes 
"""
from __future__ import annotations
from dataclasses import dataclass, field
from re import S
from typing import Type
from pyfcs.core.define import AsyncCommandEntity, CommandEntity, SetupEntity, RegistrableSetup

@dataclass
class DeviceRegister:
    name: str 
    Setup: type[SetupEntity] 
    Command: type 
    AsyncCommand: type 
    assembly: bool = False 

_device_register_loockup = {}


def is_assembly(Setup):
    return hasattr(Setup, "apply") 

def new_device_register( 
        Setup: type[RegistrableSetup], 
        Command: type|None = None, 
        AsyncCommand: type|None = None
    )->DeviceRegister:
    """ Make a new Device register class 
    
    If Command and AsynCommand classes are not given they will be created from 
    the Setup class 

    Args:
        Setup (type): can be a BaseDeviceSetup or an BaseAssemblySetup class 
        Command (optional, type): Corresponding device command class. If None 
            a new one is built from the Setup class
        AsyncCommand (optional, type): Corresponding device async command class. If None 
            a new one is built from the Setup class
    
    Return:
        element_register (DeviceRegister)
    """
    # import inside function to avoid import cycle 
        
    if Command is None:
        Command = Setup.__generate_command_class__() 

    if AsyncCommand is None:
        AsyncCommand = Setup.__generate_async_command_class__() 

    return  DeviceRegister(
            Setup.get_devtype(), 
            Setup=Setup, 
            Command=Command, 
            AsyncCommand=AsyncCommand,
            assembly = is_assembly(Setup) 
            )

def register_device( 
        Setup: type[RegistrableSetup], 
        Command: type|None = None, 
        AsyncCommand: type|None = None,
        *, 
        __loockup__: dict|None = None
    )->type:
    """ Make a new Device register class and register it 
    
    If Command and AsynCommand classes are not given they will be created from 
    the Setup class 

    Args:
        Setup (type): can be a DeviceSetup or an BaseAssemblySetup class 
        Command (optional, type): Corresponding device command class. If None 
            a new one is built from the Setup class
        AsyncCommand (optional, type): Corresponding device async command class. If None 
            a new one is built from the Setup class
    
    Return:
        element_register (DeviceRegister) hold registered classes  
    """
    register = new_device_register(
            Setup=Setup, 
            Command=Command, 
            AsyncCommand=AsyncCommand
    )
    if __loockup__ is None:
        __loockup__ = _device_register_loockup 

    __loockup__[Setup.devtype.lower()] = register 
    return register 


def get_device_classes(devtype, *, __loockup__: dict|None = None):
    """ Return a Device class register for the given device type string 

    the device type is cas un-sensitive

    Args:
        devtype:  case insensitive device type

    Returns:
        cls : The maching DeviceRegister Class 
    
    Raises:
        ValueError: if no matching devtype has been registered

    Exemple::

        lamp_register = get_device_classes("lamp")
        LampSetup = lamp_register.Setup 
        LampCommand = lamp_register.Command 
        LampAsyncCommand = lamp_register.AsyncCommand 

    """
    if __loockup__ is None:
        __loockup__ = _device_register_loockup 

    try:
        return __loockup__[devtype.lower()]
    except KeyError:
        raise ValueError(f"device of type {devtype} is not registered. Available device types are {', '.join(_device_register_loockup)}")

    
def get_devtypes(exclude_assemblies: bool =False,* , __loockup__: dict|None = None)->list[str]:
    """ return in a list of string all available device types 

    Args:
        exclude_assemblies (Optional, bool): If True assemblies will not be included in the
            list. Default is False 
    """
    if __loockup__ is None:
        __loockup__ = _device_register_loockup 

    if exclude_assemblies:
        return [name for name,r in __loockup__.items() if not r.assembly]
    return list(__loockup__)

def setup_class( devtype: str | Type[SetupEntity], * , __loockup__: dict|None = None)->Type[SetupEntity]:
    """ parse input and return a Setup Class
    
    Args:
        devtype (str,SetupEntity): if string it must be point to a registered device. 
            If a SetupEntity class it is returned as it is.

    Raises:
        ValueError: If input is not valid or if the device name was not registered 

    """
    if isinstance(devtype, str):
        return  get_device_classes(devtype, __loockup__=__loockup__).Setup

    else:
        if isinstance(devtype, type):
            if issubclass(devtype, SetupEntity):
                return devtype 
        raise ValueError(f"expecting a str devtype or a class matching SetupEntity Protocol, got a {type(devtype)}")

def command_class(
      devtype: str | Type[CommandEntity], 
      * , __loockup__: dict|None = None
    )->Type[CommandEntity]:
    """ parse input and return a Command Class
    
    Args:
        devtype (str,CommandEntity): if string it must be point to a registered device. 
            If a CommandEntity class it is returned as it is.

    Raises:
        ValueError: If input is not valid or if the device name was not registered 

    """

    if isinstance(devtype, str):
        return  get_device_classes(devtype, __loockup__=__loockup__).Command
    else:
        if isinstance(devtype, type):
            if issubclass(devtype, CommandEntity):
                return devtype 
        raise ValueError(f"expecting a str devtype or a class matching CommandEntity Protocol, got a {type(devtype)}")

def async_command_class(
      devtype: str | Type[AsyncCommandEntity], 
      * , __loockup__: dict|None = None
    )->Type[AsyncCommandEntity]:
    """ parse input and return a AsyncCommand Class
    
    Args:
        devtype (str,AsyncCommandEntity): if string it must be point to a registered device. 
            If a AsyncCommandEntity class it is returned as it is.

    Raises:
        ValueError: If input is not valid or if the device name was not registered 

    """


    if isinstance(devtype, str):
        return  get_device_classes(devtype, __loockup__=__loockup__).AsyncCommand 
    else:
        if isinstance(devtype, type):
            if issubclass(devtype, AsyncCommandEntity):
                return devtype 
        raise ValueError(f"expecting a str devtype or a class matching AsyncCommandEntity Protocol, got a {type(devtype)}")


@dataclass
class Register:
    devtype_loockup: dict[str,DeviceRegister] = field( default_factory=dict )
    all: bool = True 

    def register_device(self, 
          Setup: type[RegistrableSetup], 
          Command: type|None = None, 
          AsyncCommand: type|None = None 
        )->type[DeviceRegister]:
        return register_device( Setup, Command, AsyncCommand, __loockup__=self.devtype_loockup)
   
    def get_devtypes(self, exclude_assemblies: bool =False):
        devtypes = set(get_devtypes(  exclude_assemblies, __loockup__=self.devtype_loockup  ))
        devtypes.update( get_devtypes(  exclude_assemblies) )
        return list(devtypes) 

    def get_device_classes(self, devtype):
        try: 

            return get_device_classes( devtype, __loockup__=  self.devtype_loockup )
        except ValueError as err:
            if self.all:
                return get_device_classes( devtype )
            raise err  
    
    def setup_class(self, devtype):
        try: 
            return setup_class( devtype, __loockup__=  self.devtype_loockup )
        except ValueError as err:
            if self.all:
                return setup_class(devtype )
            raise err  
    
    def command_class(self, devtype):
        try: 
            return command_class( devtype, __loockup__=  self.devtype_loockup )
        except ValueError as err:
            if self.all:
                return command_class(devtype )
            raise err  

    def async_command_class(self, devtype):
        try: 
            return async_command_class( devtype, __loockup__=  self.devtype_loockup )
        except ValueError as err:
            if self.all:
                return async_command_class(devtype)
            raise err  


   

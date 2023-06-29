""" Function to create Command classes from a set of devices and device types 

They can be used to fix the Command and setup client to what is defined inside a configuration file
"""
from __future__ import annotations
from pyfcs.core.device import register, DeviceProperty 
from pyfcs.core.tools import get_devtypes_from_cfgfile
from pyfcs.core.define import ClientInterfaceCommander, ClientInterfacer

from .setup import  BaseDevMgrSetup, DevMgrSetupMeta
from .commands import BaseDevMgrAsyncCommands, BaseDevMgrCommands, DevMgrAsyncCommandsMeta, DevMgrCommandsMeta
from .factories import DevMgrFactories 

def get_devtypes_from_interface(interface: ClientInterfaceCommander)->dict[str,str]:
    """ Return a dictionary of devname->devtype items from a client interface """
    with interface.command( 'App', 'DevInfo') as devinfo:
        return {devname:devtype.lower() for devname, devtype in eval( devinfo() ).items() }


def parse_device_map( obj ):
    """ parse  an object into a dictionary of devname->devtype 
    
    object can be :
        - a dictionary like object (parsed as it is)
        - a relative path to a FCS configuration file (nomad template should also works)
        - a client interface, a connection is needed to ask server configuration  
    """
    if isinstance(obj, str):
        obj = get_devtypes_from_cfgfile(obj)
    elif isinstance( obj, ClientInterfaceCommander):
        return get_devtypes_from_interface(obj) 
    return dict(obj) 



def create_setup_class(
        base_name: str, 
        device_map:dict[str,str]|str = {},
        devtypes: list[str]|None = None       
        )->type[BaseDevMgrSetup]:
    """ Create a new Setup Buffer Class
    
    The created class will include setup command only for device types defined in 
    the device_map argument 

    Args:
        base_name (str): Base name e.g. if 'Fcs1' The class will be named 'Fcs1Setup'
        device_map (dict, str or Interface): Either 
                    - A dictionary of device_name -> device_type  
                    - A string path pointing to a fcs yaml config file containing devices information 
                    - An interface object, in this case the server device configuration is asked 
        devtypes (optional, list, str): A list of additional devtypes accepted by this 
            client class. If not given or None (default), only the ones defined in device_map will
            be accepted and the pairs of devname->devtype is frozen on the classe. 
            Devtypes can also be "all" which include all registered device types.
    """
    device_map = parse_device_map(device_map)
    
    namespace = {devname: DeviceProperty(devtype) for devname, devtype in device_map.items() }


    alldevtypes = set(device_map.values())
    if devtypes:
        if devtypes in [all, 'all', 'All']:
            devtypes = register.get_devtypes()
        alldevtypes.update(devtypes)
    else:
        # fix the devicetypes map 
        namespace['_devtypes_map'] = device_map 

        
    return DevMgrSetupMeta(
            base_name+"Setup", (BaseDevMgrSetup, DevMgrFactories),
            namespace, 
            devtypes=alldevtypes, 
            generate_methods = True
        )


    
def create_command_class(
        base_name: str, 
        device_map:dict[str,str]|str|None = {}, 
        devtypes:list[str]|str|None = None 
        )->type[BaseDevMgrCommands]:
    """ Create a Device Manager client class  (Synchrnous)
    
    The DevMgrSetup class is also created and included inside command class

    Args:
        base_name (str): Base name e.g. if 'Fcs1' The classwill be named 'Fcs1Command'
        device_map (dict, str or Interface): Either 
                    - A dictionary of device_name -> device_type  
                    - A string path pointing to a fcs yaml config file containing devices information 
                    - An interface object, in this case the server device configuration is asked 
        devtypes (optional, list, str, None): A list of additional devtypes accepted by this 
            client class. If not given or None (default), only devices defined in device_map will
            be accepted and the pairs of devname->devtype is frozen in the class. 
            Devtypes can also be "all" which include all registered device
            types.

    
    Returns:
        Command : built Command class
    
    """

    device_map = parse_device_map(device_map)

    Setup = create_setup_class(base_name, device_map, devtypes)

    namespace = {devname: DeviceProperty(devtype.lower()) for devname, devtype in device_map.items() }
            
    namespace['Setup'] = Setup

    Command = DevMgrCommandsMeta(
            base_name+"Commands", (BaseDevMgrCommands, DevMgrFactories), 
            namespace, 
            devtypes=devtypes, 
            generate_methods = True
        )
    return Command 

def create_async_command_class(
        base_name: str, 
        device_map:dict[str,str]|str|None = {}, 
        devtypes:list[str]|str|None = None 
        )->type[BaseDevMgrCommands]:
    """ Create a Device Manager client class  (ASynchronous)
    
    The DevMgrSetup class is also created and included inside async command class

    Args:
        base_name (str): Base name e.g. if 'Fcs1' The classwill be named  'Fcs1AsyncCommand'
        device_map (dict, str or Interface): Either 
                    - A dictionary of device_name -> device_type  
                    - A string path pointing to a fcs yaml config file containing devices information 
                    - An interface object, in this case the server device configuration is asked 
        devtypes (optional, list, str, None): A list of additional devtypes accepted by this 
            client class. If not given or None (default), only devices defined in device_map will
            be accepted and the pair of devname->devtype will be frozen in the class. 
            Devtypes can also be "all" which include all registered device types.

    
    Returns:
        Command : built Command class
    
    """

    device_map = parse_device_map(device_map)

    Setup = create_setup_class(base_name, device_map, devtypes)

    namespace = {devname: DeviceProperty(devtype.lower()) for devname, devtype in device_map.items() }
            
    namespace['Setup'] = Setup
    AsyncCommand = DevMgrAsyncCommandsMeta(
            base_name+"AsyncCommands", (BaseDevMgrAsyncCommands,), 
            namespace, 
            devtypes=devtypes, 
            generate_methods = True
        )
    return AsyncCommand


def create_command_classes(
        base_name: str, 
        device_map:dict[str,str]|str|None = {}, 
        devtypes:list[str]|str|None = None 
    )->tuple[type[BaseDevMgrCommands],type[BaseDevMgrAsyncCommands]]:
    """ Create two Device Manager client classes (Synchrnous and Asynchronous)
    
    The DevMgrSetup class is also created and included inside both commands classes  

    Args:
        base_name (str): Base name e.g. if 'Fcs1' The classes will be named 'Fcs1Command', 'Fcs1AsyncCommand'
        device_map (dict, str or Interface): Either 
                    - A dictionary of device_name -> device_type  
                    - A string path pointing to a fcs yaml config file containing devices information 
                    - An interface object, in this case the server device configuration is asked 

        devtypes (optional, list, str, None): A list of additional devtypes accepted by this 
            client class. If not given or None (default), only devices defined in device_map will
            be accepted and the pair of devname->devtype will be frozen in the class. 
            Devtypes can also be "all" which include all registered device types.

    
    Returns:
        Command : built Command class
        AsyncCommand: built Asynchronous Command class 
    
    """
    device_map = parse_device_map(device_map)
    return (
            create_command_class( base_name, device_map, devtypes), 
            create_async_command_class( base_name, device_map, devtypes)
        )



def new_command(name: str, interface: ClientInterfacer, asyncronous: bool = False)-> BaseDevMgrCommands| BaseDevMgrAsyncCommands:
    """ Build an online DevMgr Command class and instanciate it 
    
    Args:
        name (str): A base name for the client (e.g. 'fcs1') 
        interface (ClientInterfacer):  Client interface used to :
                - 1/ ask server the available device and types to build the class 
                - 2/ instanciate the object
        asynchronous (bool, optional): If True return an AsynCommand class

    """
    class_name = name.capitalize()
    if asyncronous:
        Command = create_async_command_class( class_name, interface )
    else:
        Command = create_command_class( class_name, interface)
    return Command( interface)

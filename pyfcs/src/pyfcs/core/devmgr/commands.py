
from __future__ import annotations
import time
from typing import Any, Callable
import re

from ifw.fcf.clib import log 

from pyfcs.core.tools import class_help,  StatusWaiter , StatusHandler 
from pyfcs.core.device import DeviceProperty, BaseDeviceAsyncCommand, BaseDeviceCommand
from pyfcs.core.define import ClientInterfacer, CommandEntity, DeviceClassGetter
from pyfcs.core.generator import AllCommandMethodGenerator, AllAsyncCommandMethodGenerator
from pyfcs.core.interface import Interface

from .daq_commands import  DaqCommands, DaqAsyncCommands
from .std_commands import  StdCommands, StdAsyncCommands
from .app_commands import AppAsyncCommands, AppCommands
from .setup import  BaseDevMgrSetup, DevMgrSetupMeta, _collect_devtypes, _collect_register



def _match_devststus_pattern(pattern: str, reply: list[str])->str:
    """ parse a devstatus reply accordint to a pattern """
    # In original 
    if pattern is None:
        return "\n".join(reply)
    return "\n".join( item for item in reply if re.search(pattern, item) )


def _device_properties_copy( cls:type )->dict[str,DeviceProperty]:
    properties = {}
    for attr in dir(cls):
        try:
            obj = getattr(cls, attr)
        except AttributeError:
            pass 
        if isinstance( obj, DeviceProperty):
            properties[ attr ] = obj.copy() 
    return properties 


class DevMgrCommandsMeta(type):
    """ MetaClass for a DevMgrCommand class or subclass 

    The metaclass takes 2 keword argument:
        - devtypes (iterable|None|str):  
            - A list of string, devtype to be implemented in the class 
            - Or "all" (default) to implement all registered devices 
            - Or None: implement only devices defined by DeviceProperty objects in the class. If None it also froze the devname->devtype mapping of the instances. 
            
        - generate_methods (bool): If True (default) Generate all device command method

    """
    def __new__(mcs, clsname, bases, namespace, 
            devtypes:list[str]| str | None = 'all', 
            generate_methods: bool = True,
            register: DeviceClassGetter| None  = None  
        ): 
        if register is None:
            register = _collect_register(bases)
        

        _collect_devtypes(bases, devtypes, namespace, register)

        cls =  type.__new__( mcs, clsname, bases, namespace)
        cls.__register__ = register 

        if generate_methods:
            AllCommandMethodGenerator.static_populate(cls)
            if cls.Setup is BaseDevMgrSetup:
                device_properties = _device_properties_copy(cls) 
                cls.Setup = DevMgrSetupMeta(
                        'CmdDevMgrSetup', (BaseDevMgrSetup,), device_properties, 
                        devtypes=devtypes,  generate_methods = True
                    )
        return cls


class BaseDevMgrCommands(
        DaqCommands, StdCommands, AppCommands, 
        metaclass=DevMgrCommandsMeta, 
        devtypes=[], 
        generate_methods=False
    ):
    """ Dev Mgr Commands used to send command to an FCS Device Manager  

    Args:
        interface (ClientInterfacer, str): A Client Interface or a uri string 
            If this is a Client Interface the timeout argument should be None 
        timeout (int, optional): Used only if interface is a string otherwise this is ignored 
    """
    Setup = BaseDevMgrSetup 
    _devtypes_map = None 

    def __init__(self, interface: ClientInterfacer| str, timeout: int| None = None):
        if isinstance(interface, str):
            interface = Interface(interface, timeout) 
        elif timeout is not None:
            raise ValueError(f"Timeout argument is only valid when receiving an string uri got a {type(interface)}")
        
        self.interface = interface 
     
    def new_setup(self)->Setup:
        """ Return a new Setup Buffer for this Fcs """
        return self.Setup(self.interface)
    
    def _get_device(self, devname, devtype):
        # necessary because in interface with DeviceProperty (alway syncrhonous) 
        return self.new(devname, devtype)
  
    def new(self, devname:str, devtype: str | type[CommandEntity] |  None = None)->CommandEntity:
        """ Return A Device Command object for the given device 

        Args:
            devname (str): device name 
            devtype (str,optional): device devtype. If not given this will be taken from server 
                    devtype can however be usefull if working offline. 
        """
        if devtype is None:
            devtype = self.get_devtype(devname)
        DeviceCommandClass = self.__register__.command_class(devtype)
        return DeviceCommandClass(self.interface, devname) 

    
    def get(self, name,  devtype: str | type[CommandEntity] |  None = None)->CommandEntity:
        """ Return A Device Command object for the given device 
            
        This is an alias of the new method 

        Args:
            name (str): device name 
            devtype (str,optional): device devtype. If not given this will be taken from server 
                    devtype can however be usefull if working offline. 


        """
        return self.new(name, devtype)

    def get_devtypes(self)->dict[str,str]:
        """ Return a mapping of devname->devtypes for all devices managed by the server

        Returns:
            map (dict): dictionary of devname-> devtype 
        """
        if self._devtypes_map is None:
            devtypes = eval(self.devinfo()) 
            self._devtypes_map = {**devtypes, **self.__builtin_devtypes_map__}

        return self._devtypes_map

    def get_devtype(self, devname: str)-> str:
        """ Get the device type ot a given devname 

        Args:
            name (str): device name 

        Returns:
            devtype (str): device type 

        Raise:
            ValueError if the device is not found 
        """
        try:
            return self.get_devtypes()[devname] 
        except KeyError:
            raise ValueError(f"device name <{devname}> not managed by the server")
    
    def devstatus_handler(self, *devnames)->StatusHandler:
        """ Executes a DevStatus Command and wrap result in a handy object
        
        Result is returned in a StatusHandler object which is used to 
        manipulate the returned status payload. 

        Args:
            *devnames (variable list):  List of devices to inquire status.

        It no devices are provided, the status will include all devices.
        
        Example: 
            
            >>> from pyfcs.api import DevMgrCommands 
            >>> c = DevMgrCommands.from_consul( 'fcs2-req' ) 
            >>> status = c.devstatus_handler()

            >>> print( status.lamp1.lcs.intensity ) 
            0.0 

            # Returned a new StatusHandler with only keys matching 
            # the gieven suffix (which is removed from keys) 
            >>> substates = status.restricted('lcs.substate')
            >>> print( substates.lamp1 )  
            Off 
            
            >>> print( list( substates.values() ))
            ['Off', 'On', 'Standstill'] 
            >>> print( dict( substates.items() ))
            {'lamp1': 'Off', 'lamp2': 'On', 'motor1': 'Standstill'}
            
            # filter with a re pattern. Can be applied on keys or string values
            >>> dict( status.restricted('lcs.state').filtered('Op', True).items())
            {'lamp1': 'Operational', 'lamp2': 'Operational', 'motor1': 'Operational'}
        """
        return StatusHandler(self.devstatus(*devnames))  

    def devstatus_regex(self, pattern=None)->str:
        """ DevStatus Command and match output with a pattern

        Args:
            pattern (str): Pattern to match with regular expression


        The server will deliver the status for all devices.
        This method will filter the output according the pattern
        provided. 
        """
        with self.interface.command('App','DevStatus') as devstatus:
            return _match_devststus_pattern( pattern, devstatus([]) )

    def wait( self, key:str, value:Any, *devnames, **kwargs):
        """ Wait for a given status rule to be true on several devices 

        Args: 
            key (str): status key suffix, e.g.: 'lcs.substate' 
            value (Any): if a callable must be of signature f(data)
                where data is the retrieved status data.
                Otherwise value is compared with == to the targeted status 
            *devnames: list of device to check if not given all devices are used
        
        Kwargs (same as StatusWaiter):
            timeout (int): timeout in ms after which a RuntimeError is raised 
            period  (int): the cycle period in ms to retrieve hardware status (default is 500)
            operator (Callable): Operator to treat several values of several devices into one 
                boolean var. Default is the function ``all``

        Exemple::

            c = DevMgrCommand.from_consul('fcs2-req')
            
            # wait that lamp1 and lamp2 are on 
            c.wait( "lcs.substate", "On", "lamp1", "lamp2" )
            
            # wait that one of the lamp is turned Off 
            c.wait( "lcs.substate", "Off", "lamp1", "lamp2", operator=any )
            
            # wait that a motor position is above > 30.0 uu 
            c.wait( "pos_actual", lambda pos:pos>30.0, 'motor1')
            
            # note, this is equivalent of doing 
            c.get("motor1").wait( "pos_actual", lambda pos:pos>30.0 )
        
         
        """
        waiter =  StatusWaiter(self.interface,  key, value, **kwargs)
        return waiter.wait(*devnames )
    
    @classmethod
    def help(cls, func=None):
        """ Provides a text based help of the Command class functions.

        Args:
            func (str, optional): Name of the function from where to get the help

        This method is to be used for the implementation of CLIs.
        Functions are methods of the class.
        If the parameter <func> is not provided then the help provides a list of
        functions. Functions started with '_' are skipped.
        """
        return class_help(cls, func)


class DevMgrAsyncCommandsMeta(type):
    """ MetaClass for a DevMgrAsyncCommand class or subclass 

    The metaclass takes 2 keword argument:
        - devtypes (iterable|None|str):  
            - A list of string, devtype to be implemented in the class 
            - Or "all" (default) to implement all registered devices 
            - Or None: implement only devices defined by DeviceProperty objects in the class. If None it also froze the devname->devtype mapping of the instances. 
            
        - generate_methods (bool): If True (default) Generate all device command method
    """

    def __new__(mcs, clsname, bases, namespace, 
            devtypes:list[str]| str | None = 'all', 
            generate_methods: bool = True,
            register: DeviceClassGetter| None  = None  

        ): 
        if register is None:
            register = _collect_register(bases)

        _collect_devtypes(bases, devtypes,  namespace, register)

        cls =  type.__new__( mcs, clsname, bases, namespace)
        cls.__register__ = register 

        if generate_methods:
            AllAsyncCommandMethodGenerator.static_populate(cls)
            if cls.Setup is BaseDevMgrSetup:
                device_properties = _device_properties_copy( cls )
                cls.Setup = DevMgrSetupMeta(
                        'ACmdDevMgrSetup', (BaseDevMgrSetup,), device_properties, 
                        devtypes=devtypes,  generate_methods = True
                    )
        return cls


class BaseDevMgrAsyncCommands(
        DaqAsyncCommands, StdAsyncCommands, AppAsyncCommands,
        metaclass=DevMgrAsyncCommandsMeta, 
        devtypes=[], 
        generate_methods=False
    ):
    """ Dev Mgr Commands used to send asynchronous command to an FCS Device Manager  

    Args:
        interface (ClientInterfacer, str): A Client Interface or a uri string 
            If this is a Client Interface the timeout argument should be None 
        timeout (int, optional): Used only if interface is a string otherwise this is ignored 
    """

    Setup = BaseDevMgrSetup 
    _devtypes_map = None 

    def __init__(self, interface: ClientInterfacer| str, timeout: int| None = None):
        if isinstance(interface, str):
            interface = Interface(interface, timeout) 
        elif timeout is not None:
            raise ValueError(f"Timeout argument is only valid when receiving an string uri got a {type(interface)}")
        
        self.interface = interface 
  
    async def new_setup(self)->Setup:
        """ Return a new Setup Buffer for this Fcs """
        return self.Setup(self.interface)
    
    def _build_device(self, devname:str, devtype:str | type[BaseDeviceAsyncCommand] | None):
        # function required and in interAface with DeviceProperty object 
        DeviceAsyncCommandClass =  self.__register__.async_command_class(devtype)
        return DeviceAsyncCommandClass(self.interface, devname) 
    
    def _get_device(self, devname, devtype):
        # necessary because in interface with DeviceProperty (alway syncrhonous) 
        return self._build_device(devname, devtype)

    async def new(self,
          devname:str, 
          devtype: str | type[BaseDeviceCommand] |  None = None
        )->BaseDeviceCommand:
        """ Return A Device Command object for the given device 

        Args:
            devname (str): device name 
            devtype (str,optional): device devtype. If not given this will be taken from server 
                    devtype can however be usefull if working offline. 
        """
        if devtype is None:
            devtype = await self.get_devtype(devname)
        return self._build_device(devname, devtype)    
    

    async def get(self, 
          name: str,  
          devtype: str | type[BaseDeviceCommand] |  None = None
        )->BaseDeviceCommand:
        """ Return A Device Command object for the given device 
            
        This is an alias of the new method 

        Args:
            name (str): device name 
            devtype (str,optional): device devtype. If not given this will be taken from server 
                    devtype can however be usefull if working offline. 

        """
        return await self.new(name, devtype)

    async def get_devtypes(self):
        """ Return a mapping of devname->devtypes for all devices managed by the server

        Returns:
            map (dict): dictionary of devname-> devtype 
        """
        if self._devtypes_map is None:
            devtypes = eval( await self.devinfo() )

            self._devtypes_map = {**devtypes, **self.__builtin_devtypes_map__}
        return self._devtypes_map 
    
    async def get_devtype(self, devname: str)-> str:
        """ Get the device type ot a given devname 

        Args:
            name (str): device name 

        Returns:
            devtype (str): device type 

        Raise:
            ValueError if the device is not found 
        """
        try:
            devtypes  = await self.get_devtypes()
            return devtypes[devname]
        except KeyError:
            raise ValueError(f"device name <{devname}> not managed by the server")
    
    async def devstatus_handler(self, *devnames)->StatusHandler:
        """ Executes a DevStatus Command and wrap result in a handy object
        
        Result is returned in a StatusHandler object which is used to 
        manipulate the returned status payload. 

        Args:
            *devnames (variable list):  List of devices to inquire status.

        It no devices are provided, the status will include all devices.

        """
        return StatusHandler( await self.devstatus(*devnames) )

    async def devstatus_regex(self, pattern=None)->str:
        """ DevStatus Command and match output with a pattern

        Args:
            pattern (str): Pattern to match with regular expression


        The server will deliver the status for all devices.
        This method will filter the output according the pattern
        provided. 
        """
        async with self.interface.command('App','DevStatus') as adevstatus:
            reply = await adevstatus([])
            return _match_devststus_pattern( pattern, reply )
    
    
    async def wait( self, key:str, value:Any, *devnames, **kwargs):
        """ Wait for a given status rule to be true on several devices 

        Args: 
            key (str): status key suffix, e.g.: 'lcs.substate' 
            value (Any): if a callable must be of signature f(data)
                where data is the retrieved status data.
                Otherwise value is compared with == to the targeted status 
            *devnames: list of device to check if not given all devices are used
        
        Kwargs (same as StatusWaiter):
            timeout (int): timeout in ms after which a RuntimeError is raised 
            period  (int): the cycle period in ms to retrieve hardware status (default is 500)
            operator (Callable): Operator to treat several values of several devices into one 
                boolean var. Default is the function ``all``

        Exemple::

            c = DevMgrAsyncCommand.from_consul('fcs2-req')
            
            # wait that lamp1 and lamp2 are on 
            await c.wait( "lcs.substate", "On", "lamp1", "lamp2" )
            
            # wait that one of the lamp is turned Off 
            await c.wait( "lcs.substate", "Off", "lamp1", "lamp2", operator=any )
            
            # wait that a motor position is above > 30.0 uu 
            await c.wait( "pos_actual", lambda pos:pos>30.0, 'motor1')
        """

        waiter =  StatusWaiter(self.interface,  key, value, **kwargs)
        return await waiter.async_wait( *devnames )
    
    @classmethod
    async def help(cls, func=None):
        """ Provides a text based help of the Command class functions.

        Args:
            func (str, optional): Name of the function from where to get the help

        This method is to be used for the implementation of CLIs.
        Functions are methods of the class.
        If the parameter <func> is not provided then the help provides a list of
        functions. Functions started with '_' are skipped.
        """
        return class_help(cls, func)


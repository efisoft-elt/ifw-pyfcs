from __future__ import annotations
from typing import Any, Callable, Dict, List, Type

from ModFcfif.Fcfif import VectorfcfifSetupElem
from ifw.fcf.clib import log

from pyfcs.core.device import DeviceProperty, BaseDeviceSetup, register 
from pyfcs.core.tools import PayloadReceiver, BufferHolder 
from pyfcs.core.define import ClientInterfacer, DeviceClassGetter, SetupEntity
from pyfcs.core.interface import SetupCommand 
from pyfcs.core.generator import  AllSetupMethodGenerator


def populate_schema(cls: type[SetupEntity], definitions: dict)->None:
    """ Populate a schema definition with the schema definition of the DeviceSetup class 
    
    Args:
        cls (type): A subclass of DeviceSetup 
        definitions (dict):  dictionary containing all schema definitions 

            {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "title": "FCF schema",
              "type": "array",
              "items": { ... },
              "definitions": { }  <--- This is this one 
            }
    """
    devtype = cls.get_devtype() 
    
    definitions[devtype] =  cls.get_schema()
    param = definitions.setdefault('param', {})
    param.setdefault('oneOf',[]).append( {'required': [ devtype] } )
    param.setdefault('properties', {})[devtype] = { "$ref": "#/definitions/"+devtype }

def create_empty_schema()->dict[str,Any]:
    return { 
          "$schema": "http://json-schema.org/draft-07/schema#",
          "type": "object",
          "title": "FCF schema",
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string",
                "description": "device identifier."
              },
              "param": {
                "$ref": "#/definitions/param"
              }
            }, 
            "required": ["id", "param"],
            "additionalProperties": False
          },
          "definitions": { # To Be filled 
            "param": {
              "type": "object",
              "properties": { }, # To Be filled 
            "oneOf": [] # To be Filled 
            },

            }
          }


def _collect_devtypes(bases:tuple, devtypes:list[str]|str|None, namespace:dict[str,Any], register: DeviceClassGetter)->None:
    """ 
    Build inside namespace :
        __devtypes__ :  list of accepted device types (str) for this class 
            This will be used to generate methods automaticaly 
        __builtin_devtypes_map__ : A dictionary of "builtin" devname->devtype 
            Basicaly they are devices included with the DeviceProperty object 
            e.g. : 
                class B(...):
                    motor1 = DeviceProperty('motor')
                    motor2 = DeviceProperty('motor')
            Will create __builtin_devtypes_map__ = {'motor1': 'motor', 'motor2':'motor'}
            
            If some types are not in __devtypes__ they will be added to __devtypes__ 
    
    If devtypes argument is None, this will fix the devtype map for the object instance 
    (e.g. the  _devtypes_map will be created on the class)
    Otherwise the instance will ask server for the devname->devtype map on demand.
    If devtypes is 'all' (default), all registered devices will be added (but not assemblies)
    """

    fix_devtypes = False 

    if devtypes is None:
        fix_devtypes = True 
        devtypes = set()
    elif devtypes in [all, "all", "All"]:
        devtypes = set( register.get_devtypes(exclude_assemblies=True))
    else:
        devtypes = set(devtypes)
        
    devmap = {} 
    
    for cls in bases:
        try:
            devmap.update(   cls.__builtin_devtypes_map__ )
        except AttributeError:
            pass
        
        

    for key,obj in namespace.items():
        if isinstance( obj, DeviceProperty):
            devmap[ obj.devname or key ] = obj.devtype
            
    # Add any devtypes inside the builtin devtyp_map inside 
    # the accepted set of devtypes 
    devtypes.update( devmap.values() )
    namespace['__builtin_devtypes_map__'] = devmap 
    namespace['__devtypes__'] = tuple(devtypes)

    if fix_devtypes:
        namespace['_devtypes_map'] = devmap 

def _collect_register( bases ):
    for sub in bases:
        try:
            return sub.__register__ 
        except AttributeError:
            pass             
    return register 


class DevMgrSetupMeta(type):
    """ A Meta Class for a DevMgrSetup """
    def __new__(mcs, clsname, bases, namespace, 
            devtypes:list[str]|str | None = 'all', 
            generate_methods: bool = True,
            register: DeviceClassGetter|None = None
        ): 
        if register is None:
            register = _collect_register( bases)  
        _collect_devtypes(bases, devtypes,  namespace, register) 
        cls =  type.__new__( mcs, clsname, bases, namespace)
        cls.__schema__ = None # force to None will be created by get_schema  
        cls.__register__ = register 
        if generate_methods:
            AllSetupMethodGenerator.static_populate(cls)
        return cls




class BaseDevMgrSetup( metaclass=DevMgrSetupMeta, devtypes=[], generate_methods=False):
    """ Class manage the buffer of the setup request """
    _devtypes_map = None # Will be filled at request from server 
    
    def __init__(self, interface: ClientInterfacer):
        self.interface = interface 
        self._buffer: list[SetupEntity] = [] 
        self.payload_receiver = PayloadReceiver(self.get_schema())

    @classmethod 
    def get_schema(cls)->dict:
        """ Class Method: return the class JSON schema 
        
        Returns:
            schema (dict): JSON schema for the setup buffer class 
        """
        schema = getattr(cls, "__schema__", None)
        if schema:
            return schema

        schema = create_empty_schema()
        

        definitions = schema['definitions']
        
        for devtype in cls.__devtypes__:
            populate_schema( cls.__register__.setup_class(devtype), definitions)
        
        # save for next time. Maybe it shall be in Meta??
        cls.__schema__ = schema 
        return schema  

    def __iter__(self):
        return self._buffer.__iter__()

    def __getitem__(self, item):
        return self._buffer[item] 
    

    def get_devtypes(self)->dict[str,str]:
        """ Return a mapping of devname->devtypes for all devices managed by the server

        Returns:
            map (dict): dictionary of devname-> devtype 
        """
        if self._devtypes_map is None:
            with self.interface.command('App', 'DevInfo') as devinfo:
                dev_info_str = devinfo()

            # defined inside buffer class definition ( e.g. assemblies ) 
            devtypes = { **eval(dev_info_str), **self.__builtin_devtypes_map__}
            self._devtypes_map = devtypes            

        return self._devtypes_map

    def get_devtype(self, devname: str)-> str:
        """ Return the device type of a given device
        
        Args:
            devname (str): device name (or id)  
        
        Returns:
            devtype (str): device devtype 
        
        Raises:
            ValueError if the device does not exists 
        """
        try:
            return self.get_devtypes()[devname] 
        except KeyError:
            raise ValueError(f"device name <{devname}> not managed by the server")
    
    def clear(self):
        """ Clear the current setup buffer """
        self._buffer.clear()
    
    def _clear_callback(self, err=None):
        """ A callback for the command executor 
        Clear is executed only if no error was raised  
        """
        if err is None:
            self.clear()
        else:
            log.info("setup command execution failed, buffer wasn't cleaned")

    def add_new(self, 
            devname:str , 
            devtype: str| Type[BaseDeviceSetup] |  None =None, 
            override: bool=False
        )->BaseDeviceSetup:
        """ Add a new device setup to the buffer and returns it 
        
        .. note:: 

            See the get method which will always return an existing device setup 
                or create one. 

        Args:
            devname (str): device name 
            devtype (optional, str): device type, if not given the server is asked unless 
                                     the devname->devtype is frozen on the class 
            override (optional, bool): If True it wiil override existing device setup.
                                     default is False.

        Returns:
            dev_setup (DeviceSetup): handy object to set the buffer for this device

        Exemple::

            fcs1_setup.add_new('lamp1').switch_on( 20.0, 10)
            fcs1_setup.setup()

        """                
        device_setup = self.new(devname, devtype)
        self.add(device_setup, override=override)
        return device_setup 
    
    def add(self, *devices: tuple[SetupEntity], override: bool = False):
        """ Add several DeviceSetup objects
        
        Note:: 

            See the get method which will always return an existing device setup 
                or create one

        Args:
            *device_setup (list[DeviceSetup]): Device Setup objects  
            override (optional, bool): If True it wiil override existing device setup 
        
        """
        for device_setup in devices:
            self._add_one( device_setup, override=override)
    
    def _add_one(self, device_setup: SetupEntity, override: bool = False)->None:
        found  = 0
        if override:
            for i,item in enumerate(self._buffer):
                if item.id == device_setup.id:
                    self._buffer[i] = device_setup 
                    found += 1
        if not found:
            self._buffer.append(device_setup)
        return found 
    
    def _get_device(self, devname:str , devtype: str | None = None)->BaseDeviceSetup:
        # necessary because in interface with DeviceProperty 
        return self.get(devname, devtype) 

    def new(self, devname:str , devtype: str | Type[SetupEntity] | None = None)->SetupEntity:
        """ Return a new device setup object but does not include it on the buffer 
        
        .. warning:: 

            This method will not include the created DeviceSetup in the buffer.
            Use the .get or add_new method for that. Or the .add method to add it
            

        Args:
            devname (str): device name 
            devtype (optional, str): device type, if not given the server is asked
        
         Returns:
            dev_setup (DeviceSetup): handy DeviceSetup object

        Exemple::

            lamp1 = fcs1_setup.new('lamp1')
            lamp1.switch_on( 20.0, 10)
            fcs1_setup.add( lamp1 , override=True) 

            # Equivalent to 
            fcs1_setup.get('lamp1').switch_on( 20.0, 10) 

        """
        if devtype is None:
            devtype = self.get_devtype(devname)
        DeviceSetupClass = self.__register__.setup_class(devtype)
        return  DeviceSetupClass(self.interface, devname) 
    
    
    def get(self, devname:str , devtype: str | None = None)->SetupEntity:
        """ Return the device setup object matching the name 
        
        If not found in the current buffer, a new one is created and added 

        Args:
            devname (str): device name 
            devtype (optional, str): device type, if not given the server is asked

        Exemple::

            buffer.get('lamp1').switch_on( 20.0, 10)
        """
        for device_setup in self._buffer:
            if device_setup.id == devname:
                return device_setup
        return self.add_new( devname, devtype, override=False)


    def set_payload(self, payload: List[Dict[str,Any]], override: bool = True )->None:
        """ Set an incoming payload to the setup buffer 

        Args:
            payload (list): A payload (probably comming from a json data)
            override (optional, bool): If True (default), the setup buffer 
                definition of an existing device will be overided. Added otherwise  
        """
        # payload validated agains schema 
        payload = self.payload_receiver.parse( payload )
        self._set_safe_payload( payload, override ) 

    def _set_safe_payload(self, payload: List[Dict[str,Any]], override: bool = True )->None:
        """ Add an alreadyvalidated payload to the buffer """
        devices_to_add = [] # add them only at the end if no failure  
        for i,element in enumerate(payload):
            try:
                param = element['param']
                device_id = element['id']
            except KeyError as err:
                raise ValueError(f"Item #{i} is not a valid payload ") from err

            log.debug("element: %s", element)
            log.debug("id: %s", device_id)
            log.debug("param: %s", param)
            
            for devtype, param_payload in param.items():
                try:
                    device_setup = self.new(device_id, devtype)
                    device_setup.set( **param_payload )
                except Exception as err:
                    log.error( f"Problem when setting the payload parameters {param_payload} in device  {device_id!r} as {devtype}  ")
                    raise ValueError( f"Seting up {device_id!r} as {devtype} failed" ) from err
                else:
                    devices_to_add.append( device_setup )
        # everything went well we can add them 
        self.add(*devices_to_add, override=override)
    
    def get_buffer(self) -> VectorfcfifSetupElem:
        """ Build and return the buffer 
        
        Uncomplete Setup Devices (Usually when the Action has not been set) 
        will be ignored silently 

        Return:
            buffer: VectorfcfifSetupElem ready to be sent by Mal client Setup method    
        
        """
        buffer =  VectorfcfifSetupElem()
        for ds in self._buffer:
            buffer.extend( ds.get_buffer() )
        return buffer 

    def get_payload(self, force: bool=False)->list[dict[str,Any]]:
        """ Return the payload representation of this setup buffer 

        Returns:
            payload : list of dictionary 
        """
        return sum( (ds.get_payload(force) for ds in self._buffer) , [])
    
    def load_buffer(self, buffer: VectorfcfifSetupElem, override=True)->None:
        """ Update the current Setup from a buffer (VectorfcfifSetupElem) 
        
        .. warning:: 

            load_buffer will not work correctly if the curent setup has assemblies. 
            It will update the payload of device  member of the essembly instead 
            of the assembly.

        Args:
            buffer ( VectorfcfifSetupElem )
            override ( optional , bool): if True (default) current setup with the same 
                same id will be overrided. If false a new buffer element is added 

        Exemple:

            b1 = DevMgrSetup.from_consul('fcs2-req')
            b2 = DevMgrSetup.from_consul('fcs2-req')
            
            b1.add_lamp_switch_on('lamp1', 50, 10) 
            assert b1.get_payload() != b2.get_payload()
            b2.load_buffer( b1.get_buffer() )
            assert b1.get_payload() == b2.get_payload()

        """        
        for element in buffer:
            id = element.getId()
            new: BaseDeviceSetup = self.add_new(id, override=override) 
            new.load_buffer( element )


    def setup(self, keep: bool = False)->str:
        """ Send the current setup to the server 
        
        Args:
            keep (optional, bool): if False (default) the current buffer will be cleared 
                otherwhise it stays inside the setup buffer. 
                
                ..note:: 

                    In case of error during setup the setup buffer is never cleared. 

        Returns:
            mgs (str): Server Setup message 

        """
        callback = None if keep else self._clear_callback

        with self.interface.command('App', 'Setup', callback) as setup:
            setup( self.get_buffer() )
    
    async def async_setup(self, keep: bool=False):
        """ Send the current setup to the server asynchroniously  
        
        Args:
            keep (optional, bool): if False (default) the current buffer will be cleared 
                otherwhise it stays inside the setup buffer. 
                
                ..note:: 

                    In case of error during setup the setup buffer is never cleared. 

        Returns:
            mgs (str): Server Setup message 

        """

        callback = None if keep else self._clear_callback

        async with self.interface.command('App', 'Setup', callback) as asetup:
            await asetup( self.get_buffer() )
        
    def create_setup_command(self, froze: bool = True, callback: Callable| None =None)-> SetupCommand:
        """ deport the setup command in a new object to be executed later  

        It return a standardized command object with (.exec() and .async_exec()) methods. 
        This can be usefull for the sequencer.

        Args:
            froze (optional, bool): if True (default) the setup is frozen it will be independant of 
                this setup buffer. If False any changes in this setup buffer object will be applied 
                to the returned CommandSetup 
            callback (optional, callable): callback function with signature f(err) called after setup.
                err is None in case of success or an exception instance in case of error. 
        """
        if froze:
            return SetupCommand(
                self.interface, 
                BufferHolder(self.get_buffer()), 
                callback
            )
        else:
            return SetupCommand(self.interface, self, callback)

    def __repr__(self)->str:
        cls = self.__class__
        name = (cls.__module__ + '.' + cls.__qualname__ )
        return f"<{name} at 0x{id(self):x} {self._buffer!r} >" 


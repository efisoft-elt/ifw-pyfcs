from __future__ import annotations

from abc import ABC, ABCMeta, abstractclassmethod, abstractmethod
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Dict, Union


from ModFcfif.Fcfif import SetupElem, VectorfcfifSetupElem
from elt import pymal


from pyfcs.core.define import ClientInterfacer
from pyfcs.core.interface import SetupCommand  
from pyfcs.core.tools import BufferHolder 

from .method_decorator import get_payload_parser_info, _empty
from .parameter import ParamProperty
from .mal_if import BaseMalIf
from .factories import DeviceFactoryMethods
from .class_inspector import SetupClassDefinition 


PayloadElement = Dict[ str, Union[str,Dict[str,Any]]]

def get_setup_methods(cls: type[BaseDeviceSetup])->set[str]:
    """ Return a set of setup method names of a DeviceSetup Class """
    return cls.__setup_definition__.setup_methods

def get_parameters(cls: type[BaseDeviceSetup])->set[str]:
    """ Return a set of parameter names of a DeviceSetup Class """
    return cls.__setup_definition__.parameters 

def create_schema(cls: type[BaseDeviceSetup])->dict:
    """ Build the schema definition for a DeviceSetup class 

    Args:
        cls (type): A subclass of DeviceSetup 
    
    Returns:
        schema_definition (dict): the schema definition of the DeviceSetup class  
    """
    scd = cls.__setup_definition__
    
    parameters = scd.parameters 
    properties = {}
    required = []
    definitions = { # Base schema definition 
           'type':'object',  
            'properties':properties, 
            'required': required, 
            'additionalProperties': False 
        } 

    for param_name in parameters:
        param = getattr(cls, param_name)
        name = param.name or param_name 
        properties[name] = param.get_schema()
        if param.required:
            required.append( name )
    allOf = _create_allOf_schema(cls)
    if allOf:
        definitions['allOf'] = allOf
    
    return definitions  


def _create_allOf_schema(cls: type[BaseDeviceSetup])->list[dict]:
    """ generate the 'allOf' part of a schema definition from the payload_parser methods """

    scd = cls.__setup_definition__
    allOf = []
    
    # sort by number of constrains 
    for context_keys in scd.parser_context_keys:
        context_values = scd.payload_parser_loockup[context_keys]

        for values, method_name in context_values.items():
            if_properties = { k: {"const": v} for k,v in zip( context_keys, values) }
            if_ = {"properties": if_properties} 
            method = getattr(cls, method_name)
            

            info = get_payload_parser_info (method) 
            if not info.contexts or not info.required:
                continue 
            
            required = info.required


            then = { "required": required, }
            if info.minProperties not in (None,_empty):
                then['minProperties'] = info.minProperties 
            
            if info.maxProperties not in (None,_empty):
                then['maxProperties'] = info.maxProperties 


            allOf.append( { "if": if_ , "then": then })
    return allOf


class DeviceSetupMeta(ABCMeta):
    """" MetaClass for a DeviceSetup class  """ 
    def __new__(mcs, clsname, bases, namespace, **kwargs):  
        setup_definition = SetupClassDefinition() 

        # merge the subclasses setup_definition 
        for cls in bases:
            try:
                sd = cls.__setup_definition__ 
            except AttributeError:
                pass 
            else:
                setup_definition.merge(sd )
        
        # Add special object (ParamProperty, @setup_method, @payload_parser method  and @payload_maker method)
        for key,obj in namespace.items():
            setup_definition.add_obj( key, obj )
            
        namespace['__setup_definition__'] = setup_definition
        namespace['__schema__'] = None # force None Will be build from get_schema 
        return super().__new__( mcs, clsname, bases, namespace, **kwargs)


class BaseDeviceSetup(ABC, DeviceFactoryMethods,  metaclass=DeviceSetupMeta): # Must Follow SetupEntity Protocol
    devtype = None
    _params_buffer: dict 
    MalIf = BaseMalIf 

    def __init__(self,
        interface: ClientInterfacer, 
        device_id: str, 
      )->None:
        self.interface = interface 
        self.id = device_id
        self._params_buffer = {}

    @classmethod
    def get_devtype(cls):
        """ ClassMethod - Return the device type name """
        return cls.devtype
        
    @classmethod
    def get_schema(cls)->dict[str,Any]:
        """ClassMethod -  Build the json schema definition for  the class 
        
        Returns:
            schema_definition (dict): the schema definition of the class  
        """
        if cls.__schema__ is None:
            cls.__schema__ = create_schema(cls)
        return cls.__schema__

    
    @classmethod
    def get_param_property(cls, name: str)-> ParamProperty:
        """ClassMethod - Return the parameter property object of a given parameter name """
        try:
            return getattr(cls, name)
        except AttributeError:
            raise ValueError( f"unknown parameter {name!r}") 

    def is_param_set(self, param: str)->None:
        """ return True if the parameter has been set """
        return param in self._params_buffer
     
    def is_action_set(self)->bool:
        """ Return True if parameter ``action`` has been set """
        return self.is_param_set( "action" )
    
    def is_setup_valid(self)->bool:
        """ True if the setup is complete (usually if action has been set) """
        return self.is_action_set()

    def clear(self):
        """ Clear the setup buffer. Reseted at its init state """
        self._params_buffer.clear()

    def set(self, __payload_dict__={}, **payload):
        """ Set a parameters  payload add it to the device setup buffer  
        
        ..note::

            in the context of a full payload, parameter payload is, e.g : 
                [{'id':'mylamp', 'param':{'lamp': --> {} <-- This Guy }}]
        
        ..note::
            
            ``dev.set( payload)``
            Is strictely equivalent to 
            ``dev.set( **payload )``

            Exemple: 

                ``lamp.set( {'action':'ON', 'intensity':40, 'time':10} )``
                ``lamp.set( action='ON', intensity=40, time=10 )
        
        Raises:
            ValueError: if the param payload is not valid 
        """
        payload = {**__payload_dict__, **payload}
        sd = self.__setup_definition__ 
        # look if we have a method to validate the payload according to some 
        # keys in the payload (`context_keys`)
        context_keys, validator = sd.find_payload_parser_method(payload) 
        
        if validator is None:
            for key, value in payload.items():
                # Use setattr: The value needs to be parsed  
                setattr(self, key, value)
        else: 
            # remove context parameter from the payload before sending 
            # to the validator method
            for key in context_keys:
                payload.pop(key)

            # use partial in order to deal with positional argument by name 
            partial(getattr(self, validator), **payload )()

    def get_parameter_payload(self,all=False)->dict[str,Any]:
        """ get the parameter payload 
        
        The returned payload depends on the parameters that has been set.
        Normaly the parameter payload is valid.
        if ``all=True`` All possible properties  are returned resulting in non-valid payload 

        """
        sd = self.__setup_definition__
        if all:
            # use getattr to parse out value from internal buffer 
            return {k:getattr(self,k) for k in self.sd.parameters}
        
        method_name = sd.find_payload_maker_method(self)
        
        if method_name is None:
            # return everything which has been set 
            return {k:getattr(self,k) for k in self._params_buffer}
        else:
            return getattr(self, method_name)()
     
    def get_element_payload(self)->PayloadElement:
        """ Get the payload element for this device setup """
        return {
                'id': self.id, 
                'param': {self.devtype.lower():self.get_parameter_payload()} 
            }  
   
    def get_payload(self, force: bool=False)->list[PayloadElement]:
        """ Return the payload of the current device setup buffer  device
        
        If the action has never been set this returns an empty list unless force is True 

        Args:
            force (bool, optional): force returning a non-empty payload in case where the 
                action wasn't set

        Returns:
            payload:  A list of dictionary in the form:
                [{'id':lamp1,'param':{'lamp':{'action':'OFF'}}]
                 The payload is [] if payload is not complete (e.g. no action was set) 
                 unless ``force=True``

        """
        if force or self.is_setup_valid():
            return [self.get_element_payload()] 
        else:
            return []
    
    def load_buffer(self, element: SetupElem| VectorfcfifSetupElem | BaseDeviceSetup)->None:
        """ Update the current setup from an existing buffer 
        
        Args:
            buffer_element (SetupElement,  VectorfcfifSetupElem, DeviceSetup):
                 If a Vector is given, it must be of len == 1
        """
        if isinstance( element, VectorfcfifSetupElem):
            if len(element)>1:
                 raise ValueError("The receive Vector Setup Elem has a len greater than one ")
            if not len(element):
                raise ValueError("The receive Vector Setup Elem is empty")
            element = element[0]
        
        if isinstance(element, BaseDeviceSetup):
            self._params_buffer.update( element._params_buffer ) 
            self.id = element.id 
        else: 
            malif = self.MalIf( self.interface, element)
            self._params_buffer.update( malif.get_values() )
            self.id = malif.get_id()

    def get_malif(self)->MalIf:
        """ Build and return a device mal interface for this device """
        malif = self.MalIf(self.interface)
        malif.set_values( self._params_buffer )
        malif.set_id(self.id)
        return malif 
    
    def get_element_buffer(self)->SetupElem:
        """ Return the Mal SetupElem of the curent device setup buffer """
        return self.get_malif().element 
        
    def get_buffer(self)->VectorfcfifSetupElem:
        """ Return the Cii/Mal buffer for the device 

        If the setup is uncomplete (e.g. action wasn't set) the buffer will be empty 

        Resturns:
            buffer (VectorfcfifSetupElem): Mal buffer vector 
        """
        buffer= VectorfcfifSetupElem()
        if self.is_setup_valid():
            buffer.append( self.get_element_buffer())
        return buffer

    def create_setup_command(self, froze=True, callback=None)->SetupCommand:
        """ Create a new SetupCommand from the device setup buffer 
        
        The setup command can be used to send the setup buffer independently 
        to this device setup instance and can be combined with others. 

        Args:
            froze (bool, optional): if True (default)  The payload inside the SetupCommamd
                is independent of this device setup instance. 
                If false it will follow the changes of setup of this instance.
            callback (Callable, optional): A callback method to be executed when a setup is done 

        Returns:
            setup command  :class:`SetupCommand` 
        
        Exemple::

            from pyfcs.devices import LampSetup 
            lamp1 = LampSetup.from_dummy('lamp1')

            lamp1.switch_on( 40.0, 10)

            setup = lamp1.create_setup_command()
            
            # Then later : 
            setup.exec() # execute the setup (switch on with intensity 40.% time 10 seconds)
            await setup.async_exec() # same thing but asynchronously 

        """
        if froze:
            return SetupCommand(
                    self.interface, 
                    BufferHolder(self.get_buffer()), 
                    callback
                )
        else:
            return SetupCommand(self.interface, self, callback)

    def setup(self):
        """ Execute the current setup to the real HW """
        with self.interface.command('App', 'Setup') as app_setup:
            return app_setup( self.get_buffer() )
    
    async def async_setup(self):
        """ Execute the current setup to the real HW asynchronously """
        async with self.interface.command('App', 'Setup') as asetup:
            return await asetup( self.get_buffer() )

    def __repr__(self) -> str:
        cls = self.__class__
        name = (cls.__module__ + '.' + cls.__qualname__ )
        params = ", ".join ( k+"= "+ repr(getattr(self, k)) for k in self._params_buffer  ) 
        return  f"<{name} at 0x{id(self):x} id={self.id!r} {params}>"

 




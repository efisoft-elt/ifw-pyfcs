from __future__ import annotations 
from dataclasses import dataclass, field
from typing import Any, Callable

from .method_decorator import get_payload_maker_info, get_payload_parser_info, is_payload_maker, is_setup_method, is_payload_parser
from .parameter import ParamProperty 

@dataclass
class SetupClassDefinition:
    """ Object use to handle special attibutes of a DeviceSetup class

    It holds and organise the names of parameters, setup_method, payload_parser, and
    payload_maker methods.
    """
    # This Object is instancied  in the metaclass of DeviceSetup 
    

    parameters: set[str] = field(default_factory=set)
    setup_methods: set[str] = field(default_factory=set)
        
    payload_parser_loockup: dict[tuple,dict] = field(default_factory=dict)
    payload_maker_loockup: dict[tuple,dict] = field(default_factory=dict)
    
    
    def __post_init__(self):
        self._reorder_parser_keys()
        self._reorder_maker_keys() 

    def _reorder_parser_keys(self):
        """ re-build the sorted list for the context dictionary 
        
        The ones with the maximum number of keys should appear first 
        
        """
        # TODO: Check if the ordering is correct or if we need to conserve the 
        # order of method declaration
        self.parser_context_keys = sorted( self.payload_parser_loockup, key=lambda t: len(t), reverse=True)
    
    def _reorder_maker_keys(self):
        self.maker_context_keys = sorted( self.payload_maker_loockup, key=lambda t: len(t), reverse=True)
 

    def merge(self, setup_def: 'SetupClassDefinition')->None:
        """ merge this SetupClassDefinition to an other one DeviceAsyncCommand

        Args:
            setup_def (SetupClassDefinition) 

        """
        self.setup_methods.update( setup_def.setup_methods )
        self.parameters.update( setup_def.parameters) 
        
        for context_keys, context_def in setup_def.payload_parser_loockup.items():
            self.payload_parser_loockup.setdefault( context_keys, {}).update(context_def)

        for context_keys, context_def in setup_def.payload_maker_loockup.items():
            self.payload_maker_loockup.setdefault( context_keys, {}).update(context_def)
        
        self._reorder_parser_keys()
        self._reorder_maker_keys() 
 
    
    def add_setup_method(self, name: str, method: Callable)->None:
        """ Add a new setup method 
        
        Note: Setup methods are use to automaticaly populate methods in other classes 
        such as DevMgrSetup or DevMgrCommand.

        Args:
            name (str): method name as defined in the DeviceSetup class 
            method (Callable): Method flaged as a setup method 

        
        """
        self.setup_methods.add(name)

    def add_payload_parser_method(self, name: str, method: Callable)->None:
        """ Add a new payload parser method 
        
        Args:
            name (str): method name as defined in the DeviceSetup class 
            method (Callable): must have been decorated by @payload_parser() 


        """
        info = get_payload_parser_info(method)
        if info.context_keys:
            self.payload_parser_loockup.setdefault( info.context_keys, {})[info.context_values] = name
            self._reorder_parser_keys()
    
    def find_payload_parser_method(self, 
            payload: dict[str,Any]
          )->tuple[ tuple[str], str|None]:
        """ From a payload dictionary try to find the appropriate payload parser method 
            
        Args:
            payload (dict[str,Any]) : a received payload

        Returns:
            context_key: tuple of matching context keys 
            method_name (str): the method name or None is not found 

        Exemple::
            
            from pyfcs.core.api import BaseDeviceSetup, payload_parser
            class Dev(BaseDeviceSetup):

                @payload_parser(action="MOVE_ABS", unit="UU")
                def move_abs_uu(self, pos):
                    pass
                
            cd = Dev.__setup_definition__

            payload = {'action':"MOVE_ABS", 'unit':"UU", 'pos':3.4 }
            context, name = cd.find_payload_parser_method(payload)
            assert (context, name) == ( ("action", "unit"), "move_abs_uu" )
            
        """
        for context_key in self.parser_context_keys:
            values = tuple( payload.get( k, None) for k in context_key )
            try:
                return context_key, self.payload_parser_loockup[context_key][values]
            except KeyError:
                pass 
        return tuple(), None        
    
    def add_payload_maker_method(self, name: str, maker: Callable)->None:
        """ Add a new payload maker method 
        
        Args:
            name (str):  method name as defined in the DeviceSetup class  
            maker (Callable): method, must have been decorated by @payload_maker() 
        """
        info = get_payload_maker_info(maker)
        
        if info.context_keys:
            self.payload_maker_loockup.setdefault( info.context_keys, {})[info.context_values] = name
            self._reorder_maker_keys() 

    def find_payload_maker_method(self, setup)->str|None:
        """ From a DeviceSetup instance try to find the method to dum a payload 

        Args:
            setup (DeviceSetup)

        Returns:
            method_name : str or None if not found 

        Exemple::

            from pyfcs.core.api import BaseDeviceSetup, payload_maker, ParamProperty

            class Dev(BaseDeviceSetup):
                devtype = 'test'
                action = ParamProperty(str)
                pos = ParamProperty(float)
                unit = ParamProperty(str) 
                
                @payload_maker(unit="UU", action="MOVE")
                def dump_pos(self):
                    return { "unit":"UU", "pos":self.pos }
            
            dev = Dev.from_dummy('test1')
            dev.unit = "UU"
            dev.action = "MOVE"
            dev.pos = 4.5 
            assert dev.get_element_payload() == {'id':'test1', 'param':{'test':{'unit':'UU', 'pos':4.5}}}
            

        """
        for context_key in self.maker_context_keys:
            values = tuple( getattr( setup, k, None) for k in context_key )
            try:
                return  self.payload_maker_loockup[context_key][values]
            except KeyError:
                pass 
        return None        


    def add_parameter(self, name:str, param: ParamProperty):
        """ Add a new parameter property 

        Args:
            name (str): Parameter name as it is declared in the DeviceSetup method 
            param (ParamProperty): Not used yet
        """ 
        self.parameters.add( name )
    
    def add_obj(self, name:str, obj: Any)->bool:
        """ Add a valid  object or do nothing 
        
        Valid Object are :
            - ParamProperty 
            - method decorated with @setup_method
            - method decorated with @payload_parser
            - method decorated with @payload_maker 

        Args:
            name (str): Object name as declared in the DeviceSetup class 
            obj (Any) 

        Returns:
            added (bool):  True if the object has been added False otherwise 

        """
        added = False 
        if is_setup_method(obj):
            self.add_setup_method( name, obj)
            added = True 
        if is_payload_maker(obj):
            self.add_payload_maker_method( name, obj)
            added = True 
        elif is_payload_parser(obj):
            self.add_payload_parser_method( name, obj )
            added = True 
        elif isinstance( obj, ParamProperty):
            added = True 
            self.add_parameter( name, obj)
        return added 



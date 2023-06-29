from __future__ import annotations
from dataclasses import dataclass, field
from functools import partial
import inspect
from typing import Callable, Optional

from jinja2.nodes import Call
from enum import Enum, auto 


class _empty:
    """ empty (but not None) type """
    pass 


@dataclass
class PayloadParserInformation:
    """ Hold information on payload parser methods """
    # contexts is a dictionary of (parameter_name,value) which define the 
    # condition for the method to be called when receiving a device payload 
    contexts: dict = field( default_factory=dict ) 

    # These three properties are normaly built from the method signature 
    required: list| None = None
    maxProperties: int | None = _empty 
    minProperties: int | None = _empty

    @property
    def action(self):
        return self.context.get('action', None)
    
    @property 
    def context_keys(self):
        return tuple(sorted( self.contexts) )
    @property
    def context_values(self):
        return tuple( self.contexts[k] for k in self.context_keys)



@dataclass
class PayloadMakerInformation:
    """ Hold information on payload maker methods """
    # contexts is a dictionary of (parameter_name,value) which define the 
    # condition for the method to be called when building a payload dictionary 
    contexts: dict = field( default_factory=dict )

    @property
    def action(self):
        return self.context.get('action', None)
    
    @property 
    def context_keys(self):
        return tuple(sorted( self.contexts) )
    @property
    def context_values(self):
        return tuple( self.contexts[k] for k in self.context_keys)

def _decorate_setup_method(method: Callable)->Callable:
    """ Flag a method as setup_method and returns it """
    method.pyfcs_setup_method_flag = True 
    return method 

def _decorate_payload_maker_method(info: PayloadMakerInformation, method: Callable)->Callable:
    """ Flag a method as a payload maker method , attach info, and returns it """
    method.pyfcs_payload_maker_info = info 
    return method 

def _decorate_payload_parser_method(info: PayloadParserInformation, method: Callable)->Callable:
    """ Flag a method as a payload parser method , attach info, and returns it 

    Note: the info structure is altered from method signature inspection 
    """
    method.pyfcs_payload_parser_info = info

    required, (min, max) = _inspect_payload_parser_method(method)
     

    if info.required is None:
        info.required = required
    # TODO: in case of info.required is not None, check consistancy 
    #       with method inspection 


    if info.minProperties is _empty:
        if min: # min=0 has no meaning here -> None  
            info.minProperties = min + len(info.contexts)
        else:
            info.minProperties = None

    if info.maxProperties is _empty:
        if max is not None:
            info.maxProperties = max + len(info.contexts)
        else:
            info.maxProperties = None

    return method 

VALID_REQUIRED_PARAM_KINDS = (inspect._ParameterKind.POSITIONAL_ONLY,
                              inspect._ParameterKind.POSITIONAL_OR_KEYWORD, )

NOT_POSITIONAL_PARAM_KINDS = (
            inspect._ParameterKind.VAR_POSITIONAL,
            inspect._ParameterKind.VAR_KEYWORD, 
        )


def _inspect_payload_parser_method( method: Callable)->tuple[list, tuple[int,int]]:
    """ inspect method signature and extract usefull information for payload parser 

    It is expecting that the input method is a normal object method, meaning it should 
    have an instance reference at first argument: e.g. f(self,...) 

    Returns:
        required: list of required parameters 
        (min,max): Minimum of required parameter, Maximum number of parameter
                   max is None if it cannt be determined 
    

    """
    min_param = -1 # -1 to remove the self 
    max_param = -1 
    s = inspect.signature(method)
    params = [] 

    for param, param_definition in s.parameters.items():
        if param_definition.kind in NOT_POSITIONAL_PARAM_KINDS:
            return params[1:], (min_param, None) 
        
        if param_definition.kind in VALID_REQUIRED_PARAM_KINDS:
            if param_definition.default is inspect._empty:
                min_param += 1
                max_param += 1
                if not param.startswith("__"):
                    params.append( param )
            else:
                max_param += 1
        
    return params[1:], (min_param, max_param)
                


def get_payload_parser_info(method: Callable)->PayloadParserInformation:
    """ Return the info structure of a method decorated with payload_parser 

    Args:
        method : Callable 

    Returns:
        PayloadParserInformation 

    Raises:
        ValueError if the method wasn't decorated with payload_parser()

    ..seealso:: is_payload_parser 
    """
    try:
        return method.pyfcs_payload_parser_info  
    except AttributeError:
        raise ValueError("the method does not have fcs information: it wasn't decorated as payload_parser")

def get_payload_maker_info(method: Callable)->PayloadMakerInformation:
    """ Return the info structure of a method decorated with payload_maker 

    Args:
        method : Callable 

    Returns:
        PayloadParserInformation 

    Raises:
        ValueError if the method wasn't decorated with payload_maker()

    ..seealso:: is_payload_maker
"""
    try:
        return method.pyfcs_payload_maker_info  
    except AttributeError:
        raise ValueError("the method does not have fcs information: it wasn't decorated as payload_maker")

def is_setup_method(obj):
    """ -> True if obj is a method decorated with @setup_method """
    try:
        return obj.pyfcs_setup_method_flag 
    except AttributeError:
        return False 
    
def is_payload_parser(obj):
    """ return True is obj is a  method decorated with @payload_parser() """
    try:
        get_payload_parser_info(obj)
    except ValueError:
        return False 
    else:
        return True 

def is_payload_maker(obj):
    """ return True is obj is a method decorated with @payload_maker() """
    try:
        get_payload_maker_info(obj)
    except ValueError:
        return False 
    else:
        return True 

# def setup_method(_fcall_: Optional[Callable] = None, action: Optional[str] =None)->SetupMethod:
def setup_method(_fcall_: Optional[Callable] = None)->Callable:
    """ Decorate a method as a setup method 

    This is intented to be used inside a DeviceSetup class delaration 
    The @setup_method decorator can be combined with the @payload_parser decorator 


    Args:
        fcall (Callable, optional): method definition 

    Exemple:
        class LampSetup(BaseDeviceSetup):
            @setup_method 
            def turn_off(self):
                self.action = "OFF"
           
            @setup_method
            @payload_parser(action = "ON")
            def turn_on(self, intensity, time):
                self.action = "ON" 
                self.intensity = intensity 
                self.time = time 
        
        
    """
    if _fcall_ is None:
        # return a decorator 
        return _decorate_setup_method
    else:
        return _decorate_setup_method(_fcall_)

def payload_parser(*, required:list|None=None, maxProperties:int|None=_empty, minProperties:int|None=_empty,  **contexts ):
    """ Decorate a method as a payload parser. 
    
    The decorator also declare the context on which the method will be called when the 
    device setup is receiving a payload.

    Please, for more details see implementation on devices 
    
    """
    info = PayloadParserInformation( contexts= contexts, required=required, maxProperties=maxProperties, minProperties=minProperties)
    return partial(_decorate_payload_parser_method, info)


def payload_maker(**contexts):
    """ Decorate a method as a payload maker 
    
    The payload maker method is used to produce a valid payload when the context defined 
    by the payload_maker decorator is matched 

    """
    info = PayloadMakerInformation(contexts=contexts)
    return partial(_decorate_payload_maker_method, info)




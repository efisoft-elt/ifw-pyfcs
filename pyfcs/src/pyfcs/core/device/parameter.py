from __future__ import annotations
from dataclasses import dataclass
from enum import EnumMeta
from typing import Any, Callable, Optional, Type
from typing_extensions import Protocol

from .parser import BaseParser , StringParser, parse_parser, ParsingError


class ParamParentProtocol(Protocol):
    _params_buffer : dict 

def set_and_record(param_name:str, setter: Callable, param_set : set[str], value: Any)->None:
    try:
        setter(value)
    except Exception as er:
        raise ValueError("Problem when setting value") from er 
    else:
        param_set.add(param_name)

@dataclass
class MethodNameGetter:
    """ Call the defiined device method to get value """
    method: str 
    def __call__(self, device):
        return getattr( device, self.method)()

@dataclass
class MethodNameSetter:
    """ Call the defined device method to set a value """
    method: str 
    def __call__(self, device, value):
        getattr( device, self.method)(value)

@dataclass
class ParamProperty:
    parser: BaseParser = StringParser
    name: str | None   = None 
    required: bool = False 
    description: str = ""

    def __post_init__(self):
        self.parser = parse_parser(self.parser)

    def __set_name__(self, owner: ParamParentProtocol, name: str):
        if self.name is None:
            self.name = name 

    def __get__(self, parent: ParamParentProtocol, owner: type[ParamParentProtocol])->Any:
        if parent is None: return self
        try:
            value = parent._params_buffer[self.name]
        except KeyError:
            return None
        return self.parse_out(value)
    
    def __set__(self, parent: ParamParentProtocol, value: Any)-> None:
        if value is None:
            # setting None is equivalent to deleting the param
            parent._params_buffer.pop(self.name, None) 
        else:
            parent._params_buffer[self.name] = self.parse_in( value)
    
    def __delete__(self, parent):
        parent._params_buffer.pop(self.name, None) 

    def parse_in(self, value):
        try:
            return self.parser.parse_in(value)
        except ParsingError as err:
            raise ParsingError( f"parameter {self.name!r}: {err}") from err
    
    def parse_out(self, value):
        try:
            return self.parser.parse_out(value) 
        except ParsingError as err:
            raise ParsingError( f"parameter {self.name!r}: {err}") from err

    def get_schema(self):
        schema = self.parser.get_schema()
        if self.description:
            schema['description'] = self.description
        return schema 


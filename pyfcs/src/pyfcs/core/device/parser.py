from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, EnumMeta
from functools import partial
from typing import Any, Iterable, Optional, Type
from collections import UserList 


def enum_map(enumerator, prefix="")->dict[str,Enum]:
    map = enumerator.__members__
    if prefix:
        n = len(prefix)
        map = {name[n:]:v for name,v in map.items()}
    return map 

class ParsingError(ValueError):
    pass

class BaseParser:
    def parse_in(self, value):
        return value 
    def parse_out(self, value):
        return value 
    
    def get_schema(self):
        return {}

@dataclass 
class StringParser(BaseParser):
    minLength: int = None
    maxLength: int = None
    pattern: str = None
    format: str = None
    enum: str = None
    strict: bool = None
    def parse_in(self, value):
        if self.strict and not isinstance(value, str):
            raise ParsingError( f"expecting a string got a {type(value)} ")
        else:
            value = str(value)

        if self.enum is not None:
            if value not in self.enum:
                raise ValueError(f"not a vlid string expecting one of {', '.join(self.enum)} got {value!r}")

        if self.minLength is not None:
            if len(value)<self.minLength:
                raise ParsingError( f"the string must have a minimum size of {self.minLength} got {value!r}" )
        
        if self.maxLength is not None:
            if len(value)>self.maxLength:
                raise ParsingError( f"the string must not be exceed {self.maxLength} characters got {value!r}")

        if self.pattern is not None:
            raise RuntimeError("pattern keyword is not yet implemented")

        return value 
    
    def get_schema(self):
        schema = {'type': 'string'}
        if self.enum is not None:
            schema['enum'] = list(self.enum) 
        for param in [  "minLength", "maxLength", "format"]:
            value = getattr( self, param)
            if value is not None:
                schema[param] = value
        return schema  


@dataclass(frozen=True)
class StringMapParser(BaseParser):
    map: dict[str,Any]
     
    def __post_init__(self):
        # inverse dictionary 
        self.rmap = dict( zip( self.map.values(), self.map.keys() ))  
        
    def parse_in(self, value):
        try:
            return self.map[value]
        except KeyError:
            raise ValueError(f"value must be one of {', '.join(self.map)}, got {value}")
    
    def parse_out(self, value):
        return self.rmap[value]
    
    def get_schema(self):
        return {
                "type":  "string", 
                "enum": list(self.map)
        }


class EnumNameParser(StringMapParser):
    def __init__(self, enumerator:EnumMeta, prefix=""):
        super().__init__( enum_map( enumerator, prefix))


@dataclass
class EnumParser(BaseParser):
    enumerator: EnumMeta
    def parse_in(self, value):
        return self.enumerator(value).value 
    def parse_out(self, value):
        return self.enumerator(value)
    def get_schema(self):
        return {
            "type": "string",
            "enum": [str(e.value) for e in  self.enumerator] # force beeing a string 
        }



@dataclass
class FloatParser(BaseParser):
    minimum: Optional[float] = None
    maximum: Optional[float] = None 
    exclusiveMinimum: Optional[float] = None
    exclusiveMaximum: Optional[float] = None 
    multipleOf: Optional[float] = None

    type_ = float
    def parse_in(self, value):
        value = self.type_(value)
        if self.minimum is not None:
            if value< self.minimum:
                raise ParsingError(f"value shall be >= {self.minimum}, got {value}")
        if self.exclusiveMinimum is not None:
            if value<= self.exclusiveMinimum:
                raise ParsingError(f"value shall be > {self.exclusiveMinimum}, got {value}")

        if self.maximum is not None:
            if value> self.maximum:
                raise ParsingError(f"value shall be <= {self.maximum}, got {value}")
        
        if self.exclusiveMaximum is not None:
            if value>= self.exclusiveMaximum:
                raise ParsingError(f"value shall be < {self.exclusiveMaximum}, got {value}")
        
        if self.multipleOf is not None:
            if value%self.multipleOf:
                raise ParsingError(f"value mus be a multiple of {self.multipleOf} for {value}")

        return value 

    
    def get_schema(self):
        schema = {'type': 'number'}
        
        if self.minimum is not None:
            schema['minimum'] = self.minimum
        if self.maximum is not None:
            schema['maximum'] = self.maximum
        if self.exclusiveMaximum  is not None:
            schema['exclusiveMaximum'] = self.exclusiveMaximum
        if self.exclusiveMinimum  is not None:
            schema['exclusiveMinimum'] = self.exclusiveMinimum
        if self.multipleOf is not None:
            schema['multipleOf'] = self.multipleOf
        return schema 

@dataclass
class IntParser(FloatParser):
    minimum: Optional[int] = None
    maximum: Optional[int] = None 
    exclusiveMinimum: Optional[int] = None
    exclusiveMaximum: Optional[int] = None 
    multipleOf: Optional[int] = None

    type_ = int 
    
    def get_schema(self):
        schema = {'type': 'integer'}
        if self.minimum is not None:
            schema['minimum'] = int(self.minimum)
        if self.maximum is not None:
            schema['maximum'] = int(self.maximum)
        return schema 


class ListWithParser(UserList):
    """ A list with an item parser """
    def __init__(self, 
            initlist:Iterable|None=None, 
            item_parser: BaseParser|None=None
        ):
        self._item_parser = item_parser 
        if item_parser:
            self._parse = item_parser
        else:
            self._parse = lambda v:v 

        self.data = []
        if initlist is not None:
            self.extend( initlist )

    def __setitem__(self, i, item): self.data[i] = self._parse(item)
    def append(self, item): self.data.append(self._parse(item))
    def insert(self, i, item): self.data.insert(i, self._parse(item))
    def copy(self): return self.__class__(self, self._item_parser) 
    
    def extend(self, other):
        self.data.extend( self._parse(item) for item in  other)
            
    def __add__(self, other):
        return self.__class__(
            self.data + [self._parse(item) for item in other],
            self._item_parser
         )
    def __radd__(self, other):
        return self.__class__(
            [self._parse(item) for item in other] + self.data,
            self._item_parser
         )
    def __iadd__(self, other):
        self.data += [self._parse(item) for item in other] 
        return self

@dataclass
class ListParser(BaseParser):
    element_parser: BaseParser 
    
    def __post_init__(self):
        self.element_parser = parse_parser( self.element_parser )

    def parse_in(self, array):
        return ListWithParser( array, self.element_parser.parse_in)
    
    def get_schema(self):
        return {
            "type": "array",
            "items":  self.element_parser.get_schema()
        }



class ParserFactory:
    def __init__(self, cls, *args, **kwargs):
        self._constructor = partial(cls, *args, **kwargs)
    
    def create(self):
        return self._constructor()

# Some built in parser as short cut for ParamProperty  
built_in_parser_factories = {
    float: ParserFactory(FloatParser), 
    "float": ParserFactory(FloatParser), 
    "number": ParserFactory(FloatParser),
    int: ParserFactory(IntParser), 
    "int": ParserFactory(IntParser), 
    "integer": ParserFactory(IntParser), 
    str: ParserFactory(StringParser),
    "str": ParserFactory(StringParser),
    "string" : ParserFactory(StringParser)
}

def parse_parser( obj: Any )->BaseParser:
    """ Parse an obj as a parser instance or raise ValueError 
        
    Args: 
        obj : must be a BaseParser object or any of the following :
            __valid_parsers__
            
    Returns:
        parser: BaseParser 
    """

    if isinstance(obj, BaseParser):
        return obj 
    else:
        try:
            factory =  built_in_parser_factories[obj] 
        except KeyError:
            raise ValueError( f"{obj} is not a valid parser")
        else:
            return factory.create()

parse_parser.__doc__  = parse_parser.__doc__.replace(
    "__valid_parsers__", 
    ', '.join( repr(_e_) for _e_ in built_in_parser_factories)
)
    










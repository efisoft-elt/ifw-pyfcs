from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


from pyfcs.core.api  import ParamProperty, parser 



class Signals(str, Enum):
   DIGITAL = "DIGITAL"
   ANALOG = "ANALOG"
   INTEGER = "INTEGER"



def parse_digital_value(value: bool or str)->bool:
    """ Parse a digital payload value as python boolean """
    if isinstance(value, str):
        return value == "True"
    return bool(value)

def parse_channel_value(signal, value: str|bool|int|float)-> bool|int|float:
    if signal == Signals.DIGITAL:
        return parse_digital_value(value)
    if signal == Signals.ANALOG:
        return float(value)
    if signal == Signals.INTEGER:
        return int(value) 
    raise ValueError( f"Bug! {signal!r} is not a valid signal" )


class ChannelParser(parser.BaseParser):
    """ A parser for Single Channel definition (a dcitionary) """
    def parse_in(self, channel):
        if not isinstance( channel, dict):
            raise parser.ParsingError( f"Expecting a dictionary for channel definition got a {type(channel)}")

        try:
            signal = channel['signal']
            value = channel['value']
            name = channel['name']
        except KeyError as err:
            raise parser.ParsingError( f"missing {err} key in payload" )
        
        # let it raise an error 
        channel['signal'] = Signals( signal ).value
        channel['value'] = parse_channel_value(signal, value) 
        return channel 
    
    def get_schema(self):
        return {
                 "type": "object",
                 "properties": {
                    "name": {
                        "name": "string"
                      },
                     "signal": {
                         "type": "string",
                         "enum": ["DIGITAL","ANALOG", "INTEGER"],
                         "description": "Signal type."
                     },
                    "value": {
                        "type": ["boolean","integer","number"]
                      }
                    },
                 "required": ["name","value"],
                "additionalProperties": False
        }




class ChannelListParser(parser.BaseParser):
    channel_parser = ChannelParser() 

    def parse_in(self, channels):
        return [ self.channel_parser.parse_in(channel) for channel in channels] 
    
    def get_schema(self):
        return {
             "type": "array",
              "items": self.channel_parser.get_schema()
            }

@dataclass
class ChannelListParamProperty( ParamProperty ):
    parser: ChannelListParser = field( default_factory=ChannelListParser )
    description: str = "list of channel definitions" 
    

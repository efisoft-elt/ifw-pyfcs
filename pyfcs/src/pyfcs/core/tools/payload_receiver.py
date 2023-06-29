from __future__ import annotations

from dataclasses import dataclass

from jsonschema.exceptions import ValidationError
# import json 
import ifw.fcf.clib.json_procs as json
import jsonschema 
from ifw.fcf.clib import log

@dataclass
class PayloadReceiver:
    schema: dict | None
    
    def load_json_string(self, json_str: str)->dict:
        """ Load from a  json string and validate it agains the schema 

        Args:
            json_str (str): json string 
        Return:
            payload: payload python object    
        """
        ## remove quotes that may interfere with the parsing
        if json_str.startswith('"') and json_str.endswith('"'):
            json_str = json_str[1:-1]
        if json_str.startswith('\'') and json_str.endswith('\''):
            json_str = json_str[1:-1]
        data = json.loads( json_str )
        return self.parse(data)
    
    def load_json_file(self, file_path: str)->dict:
        """ Load from a json file and validate it agains the schema
        Args:
            file_path (str): json file path  
        Return:
            payload: payload python object  
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return self.parse( data ) 
    
    def load_spf_string(self, spf: str, devtypes: dict[str,str]):

        # TODO: Check, I think it was dropped in v5 
        param_list = spf.split(",")
        
        
        reversed_payload : dict = {} # payload organized by devtype 
        for elem in param_list:
            param, _, value = elem.partition("=")
            if not value:
                raise ValueError("wrong format, use id:key=value")
            id, _, key = param.partition(":")
            if not key:
                raise ValueError("wrong param format, use id:key format")
            id, key, value = id.strip(), key.strip(), value.strip()
            
            try:
                devtype = devtypes[id].lower()
            except KeyError:
                raise ValueError(f"device {id!r} is not managed")
            
            param: dict = reversed_payload.setdefault(devtype, {}).setdefault(id,{})
            param[key] = value 
        
        return self.load_reversed_payload( reversed_payload )
            
    def load_reversed_payload(self, reversed_payload: dict):
        payload: list = []
        for devtype, dev_payload in reversed_payload.items():
            for id,param in dev_payload.items():
                payload.append( 
                   {'id': id, 'param':{devtype: param} }
                )
        return self.parse( payload ) 
    

    def validate(self, payload):
        try:
            jsonschema.validate( instance=payload, schema=self.schema)
        except ValidationError:
            return False  
        else:
            return True

    def parse(self, payload):
        if self.schema is None:
            return payload 

        try:
            jsonschema.validate( instance=payload, schema=self.schema)
        except ValidationError as er:
            log.error(f"Given json data is Invalid: {er}")
            raise 
        else:
            log.info("Given json data Valid")

        return payload 

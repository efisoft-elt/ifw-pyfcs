""" Durty / Quick Device Setup generator. Not intended for production """
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from jinja2 import Template

MODULE = "pyfcs"


template = """
from ModFcfif.Fcfif import {{ devtype|capitalize }}Device
from ModFcfif.Fcfif import Action{{ devtype|capitalize }} 
from ModFcfif.Fcfif import DeviceUnion

{% for imp in imports %}
{{ imp }}
{% endfor %}
from {{ module }}.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['{{ devtype|capitalize }}Setup', '{{ devtype|capitalize }}Command', '{{ devtype|capitalize }}AsyncCommand']

# quick create a MalIf class 
{{ devtype|capitalize }}MalIf = create_mal_if( 
        {{ devtype|capitalize }}Device, DeviceUnion.get{{ devtype|capitalize }}, DeviceUnion.set{{ devtype|capitalize }}, 
        {% for value in values -%}
        {{ value.name }} = ( {{ value.getter }}, {{ value.setter }}),
        {% endfor %}
    )

# This device class is registered at the end of this file 
class {{ devtype|capitalize }}Setup({{ depedency }}):
    devtype = "{{ devtype|lower }}"
    MalIf = {{ devtype|capitalize }}MalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {% for param in parameters -%}
    
    {{ param.name }} = ParamProperty( {{ param.parser }},
                    description = "{{ param.description }}",
                    {% if param.required -%}
                    required = True
                    {% endif -%}
            )
    {% endfor %}
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    {% for setupfunc in setupfuncs -%}
    {% if setupfunc.setup_method -%}
    @setup_method{% endif %}
    @payload_parser({{ setupfunc.s_signature }})
    def {{ setupfunc.method }}(self, {{ setupfunc.f_signature }}):
        {% if setupfunc.valid -%}
        \"\"\" {{ setupfunc.doc }}
        \"\"\"
        {% for req in setupfunc.required -%}
        self.{{ req }} = {{ req }}
        {% endfor %} 
        {% for name, value in setupfunc.context.items() -%}
        self.{{ name }} = {{ value|tojson }} 
        {% endfor %}
        {% else -%}
        raise ValueError("un-complete payload")
        {% endif %}
    
    {% if setupfunc.payload_parser -%}
    @payload_maker({{ setupfunc.pm_signature }})
    def dump_{{ setupfunc.method }}(self):
        \"\"\" dump payload when {{ setupfunc.pm_signature }}
        \"\"\"
        return { {% for name, value in setupfunc.context.items() %}
            {{ name|tojson }} : {{ value|tojson }}, {% endfor %} 
            {% for req in setupfunc.required %}
            {{ req|tojson }} : self.{{ req }},{% endfor %}
        }
    {% endif %}
    {% endfor %}
    {% filter indent(width=4) -%}
    {{ additional_method }}
    {% endfilter %}
# register the device. This will create the Command and AsyncCommand classes  
{{ devtype|lower }}_classes = register_device( {{ devtype|capitalize }}Setup )
{{ devtype|capitalize }}Command = {{ devtype|lower }}_classes.Command 
{{ devtype|capitalize }}AsyncCommand = {{ devtype|lower }}_classes.AsyncCommand 
"""
def build_args(schema, params):
    args = [ ]
    for p in params:
        if p in schema:
            v = schema[p]
            args.append( f"{p} = {v!r}" ) 
    return args


@dataclass
class Parameter:
    name: str
    parser: str 
    description: str 
    required: bool = False
    default: Any = None
    ptype: str = ""
  
@dataclass
class Value:
    name: str
    setter: str = None 
    getter: str = None 

@dataclass
class Action:
    method: str 
    action: str
    args: dict 
    
    def __post_init__(self):
        if self.args:
            signature = [f"{p} = {v!r}" for p,v in self.args.items()]
            self.signature = ", " +  ", ".join(signature)
        else:
            self.signature = "" 


default_map = {
    "number": 0.0, 
    "integer": 0, 
    "string" : "''"
}
pytype_map = {
    "number": "float", 
    "integer": "int", 
    "string" : "str"
}

def get_value(devtype, name):
    setter = devtype.capitalize()+"Device"+".set"+name.capitalize()
    getter = devtype.capitalize()+"Device"+".get"+name.capitalize()
    if name == "posang" and devtype in ["adc", "drot"]:
        setter = devtype.capitalize()+"Device"+".setPos"
        getter = devtype.capitalize()+"Device"+".getPos"
    if name == "offset" and devtype == "drot":
        setter = "lambda d,v: 'V5 feature!'"
        getter = "lambda d,v: 0.0"
    return Value(name=name, getter=getter, setter=setter) 

def get_value(devtype, name):
    setter = "'set"+name.capitalize()+"'"
    getter = "'get"+name.capitalize()+"'"
    if name == "posang" and devtype in ["adc", "drot"]:
        setter = "'setPos'"
        getter = "'getPos'"
    if name == "offset" and devtype == "drot":
        setter = "lambda d,v: 'V5 feature!'"
        getter = "lambda d,v: 0.0"

    return Value(name=name, getter=getter, setter=setter) 
def parameter_from_schema(devtype, name, schema, required=[], imports=set()):
    type_ = schema['type']

    if name== "action" and devtype ==  "drot":
        parser =  "parser.EnumNameParser( Action"+devtype.capitalize()+", prefix='DROT_')" 
    elif name== "action" and devtype ==  "adc":
        parser =  "parser.EnumNameParser( Action"+devtype.capitalize()+", prefix='ADC_')" 

    elif name == "action":
        parser =  "parser.EnumNameParser( Action"+devtype.capitalize()+")" 
    elif name == "unit" and devtype == "motor":
        imports.add( "from ModFcfif.Fcfif import MotorPosUnit")
        parser = "parser.EnumNameParser(MotorPosUnit)" 
    elif name == "mode" and devtype == "drot":
        imports.add( "from ModFcfif.Fcfif import ModeDrot")
        parser = "parser.EnumNameParser(ModeDrot)" 
    elif name == "mode" and devtype == "adc":
        imports.add( "from ModFcfif.Fcfif import ModeAdc")
        parser = "parser.EnumNameParser(ModeAdc, prefix='ADC_')" 
    elif name== "axis" and devtype == "adc":
        imports.add( "from ModFcfif.Fcfif import AxesAdc")
        parser = "parser.EnumNameParser(AxesAdc)"

    else:
        if type_ == "string":
            args = build_args(schema,  ["enum", "minLength", "maxLength", "format"])
            parser = "parser.StringParser("+ ", ".join( args )+")"
        elif type_ == "number":
            args = build_args(schema,  ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"])
            parser = "parser.FloatParser("+ ", ".join( args )+")"
        elif type_ == "integer":
            args = build_args(schema,  ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"])
            parser = "parser.IntParser("+ ", ".join( args )+")"
        else:
            parser = "ERROR_UNKOWN_TYPE "+ type_
    
    ptype =  pytype_map.get( type_, "")
        
    return Parameter(
        name, 
        parser, 
        description=schema.get("description", None), 
        required= name in required , 
        default = default_map.get(type_,None),
        ptype = ptype
    )
        
def parameters_from_schema(devtype, properties, required=[], imports=set()):
    return [parameter_from_schema(devtype, name, schema, required, imports) for name, schema in properties.items()]

def get_values( devtype, properties):
    return [get_value(devtype, name) for name in properties]

@dataclass 
class SetupFunc:
    method: str 
    context: dict 
    required: list 
    maxProperties: int 
    minProperties: int|None = None 

    setup_method: bool = True
    doc: str = ""
    def __post_init__(self):
        self.context_str = ", ".join( f"{k}= {v!r}" for k,v in self.context.items() )
        if self.minProperties is None:
            self.minProperties =  (len(self.context)+len(self.required)) 

        if (len(self.context)+len(self.required)) >= self.minProperties:
            # self.s_signature = f"{self.context_str}, required={self.required}, maxProperties={self.maxProperties}"  
            
            self.s_signature = self.context_str 

            self.valid = True 
            self.f_signature = ", ".join( self.required )

        else:
            # self.s_signature = f"{self.context_str}, required={self.required}, minProperties={self.minProperties}"
            self.s_signature = self.context_str 

            self.setup_method = False 
            self.valid = False
            nmissing = self.minProperties- (len(self.context)+len(self.required))
            sup_args = [ f"__{i}__" for i in range(nmissing)]
            self.f_signature =  " , ".join( self.required+sup_args )+", *args"

            # self.f_signature =  "*args, "+" , ".join( self.required )
           

                
        self.action = self.context.get('action', None)
        self.payload_parser = len(self.context)>0 
        self.pm_signature =  self.context_str 
        if not self.valid:
            self.payload_parser = False 
            self.method = "_"+self.method  
        
known_setupfuncs = {
    None: {},
}
method_name_patch = {
        "off": "switch_off", 
        "on" : "switch_on", 
        "move_abs_uu": "move_abs_pos", 
        "move_rel_uu": "move_rel_pos",
        "move_by_name": "move_name_pos"
    }

additional_methods = {
    "motor":
"""
def _set_pos(self, pos_or_enc, unit):
    self.unit = unit 
    if unit == "UU":
        self.pos = pos_or_enc 
    else:
        self.enc = pos_or_enc 

@setup_method
def move_abs(self, pos_or_enc: float, unit: str ="UU"):
    \"\"\" move in absolute a motor 
    
    Args:
        pos_or_enc (float): position in user unit or encoder according to unit
        unit (str,optional): "UU" (default) or "ENC"
    \"\"\"
    self.action = "MOVE_ABS"
    self._set_pos( pos_or_enc, unit) 

@setup_method
def move_rel(self, pos_or_enc:float , unit: str ="UU"):
    \"\"\" move in relatif a motor 
    
    Args:
        pos_or_enc (float): position in user unit or encoder according to unit
        unit (str,optional): "UU" (default) or "ENC"
    \"\"\"
    self.action = "MOVE_REL"
    self._set_pos( pos_or_enc, unit) 

@setup_method
def move(self, pos_or_enc:float , type:str = "abs", unit: str ="uu"):
    \"\"\" move to a target position  
    
    Args:
        pos_or_enc (float): target position in user unit or encoder according to unit
        type (str, optional): Type of movement - absolute ("abs", default) or relative ("rel") case unsensitive
        unit (str, optional): User units ("uu") or encoders ("enc") case unsensitive

    \"\"\"
    type = type.lower()
    unit = unit.lower()
    if type == "rel":
        self.action = "MOVE_REL"
    elif type == "abs":
        self.action = "MOVE_ABS"
    else:
        raise ValueError(f"provided movement type is unknown, expecting 'rel','REL', 'abs' or 'ABS' got {type!r}" )
    if unit == "uu":
        self.unit = "UU"
        self.pos = pos_or_enc
    elif unit == "enc":
        self.unit = "ENC"
        self.enc = pos_or_enc 
    else:
        raise ValueError(f"provided unit is unknown, expecting 'uu', 'UU', 'enc' or 'ENC' got {unit!r}" )
""",

"adc": 
"""
@setup_method
def move(self, pos_or_enc:float , type:str = "abs", unit: str ="uu", aux_motor=""):
    \"\"\" move to a target position  
    
    Args:
        pos_or_enc (float): target position in user unit or encoder according to unit
        type (str, optional): Type of movement - absolute ("abs", default) or relative ("rel") case unsensitive
        unit (str, optional): User units ("uu") or encoders ("enc") case unsensitive
        aux_motor (str, optional): Auxiliar motor name : 'motor1' or 'motor2'

    \"\"\"
    type = type.lower()
    unit = unit.lower()
    if type == "rel":
        self.action = "MOVE_REL"
    elif type == "abs":
        self.action = "MOVE_ABS"
    else:
        raise ValueError(f"provided movement type is unknown, expecting 'rel','REL', 'abs' or 'ABS' got {type!r}" )
    if unit == "uu":
        self.unit = "UU"
        self.pos = pos_or_enc
    elif unit == "enc":
        self.unit = "ENC"
        self.enc = pos_or_enc 
    else:
        raise ValueError(f"provided unit is unknown, expecting 'uu', 'UU', 'enc' or 'ENC' got {unit!r}" )
    if aux_motor == "motor1":
        self.axis = "ADC1"
    elif aux_motor == "motor2":
        self.axis = "ADC2"
    else:
        raise ValueError(f"provided auxiliar motor ({aux_motor!r}) is unknown, please use either motor1 or motor2")
""",

}



def find_known_setupfunc(devtype, action_name, parameters):
    try:
        return known_setupfuncs[devtype][action_name]
    except KeyError:
        pass 
    try:
        return known_setupfuncs[None][action_name]
    except KeyError:
        pass
    
    method = action_name.lower()
    method = method_name_patch.get(method, method )


    doc = f"{method} "

    return SetupFunc(method, {'action':action_name}, [], 1, doc=doc)



def get_setup_funcs(devtype, allOf, parameters):
    funcs = [get_setup_func( devtype, context, parameters) for context in allOf] 
    return sorted( funcs, key = lambda f: len(f.context), reverse=True)

def get_setup_func(devtype, context, parameters):
    p = context['if']['properties']
    
    values = []
    methodcontext = {}

    def order(name):
        try:
            return ['action'].index(name)
        except ValueError:
            return 999

    for name  in sorted( p, key=order):
        c = p[name]
        value = c['const']
        values.append( value.lower() )
        methodcontext[name] = value 
    required = context['then'].get('required', [])
    maxProperties = context['then'].get('maxProperties', 0)
    minProperties = context['then'].get('minProperties', None)

    
    method = "_".join(values)
    method = method_name_patch.get(method, method )
    
    doc = f"{method}" 
    doc += "\n        \n        Args:\n"
    doc += " "*12+ ("\n            ".join(arg_doc(required, parameters)))
    
    return SetupFunc( method, methodcontext, required, maxProperties, minProperties=minProperties, doc=doc)
    
def arg_doc(param_names, parameters):
    docs = []
    for param_name in param_names:
        for p in parameters:
            if param_name == p.name:
                if p.ptype:
                    docs.append( f"{p.name} ({p.ptype}) : {p.description}" )
                else:
                    docs.append( f"{p.name} : {p.description}" )
                break 
        else:
            docs.append( f"{param_name} : ... ")
    return docs 


def build_from_schema( devtype, schema):
    
    action_names = schema['definitions'][devtype]['properties']['action']['enum'] 
    allOf = schema['definitions'][devtype].get('allOf', {})

    imports  = set() 
    parameters = parameters_from_schema(devtype,
                    schema['definitions'][devtype]['properties'] , 
                    schema['definitions'][devtype]['required'],
                    imports
            )
    values = get_values( devtype, schema['definitions'][devtype]['properties'] )
    if devtype == "drot":
        imports.add("from .motor import MotorSetup")
        depedency = "MotorSetup"
    else:
        depedency = "BaseDeviceSetup"

    setupfuncs = get_setup_funcs(devtype,allOf, parameters)
    for action_name in action_names:
        for setupfunc in setupfuncs:
            if action_name == setupfunc.context.get('action' ,None):
                break 
        else:
            setupfuncs.append(
                find_known_setupfunc( devtype, action_name, parameters )
            )
    

    s = Template(template).render(
        module=MODULE,
        devtype=devtype, 
        parameters= parameters, 
        values=values,  
        setupfuncs = setupfuncs, 
        imports = list(imports), 
        depedency = depedency, 
        additional_method = additional_methods.get(devtype, "")
        )
    return s


if __name__ == "__main__":
    import sys
    import json 
    
    _, devtype, file = sys.argv 
    
    with open(file) as f:
        schema = json.load(f)
        print( build_from_schema( devtype, schema ))


#     schema = {
#   "$schema": "http://json-schema.org/draft-07/schema#",
#   "definitions": {
#      "lamp": {
#       "type": "object",
#       "properties": {
#         "action": {
#           "type": "string",
#           "enum": ["ON", "OFF"],
#           "description": "Lamp action."
#         },
#         "intensity": {
#           "type": "number",
#           "minimum": 1,
#           "maximum": 100,
#           "description": "Lamp intensity."
#         },
#         "time": {
#           "type": "integer",
#           "minimum": 1,
#           "description": "Lamp timer."
#         }
#       },
#       "required": ["action"]
#     }
#   }
# }
    
#     print( build_from_schema( 'lamp', schema ))

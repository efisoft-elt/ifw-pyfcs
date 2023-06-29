from __future__ import annotations
from warnings import warn 

from dataclasses import dataclass, field
from typing import Callable, Iterable
import inspect 
from jinja2  import Template

from .device import register,  Register, get_setup_methods 
from .tools import Empty 

try:
    from docstring_parser import parse as doc_parse 
except ImportError:
    doc_parse = None

def collect_setup_methods( 
        devtype_names: Iterable | None  =None, 
        register: Register = register
     )->dict[str, list[str]]:
    """ Loock at all registered devices and collect the setup method names 
    
    setup methods are decorated with @setup_method inside the DeviceSetup declaration
    

    Args:
        devtype_names (optional, Iterable): list of devtypes 
            if not given all recorded device are taken 

    Returns:
        methods (dict):  keys are method name and values are list of devtype having the setup method 
    """
    if devtype_names is None:
        devtype_names = register.get_devtypes()

    methods = {} 
    for devtype in devtype_names:
        DeviceSetup = register.setup_class(devtype)  
        for method in get_setup_methods( DeviceSetup ):
            methods.setdefault( method, set()).add( devtype )
    return methods 

def get_setup_methods_of( devtype: str | type, register: Register )->list[str]:
    if isinstance( devtype, str):
        cls = register.setup_class(devtype)
    else:
        cls = devtype
    return get_setup_methods(cls)

def get_class_devtypes(cls):
    try:
        return cls.__devtypes__
    except AttributeError:
        return cls.__register__.get_devtypes()


class BaseMethodGenerator:
    def render(self)->tuple[str,str]:
        """ render the function. return (method name, method code)"""
        raise NotImplementedError

    def create(self)-> tuple[str,Callable]:
        """ create the method. return (method name, function) """
        loc = locals()
        name, code = self.render()
        exec( code, globals(), loc)
        return name, loc[name]

class BaseAllMethodGenerator:
    generators: list[BaseMethodGenerator] = None # to be defined in __init__ by subclass 
    
    def render_all(self) -> list[tuple[str,str]]:
        return  list( gen.render() for gen in self.generators )

    def create_all(self) -> list[tuple[str, Callable]]:
        return list( gen.create() for gen in self.generators )
    
    def populate(self, cls)->None:
        for name, method in self.create_all():
            if not hasattr(cls, name):
                setattr(cls, name, method)
        # return cls to be used as decorator 
        return cls
    
def reindent(s: str, inddentation:str ="")->str:
    if not s:
        return "" 
    lines = s.split("\n")
    first  = lines[0]
    spaces = " "*( len(first)-len(first.lstrip(" ") ) )
    new_lines = [] 
    for l in lines:
        if l.startswith(spaces):
            new_lines.append( inddentation+ l[len(spaces):] )
    return "\n".join(new_lines)
    

import re
def decompose_doc(doc):
    doc = doc.strip("\n\r ")
    short_description, _, doc = doc.partition("\n")
    
    elements  = [e.strip("\n\r") for e in  re.split(r"Args[ \t]*:[ \t]*\n", doc)]
    elements = [e for e in elements if e.strip(" \n\r")]
    if elements:
        args, *_ = elements 
    else:
        args = ''
    return short_description, args




def build_doc( method_name, valid_devtypes, register):
    """ dynamicaly build the doc """
    # TODO: Quick and durty implementation To be redone
    short_descriptions: list[str] = []
    args_list: list[str] = []
    for devtype in valid_devtypes:
        cls = register.setup_class(devtype)
        method = getattr( cls, method_name)
        doc = method.__doc__ 
        
        if doc:
            short_description, args = decompose_doc(doc)
        else:
            short_description = method_name + " "+devtype
            args = str(inspect.signature(method)).strip("()").split(",")[1:]
            args = "    "+"    ".join(args)
        if not args.strip(" \n\r"):
            args = f"{devtype}: *no further argument*"
        else:
            args = reindent(args, "    ")
            args = f"{devtype}:\n{args}\n"

        short_descriptions.append(short_description)
        args_list.append( args )
    

    description = "\n".join(short_descriptions)
    argspec = "Args:\n  all:\n    name (str): device name \n\n"
    argspec += "  "+("\n  ".join(args_list))
    doc = f""" {description} \n{argspec}\n"""
    return doc 

@dataclass 
class ArgSpec:
    name: str
    devtypes: list = field( default_factory= list) 
    atype: str|None = None 
    description: str = "" 
    is_optional: bool = False 
    def __str__(self):
        if self.devtypes:
            devtypes = "("+(", ".join(self.devtypes))+")"
        else:
            devtypes = ""

        if self.atype:
            if self.is_optional:
                atype = "("+self.atype+", optional)"
            else:
                atype = "("+self.atype+")"

        else:
            if self.is_optional:
                atype = "(optional)"
            else:
                atype = ""
        
        return f"{self.name} {atype}: {self.description} {devtypes} "


def build_doc_with_parser( method_name, valid_devtypes, register):
    short_description = ""
    args = {'devname': ArgSpec( 'devname', atype="str",description=f"Device name (Suported types: {', '.join(valid_devtypes)})") }
    for devtype in valid_devtypes:
        cls = register.setup_class(devtype) 
        method = getattr( cls, method_name)
        doc = doc_parse(  method.__doc__ )
        if doc.short_description:
            short_description = short_description or doc.short_description 
        if doc.params:
            for param in doc.params:
                name = param.arg_name.strip()
                if name in args:
                    args[name].devtypes.append( devtype) 
                else:
                    args[name] = ArgSpec( name, [devtype], param.type_name, param.description, param.is_optional)
    
    short_description = short_description + " for " + (", ".join( valid_devtypes) )

    sdoc = short_description 
    sdoc += "\n\n"
    sdoc += "Args:\n"
    sdoc += "  "+("\n  ".join( str(a) for a in args.values() ))
    return sdoc 


def check_empty(devtype, *args, **kwargs):
    for a in args:
        if a is Empty:
            raise ValueError( f"For a {devtype!r}, {a!r} cannot be empty" )
    for k,v in kwargs.items():
        if v is Empty:
            raise ValueError( f"For a {devtype!r}, {k!r} cannot be empty" )



@dataclass
class MethodSignature:
    name: str
    nargs: int 
    nposargs: int 
    arg_names: tuple[str] 
    devtype : str
    parameters: list[inspect.Parameter]
    has_empty: bool = False
    empty_args: list = field( default_factory=list) 
    
    def is_compatible_with(self, ms: MethodSignature):
        if ms.arg_names == self.arg_names and ms.nposargs == self.nposargs:
            return True, ""
        
        mpos = min( self.nargs, ms.nargs )
        if ms.arg_names[:mpos] != self.arg_names[:mpos]:
            return False, f"incompatible method argument signature, param names are different for {self.name} {self.devtype} vs {ms.devtype}:  {self.arg_names} vs {ms.arg_names} "
        
    
        if self.nposargs != ms.nposargs:
            if self.nposargs < ms.nposargs:
                left, right = self, ms 
            else:
                left, right = ms, self 
            empty_args = []
            for i in range( left.nposargs, right.nposargs):
                param = right.parameters[i]
                left.parameters.append(  inspect.Parameter( param.name, param.kind,  default=Empty) )
                right.parameters[i] = inspect.Parameter( param.name, param.kind,  default=Empty) 
                empty_args.append( param.name ) 
            left.nargs = len(left.parameters)    
            right.has_empty = True
            right.empty_args = empty_args 
        # if self.nposargs != ms.nposargs:
        #     return False, f"incompatible method argument signature, number of pos args arguments must be the same for {self.name} {self.devtype} vs {ms.devtype}: {self.nposargs} vs {ms.nposargs} " 
        return True, "" 

    @property
    def signature(self):
        return str( inspect.Signature( self.parameters )).lstrip("(").rstrip(")")
    
    @property
    def call_signature(self):
        return ", ".join(self.arg_names) 
    
    @property
    def empty_args_signature(self):
        return ", ".join( f"{a}= {a}" for  a in self.empty_args )

    def __str__(self):
        return self.call_signature

    def __hash__(self):
        return id(self)

def extract_signature(name: str, method: Callable, devtype: str)->MethodSignature:
    i = inspect.signature( method )
    parameters = list(i.parameters.values())[1:]
     
    return MethodSignature( 
                    name, 
                    len(parameters),
                     sum( [p.default == inspect._empty for p in parameters] ), 
                     tuple(p.name for p in parameters) , 
                     devtype = devtype, 
                    parameters = parameters, 
                )

def collect_signatures(method_name: str, valid_devtypes: list[str], register: Register)->tuple[str, dict[tuple,str]]:
    """ Collect signatures for a method and a list of devtypes 

    The idea is to conserve as much as possible the signature for the built method. 
    - If all method signature are the same, it is conserved 
    - If they are not compatible the method signature will be (*arg, **kwargs)
    
    This is to conserve the Cli Client functionality as much as possible. 

    Outputs:
        method_signature (str): the method signature without the "self, devname," prefix
        call_signatures (dict): Dictionary of tuple of devtypes as key and claa signature as value.
    """
    signatures: list[MethodSignature] = []
    
    # any failure of conserving signature will send this default 
    default = ("*args, **kwargs", {tuple(valid_devtypes):"*args, **kwargs"})

    # extract all method signature 
    for devtype in valid_devtypes:
        cls = register.setup_class(devtype)
        method = getattr( cls, method_name)
        signatures.append(  extract_signature(method_name, method, devtype ) )
    
    if not signatures:
         return "", { tuple(valid_devtypes):""} 

    # Check signature compatibility 
    # If not compatible the built method will be (self, name, *args, **kwargs)
    # and setup called as .setup( *args, **kwargs )

    collection: dict[str, tuple] = {}
    # method_signature: MethodSignature = None
    method_signature: MethodSignature = signatures[0] 

    for i,sig in enumerate( signatures) :
        for other in signatures[i+1:]:
            compatible, raison = sig.is_compatible_with( other )
            if not compatible:
                warn( raison, UserWarning )
                return  default 

            # keep the one with th emaximum of argument  
            if sig.nargs>= other.nargs:
                method_signature = sig 
            else:
                method_signature = other 
        collection.setdefault( sig, []).append( sig.devtype )

    
    # Try if the signature works. If it does not send the default  
    try:
        exec( "def _("+method_signature.signature+"):...") 
    except (SyntaxError, NameError):
        warn(
            f"Warning problem with method {method_name} signature : {method_signature.signature}", 
            UserWarning
        )
        return default 

    return method_signature.signature, { tuple(devtype): sig for sig,devtype in collection.items()}


@dataclass
class CommandMethodGenerator(BaseMethodGenerator):
    method_name: str 
    valid_devtypes: list[str]
    prefix: str = ""
    register: Register = register 
    template = Template(
"""
def {{ prefix }}{{ new_method_name }}(self, devname: str, {{ method_signature }})->None:
    \"\"\"{{ doc }}
    \"\"\"
    devtype = self.get_devtype(devname)
    devtype = devtype.lower()
    DeviceSetup = self.__register__.setup_class(devtype) 
    device_setup = DeviceSetup( self.interface, devname )

    {% for devtypes, signature in signatures[:1] -%}
    if devtype in {{ devtypes }}:
        {% if signature.has_empty -%}
        check_empty(devtype,  {{ signature.empty_args_signature }} )
        {% endif -%}
        device_setup.{{ method_name }}( {{ signature.call_signature }} )
    {% endfor %}
    {% for devtypes, signature in signatures[1:] -%} 
    elif devtype in {{ devtypes }}:
        {% if signature.has_empty -%}
        check_empty(devtype,  {{ signature.empty_args_signature }} )
        {% endif -%}
        device_setup.{{ method_name }}( {{ signature.call_signature }} )
    {% endfor %}
    else:
        raise ValueError(f"Function available only for {', '.join({{ valid_devtypes }})}. got a {devtype!r}")

    return device_setup.setup()
""")
    def build_doc(self)->str:
        """ dynamicaly build the doc """
        # TODO: Quick and durty implementation To be redoe
        if doc_parse:
            return build_doc_with_parser( self.method_name, self.valid_devtypes, self.register) 
        else:
            return build_doc( self.method_name, self.valid_devtypes, self.register)

    def render(self) -> tuple[str,str]:
        valid_devtypes = tuple( devtype.lower() for devtype in self.valid_devtypes)
        # valid_devtypes = self.valid_devtypes
        method_signature, signatures = collect_signatures(self.method_name, self.valid_devtypes, self.register)
        code = self.template.render(
            prefix =self.prefix, 
            doc = self.build_doc(),
            new_method_name=self.method_name,
            method_name=self.method_name, 
            valid_devtypes= valid_devtypes, 
            method_signature = method_signature, 
            signatures = list(signatures.items())
        )
        # if self.method_name == "move":
        #     print( code )
        # print( code ) 
        return self.method_name, code
    


class AllCommandMethodGenerator(BaseAllMethodGenerator):
    def __init__(self, devtype_names: Iterable | None  =None, register: Register = register):
        method_collection = collect_setup_methods( devtype_names, register )
        self.generators = [CommandMethodGenerator(*item, register=register) for item in method_collection.items()]
    
    @classmethod
    def static_populate(thisclass, cls):
        generator = thisclass( get_class_devtypes(cls), cls.__register__ )
        generator.populate( cls) 
        return cls 


@dataclass
class AsyncCommandMethodGenerator(CommandMethodGenerator):
    method_name: str 
    valid_devtypes: list[str]
    prefix: str = ""
    register: Register = register 
    template = Template(
"""
async def {{ prefix }}{{ new_method_name }}(self, devname: str, {{ method_signature }})->None:
    \"\"\"{{ doc }}
    \"\"\"
    devtype = await self.get_devtype(devname)
    devtype = devtype.lower()
    
    DeviceSetup = self.__register__.setup_class(devtype) 
    device_setup = DeviceSetup( self.interface, devname)
    
    {% for devtypes, signature in signatures[:1] -%}
    if devtype in {{ devtypes }}:
        {% if signature.has_empty -%}
        check_empty(devtype,  {{ signature.empty_args_signature }} )
        {% endif -%}
        device_setup.{{ method_name }}( {{ signature.call_signature }} )
    {% endfor %}
    {% for devtypes, signature in signatures[1:] -%} 
    elif devtype in {{ devtypes }}:
        {% if signature.has_empty -%}
        check_empty(devtype,  {{ signature.empty_args_signature }} )
        {% endif -%}
        device_setup.{{ method_name }}( {{ signature.call_signature }} )
    {% endfor %}
    else:
        raise ValueError(f"Function available only for {', '.join({{ valid_devtypes }})}. got a {devtype!r}")
    
    return await device_setup.async_setup()
""")

class AllAsyncCommandMethodGenerator(BaseAllMethodGenerator):
    def __init__(self, devtype_names: Iterable | None  =None,  register: Register = register):
        
        method_collection = collect_setup_methods( devtype_names, register )
        self.generators = [AsyncCommandMethodGenerator(*item, register=register) for item in method_collection.items()]
    
    @classmethod
    def static_populate(thisclass, cls):
        generator = thisclass( get_class_devtypes(cls), cls.__register__ )
        generator.populate( cls) 
        return cls 



@dataclass 
class SetupMethodGenerator(BaseMethodGenerator):
    method_name: str 
    devtype: str 

    template = Template(
"""
def {{ new_method_name }}(self, name, *args, **kwargs)->None:
    return self.get(name, '{{ devtype }}').{{ method_name }}( *args, **kwargs)
"""
)
    def render(self) -> tuple[str,str]:
        new_method_name =  f"add_{self.devtype}_{self.method_name}"
        code = self.template.render( 
            new_method_name=new_method_name,
            method_name=self.method_name, 
            devtype=self.devtype, 
        )
        return new_method_name, code
    
class AllSetupMethodGenerator(BaseAllMethodGenerator):
    def __init__(self, devtype_names: Iterable | None  =None,  register: Register = register):

        method_collection = collect_setup_methods( devtype_names, register )
        self.generators = [SetupMethodGenerator(m,dt) for m,lst in method_collection.items() for dt in lst]
    
    @classmethod
    def static_populate(thisclass, cls):
        generator = thisclass( get_class_devtypes(cls), cls.__register__ )
        generator.populate( cls) 
        return cls 

@dataclass
class DeviceCommandGenerator(BaseMethodGenerator):
    method_name: str 
    # -------------
    template = Template( 
"""
def {{ method_name }}(self, *args, **kwargs)->None:
    dev_setup = self.Setup( self.interface, self.id ) 
    dev_setup.{{ method_name }}( *args, **kwargs)
    return dev_setup.setup()
"""
    )
    def render(self) -> tuple[str,str]:
        code = self.template.render( 
            method_name=self.method_name,
        )
        return self.method_name, code 

class AllDeviceCommandGenerator(BaseAllMethodGenerator):
    def __init__(self, devtype:  type,  register: Register = register):

        self.generators = [DeviceCommandGenerator(method) for method in get_setup_methods(devtype)]
    
    @classmethod
    def static_populate(thisclass, cls):
        Setup = cls.Setup
        generator = thisclass( Setup)
        generator.populate( cls) 
        return cls 




@dataclass
class DeviceAsyncCommandGenerator(BaseMethodGenerator):
    method_name: str 
    # -------------
    template = Template( 
"""
async def {{ method_name }}(self, *args, **kwargs)->None:
    dev_setup = self.Setup( self.interface, self.id ) 
    dev_setup.{{ method_name }}( *args, **kwargs)
    return await dev_setup.async_setup()
"""
    )
    def render(self) -> tuple[str,str]:
        code = self.template.render( 
            method_name=self.method_name,
        )
        return self.method_name, code 

class AllDeviceAsyncCommandGenerator(BaseAllMethodGenerator):
    def __init__(self, devtype: str | type):
        self.generators = [DeviceAsyncCommandGenerator(method) for method in get_setup_methods(devtype)]
    
    @classmethod
    def static_populate(thisclass, cls):
        Setup = cls.Setup
        generator = thisclass( Setup )
        generator.populate( cls) 
        return cls 


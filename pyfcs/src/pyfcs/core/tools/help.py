from inspect import signature, Signature , Parameter 
from typing import Callable

from .empty import Empty 

try:
    from docstring_parser import parse
except:
    parse = None


def func_help(name, method: Callable):
    help_str = []
    # cleanup parameters from annotations 
    parameters = [ Parameter( p.name, p.kind, default=p.default) for p in signature(method).parameters.values() ]
    sig = str( Signature(  parameters[1:] ) ) # remove the first one which is an obj instance (probably self) 
    sig = sig.lstrip('(')
    sig = sig.rstrip(')')
    
    default_params = [p.name for p in parameters if p.default is Empty]

    if parse is not None:
        parsed_doc = parse(method.__doc__)
        
        help_str.append(f"Short description: {parsed_doc.short_description}")
        help_str.append(f"Command usage: {name} {sig}")
        help_str.append("where:")
        for obj in parsed_doc.params:
            type_name = f"({obj.type_name})" if obj.type_name else ""
            if obj.is_optional or obj.arg_name.strip() in default_params:
                help_str.append(f"\t[{obj.arg_name.strip()}{type_name}]: \t{obj.description.lstrip(' ')}")
            else:
                help_str.append(f"\t<{obj.arg_name.strip()}{type_name}>: \t{obj.description.lstrip(' ')}")
    else:
        help_str.append(f"Command usage: {name} {sig}")
        help_str.append(f"Description:")
        help_str.append(method.__doc__)
    
    return help_str


def class_help(cls: type, func: str =None):
    help_str = []
    if func is None:
        help_str.append("Available command list:")
        for i in dir(cls):
            if not i.startswith("_"):
                help_str.append(f" - {i}")
    else:
        help_str = func_help(func, getattr(cls, func))

    reply = '\n'.join(help_str)
    return reply

import inspect 
def method_class_metadata(cls):
    options = dict()
    methods = []
    method_list = dir(cls)
    for method in method_list:
        if not method.startswith("_"):
            available_methods = getattr(cls, method)
            try:
                args = inspect.getfullargspec(available_methods).args
            except TypeError:
                continue
            if parse is not None:
                parsed_doc = parse(available_methods.__doc__)
                print("AAAAAAAAAAAAAAAAAAAAAAAA", method, args[1:],   parsed_doc.params )
                options[method] = {
                    "options": "" if parsed_doc.params is None else list(
                        map(
                            lambda d: {
                                "flag": d[1],
                                "meta": "" if not parsed_doc.params else
                                (parsed_doc.params[d[0]].description).lstrip(" "),
                            },
                            enumerate(args[1:]),
                        )
                    ),
                    "meta": parsed_doc.short_description,
                    "returns": parsed_doc.returns.type_name if parsed_doc.returns
                    else None,
                }
    return options

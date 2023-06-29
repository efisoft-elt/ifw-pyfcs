from __future__ import annotations

from dataclasses import dataclass, field
import traceback 
import functools
from io import StringIO
from typing import Any, Callable, Coroutine
from pymalcpp import MalException
from elt import pymal 

from ifw.fcf.clib import log

from ..define import ClientInterfacer, ClientKind
from ..tools import cash_property

@dataclass 
class Command:
    """ Command class to execute a Cii client command 
    
    The execution of command is within a context manager and allows 
    the  good logging of any execution errors.

    Args:
        interface: Interface with a .get_client(client_kind) method 
        client_kind (str): Client type, e.g. : "Std", "Daq", "App"
        method_name (str): Method name to be executed, e.g. "Init"
        callback (optional, Callable): A callback method with signature f(err)
            where ``err`` is None in case of success or is an exception instance 
            in case of error 

    Exemple::

        from pyfcs.core.api import ConsulInterface, Command 
        fcs2_if = ConsulInterface('fcs2-req')
        with Command(fcs2_if, 'Std', 'Init') as init:
            init()
        
    This is equivalent of doing: 

        with fcs2_if.command( 'Std', 'Init') as init:
            init()

    Within asynchronious function `async with` keywords will return an asynch function::

        async def my_init():
            async with fcs2_if.command( 'Std', 'Init') as async_init:
                wait async_init()

    """
    interface: ClientInterfacer
    client_kind: ClientKind
    method_name: str 
    callback: Callable|None = None
     
    
    
    def log_error(self, exc_type, exc_val, exc_tb): # see __exit__ for arguments 
        """ log execution error of the command """
        method_info = f"{self.method_name} on {self.client_kind} interface" 

        if isinstance(exc_val, MalException):
            if hasattr(exc_val, 'getDesc'): # some Mal Exception does not have getDesc 
                log.error(f"Got exception from command {method_info}:\n      {exc_val.getDesc()}")
            else:
                log.error(f"Got exception from command {method_info}") 
        elif isinstance(exc_val,pymal.TimeoutException):
            log.error(f"Got a timeout exception from command {method_info} after {self.interface.timeout} [ms]")
        else:
            log.error(f"Got an exception when handling command {method_info}:\n      {exc_val}")
            # print the tracback inside the log debug, maybe adjust the limits  
            output = StringIO()
            traceback.print_tb( exc_tb, None, output)
            log.debug( output.getvalue() )
                
    

    @cash_property
    def method(self)->Callable:
        client = self.interface.get_client(self.client_kind, asynchronous=False)
        method =  getattr(client, self.method_name)
        return method        
            
    @cash_property
    def async_method(self)->Coroutine:
        client = self.interface.get_client(self.client_kind, asynchronous=True)
        raw_method = getattr(client, self.method_name)
        async def wrapped_async_method(*args, **kwargs):
            return await raw_method(*args, **kwargs).create_future()
        return wrapped_async_method

    def __enter__(self):
        return self.method 
    
    async def __aenter__(self):
        return self.async_method
    
    def __exit__(self, exc_type, exc_val, exc_tb ):
        if exc_type:
            self.log_error(exc_type,  exc_val, exc_tb)
        
        if self.callback:
            self.callback(exc_val) 
        
    async def __aexit__(self, exc_type, exc_val, exc_tb ):
        if exc_type:
            self.log_error(exc_type,  exc_val, exc_tb)
        
        if self.callback:
            self.callback(exc_val) 
                                                                   
    def exec(self, *args, **kwargs):
        with self as func:
            return func(*args, **kwargs)

    async def async_exec(self, *args, **kwargs):
        async with self as coroutine:
            return await coroutine(*args, **kwargs)
    
    def partial(self, *args, **kwargs)->CommandWithArgs:
        """ Return a command object with partial method argument set """
        return CommandWithArgs( 
                self.interface, 
                self.client_kind, 
                self.method_name, 
                self.callback,
                args, kwargs               
            )

class DummyCommand(Command):
    def method(self, *args, **kwargs):
        print(f"Dummy method {self.client_kind}, {self.method_name} called with arguments args={args}, kwargs={kwargs}")
        return ""

    async def async_method(self, *args, **kwargs):
        print(f"Dummy Async method {self.client_kind}, {self.method_name} called with arguments args={args}, kwargs={kwargs}")
        return ""



@dataclass
class CommandWithArgs(Command):
    """ A Mal client command object with some arguments 
    
    Mostly, this object is created from the partial method of a Command object. 

    Exemple::

        interface.command( 'Std', 'Init').partial( ['lamp1', 'lamp2' ]) 
        
    """
    args: tuple = field( default_factory=tuple)
    kwargs: dict[str,Any] = field( default_factory=dict) 
    
    @cash_property
    def method(self):
        return functools.partial(super().method, *self.args, **self.kwargs) 

    @cash_property
    def async_method(self):
        return functools.partial(super().async_method, *self.args, **self.kwargs) 

    def partial(self, *args, **kwargs):
        return CommandWithArgs( 
                self.interface, 
                self.client_kind, 
                self.method_name, 
                self.callback,
                self.args+ args, {**self.kwargs, **kwargs}               
            )


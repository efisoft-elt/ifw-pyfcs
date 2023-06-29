from __future__ import annotations
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Coroutine, Iterator
from typing_extensions import Protocol

import asyncio

from ModFcfif.Fcfif import ExceptionErr as AppExceptionErr
from ModFcfif.Fcfif import VectorfcfifSetupElem
from elt.pymal import TimeoutException
from ifw.fcf.clib import log


from ..define import  ClientInterfacer, BufferGetter, SetupMember
from .command import Command 



@dataclass
class SetupCommand: # must be compliant to CommandExecutor Protocol 
    """ Object holding a setup to execute it 
    
    Args:
        interface : interface object with the .command(client_kind, method_name) method 
        setup: Object holding a buffer. Must have the .get_buffer() method 
        callback (optional, callable): A callback called after setup with signature f(exc)
            where exc is None or a raised exception
    """
    interface: ClientInterfacer
    setup: BufferGetter
    callback: Callable | None = None
    
    def __post_init__(self):
        self._setup_command = self.interface.command('App', 'Setup', callback=self.callback)

    @property 
    def method(self)->Callable:
        return partial( self._setup_command.method, self.get_buffer() )

    @property 
    def async_method(self)->Coroutine:
        return partial( self._setup_command.async_method, self.get_buffer())

    def __enter__(self):
        return self.method 
    
    def __exit__(self, exc_type, exc_val, exc_tb ):
        return self._setup_command.__exit__(exc_type, exc_val, exc_tb)
    
    async def __aenter__(self):
        return self.async_method 

    async def __aexit__(self, exc_type, exc_val, exc_tb ):
        return await self._setup_command.__aexit__(exc_type, exc_val, exc_tb)

    def get_buffer(self)->VectorfcfifSetupElem:
        """ Return the buffer of this SetupCommand """
        return self.setup.get_buffer()

    def exec(self)->str:
        """ Execute the stored setup right now """
        buffer = self.get_buffer()
        with self._setup_command as cmd:
            reply = cmd( buffer )
        return reply 

    async def async_exec(self)->str:
        """ Execute Asynchroniously the stored setup """
        buffer = self.get_buffer()
        async with self._setup_command as acmd:
            reply = await acmd( buffer )
        return reply 


@dataclass
class SetupCommandGroup:
    setups : list[SetupMember]

    _setup_dict: dict[ClientInterfacer,list[BufferGetter]] = None
    
    def __post_init__(self):
        # check setups objects 
        for setup in self.setups:
            assert isinstance( setup, SetupMember)

        self._setup_dict = self._colect_by_interface()
    
    def __iter__(self)->Iterator[SetupMember]:
        return self.setups.__iter__()


    def _flat_setup_list(self)->list[SetupMember]:
        """ build and return a flat list of Setups  """
        flat_list = [] 
        for setup in self.setups:
            if hasattr( setup, "__iter__"):
                flat_list.extend(setup)
            else:
                flat_list.append(setup) 
        return flat_list

    def _colect_by_interface(self)->dict[ClientInterfacer,list[BufferGetter]]:
        setup_dict = {}
        for setup in self._flat_setup_list():
            setup_dict.setdefault( setup.interface, []).append(setup)
        return setup_dict
    
    def exec(self):
        replies = {}
        for interface, setups in self._setup_dict.items():
            buffer = VectorfcfifSetupElem()

            for setup in setups:
                buffer.extend( setup.get_buffer() )
            replies[interface] = SetupCommand(interface, buffer).exec()

    async def async_exec(self):
        coroutines = []
        for interface, setups in self._setup_dict.items():
            buffer = VectorfcfifSetupElem()
            for setup in setups:
                buffer.extend( setup.get_buffer() )
            coroutines.append( SetupCommand(interface, buffer).async_exec() )

        return await asyncio.gather( *coroutines )
    
    def log_error(self,  exc_type, exc_val, exc_tb):
        return Command.log_error(self, exc_type, exc_val, exc_tb)


    def __enter__(self):
        return self.exec
     
    async def __aenter__(self):
        return self.async_exec
    

    def __exit__(self, exc_type, exc_val, exc_tb ):
        if exc_type:
            self.log_error(exc_type,  exc_val, exc_tb)
        
         
    async def __aexit__(self, exc_type, exc_val, exc_tb ):
        if exc_type:
            self.log_error(exc_type,  exc_val, exc_tb)
        

    

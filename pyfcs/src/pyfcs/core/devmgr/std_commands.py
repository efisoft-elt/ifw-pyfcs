from __future__ import annotations
from dataclasses import dataclass
from pyfcs.core.define import  ClientInterfacer


@dataclass
class StdCommands:
    interface: ClientInterfacer

    def state(self)->str:
        """ Execute GetState command - Std Interface """
        with self.interface.command('Std', 'GetState') as state:
            return state()


    def status(self)->str:
        """ Execute GetStatus command - Std Interface """
        with self.interface.command('Std', 'GetStatus') as status:
            return status()


    def init(self)->str:
        """ Execute Init command - Std Interface """
        with self.interface.command('Std', 'Init') as init:
            return init()


    def enable(self)->str:
        """ Execute Enable command - Std Interface """
        with self.interface.command('Std', 'Enable') as enable:
            return enable()


    def disable(self)->str:
        """ Execute Disable command - Std Interface """
        with self.interface.command('Std', 'Disable') as disable:
            return disable()


    def reset(self)->str:
        """ Execute Reset command - Std Interface """
        with self.interface.command('Std', 'Reset') as reset:
            return reset()


    def stop(self)->str:
        """ Execute Stop command - Std Interface """
        with self.interface.command('Std', 'Stop') as stop:
            return stop() 


@dataclass
class StdAsyncCommands:
    interface: ClientInterfacer

    async def state(self)->str:
        """ Async Execute GetState command - Std Interface """
        async with self.interface.command('Std', 'GetState') as astate:
            return await astate()


    async def status(self)->str:
        """ Async Execute GetStatus command - Std Interface """
        async with self.interface.command('Std', 'GetStatus') as astatus:
            return await astatus()


    async def init(self)->str:
        """ Async Execute Init command - Std Interface """
        async with self.interface.command('Std', 'Init') as ainit:
            return await ainit()


    async def enable(self)->str:
        """ Async Execute Enable command - Std Interface """
        async with self.interface.command('Std', 'Enable') as aenable:
            return await aenable()


    async def disable(self)->str:
        """ Async Execute Disable command - Std Interface """
        async with self.interface.command('Std', 'Disable') as adisable:
            return await adisable()


    async def reset(self)->str:
        """ Async Execute Reset command - Std Interface """
        async with self.interface.command('Std', 'Reset') as areset:
            return await areset()


    async def stop(self)->str:
        """ Async Execute Stop command - Std Interface """
        async with self.interface.command('Std', 'Stop') as astop:
            return await astop()
   

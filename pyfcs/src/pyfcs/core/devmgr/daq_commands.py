from __future__ import annotations
from dataclasses import dataclass

from pyfcs.core.define import ClientInterfacer
    

@dataclass
class DaqCommands:
    """  A collection of synchronous call for Metadaq interface  """ 
    interface: ClientInterfacer 

    def startdaq(self, id: str)->str:
        """ Execute StartDaq command - Metadaq Interface  """
        with self.interface.command('Daq','StartDaq') as startdaq:
            return startdaq(id).GetId()
    
    def stopdaq(self, id: str)->str:
        """ Execute StopDaq command - Metadaq Interface  """
        with self.interface.command('Daq','StopDaq') as stopdaq:
            return _stopdaq_wrap_reply( stopdaq(id)) 
    
    def abortdaq(self, id: str)->str:
        """ Execute AbortDaq command - Metadaq Interface """
        with self.interface.command('Daq','AbortDaq') as abortdaq:
            return abortdaq(id).GetId()
    
    def daqstatus(self, id: str)->str:
        """ Execute  GetDaqStatus command - Metadaq Interface """
        with  self.interface.command('Daq','GetDaqStatus') as get_daqstatus:
            return _daqstatus_wrap_reply( get_daqstatus(id) )

@dataclass
class DaqAsyncCommands:
    """   A collection of asynchronous call for Metadaq interface   """ 
    interface: ClientInterfacer 

    async def startdaq(self, id: str)->str:
        """ Async Execute StartDaq command - Metadaq Interface  """
        async with self.interface.command('Daq','StartDaq') as astartdaq:
            return (await astartdaq(id)).GetId()
    
    async def stopdaq(self, id: str)->str:
        """ Async Execute StopDaq command - Metadaq Interface  """
        async with self.interface.command('Daq','StopDaq') as astopdaq:
            return _stopdaq_wrap_reply(await astopdaq(id)) 
    
    async def abortdaq(self, id: str)->str:
        """ Async Execute AbortDaq command - Metadaq Interface """
        async with self.interface.command('Daq','AbortDaq') as aabortdaq:
            return (await aabortdaq(id)).GetId()
    
    async def daqstatus(self, id: str)->str:
        """ Async Execute  GetDaqStatus command - Metadaq Interface """
        async with  self.interface.command('Daq','GetDaqStatus') as adaqstatus:
            return _daqstatus_wrap_reply( await adaqstatus(id) )



# #####################################################################3


def _stopdaq_wrap_reply(daqobj)->str:
    reply = [
            f"id: {daqobj.getId()}",  
            f"files: {daqobj.getFiles()}",  
            f"keywords: {daqobj.getKeywords()}",
        ]
    return '\n'.join(reply)

def _daqstatus_wrap_reply( daqobj):
    reply = [
            f"id: {daqobj.getId()}",  
            f"state: {daqobj.getState()}", 
            f"files: {daqobj.getFiles()}",  
            f"keywords: {daqobj.getKeywords()}",
        ]
    return '\n'.join(reply)



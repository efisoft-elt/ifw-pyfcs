from __future__ import annotations
import asyncio
from dataclasses import dataclass
import json
from typing import Any, Callable 
import re
import time

from pyfcs.core.define import ClientInterfacer

def _parse_value(v):
    # use json loader to convert values 
    # if failed we can assume it is a string 
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        v = v.strip()
        return v.lstrip("'").rstrip("'") 



def status_list_to_dict(status):
    output = {} 
    for line in status:
        key,_, value = line.partition(" = ")
        if value:
            output[key] = _parse_value(value) 
    return output 


class EmptyDefault:
    pass

class StatusHandler:
    """ Handy tool to manage status information as returned by App/DevStatus Command 

    Exemple:: 

        from pyfcs.core.api import StatusHandler
        
        sh = StatusHandler([ 'lamp1.lcs.state = Operational', 
                            'lamp1.lcs.substate = Off', 
                            'lamp1.lcs.intensity = 0.0', 
                            'lamp2.lcs.state = Operational', 
                            'lamp2.lcs.substate = Off', 
                            'lamp2.lcs.intensity = 0.0'])        


        assert sh.lamp1.lcs.substate == 'Off'
        assert sh.get( 'lamp1.lcs.substate') == 'Off'
        
        # sh.lamp1 return a setup restricted to lamp1 value, 
        # the lamp1 prefix is removed 
        assert type(sh) is type(sh.lamp1)
    
        substates = sh.restricted('lcs.substate')
        assert substates.lamp1 == 'Off'
        assert substates.lamp2 == 'Off'

    """
    def __init__(self, status: list[str]| dict[str,Any]):
        if isinstance( status, dict):
            self._status = status
        elif isinstance( status, str):
            self._status = status_list_to_dict( status.split("\n") )
        else:
            self._status = status_list_to_dict( status )
    
    def __getitem__(self, item):
        return self._status[item]
    
    def __setitem__(self,item , value):
        self._status[item] = value 

    def __delitem__(self, item):
        del self._status[item]

    def __getattr__(self, attr):
        if attr in self._status:
            return self._status[attr] 
        
        new_status = {}
        dattr = attr+"."
        lattr = len(dattr)
        for key,value in self._status.items():
            if key.startswith( dattr):
                new_status[ key[lattr:] ] = value 
        if not new_status:
            raise AttributeError( f'{attr!r}')
        return self.__class__(new_status) 
    
    def __iter__(self):
        for key,value in self._status.items():
            if value is '':
                yield f"{key} = ''"
            else:
                yield f"{key} = {value}"
    
    def __repr__(self):
        return self.__class__.__name__+"("+repr(list(self))+")"

    def __str__(self):
        return "\n".join( self )
    
    def __len__(self):
        return len(self._status) 

    def values(self):
        for value in self._status.values():
            yield value 

    def keys( self):
        for keys in self._status.keys():
            yield keys 
    
    def items( self):
        for items in self._status.items():
            yield items 

    def get(self, key, default=EmptyDefault):
        """ Return value matching a key 

        If the key is not found and a default is given return the default 
        else raise a KeyError 

        Args:
            key (str)
            default (optional, Any) 

        Returns:
            value (Any) 
        Raises:
            KeyError : if key not found and no default provided 
        """
        try:
            return self._status[key]
        except KeyError:
            if default is EmptyDefault:
                raise 
            else:
                return default 

    def filtered(self, pattern: str, on_values: bool = False)->StatusHandler:
        """ Filter the status bufffer with a regexp pattern applied on keys 

        Args:
            pattern (str): Regular Expression pattern to match 
            on_values (optional, bool): If True the search pattern is applied 
                on string values instead of keys. Non-string values are than 
                excluded of result 

        Returns:
            new_status_handler (StatusHandler): filtered status handler  
        """

        status = {}
        if on_values:
            for key,value in self._status.items():
                if isinstance( value, str) and re.search( pattern, value):
                    status[key] = value 
        else:
            for key,value in self._status.items():
                if re.search( pattern, key):
                    status[key] = value 
        return self.__class__( status )
    
    def restricted(self, key_suffx):
        """ Filter the status buffer with a given key suffix 
        
        For all match the key suffix is removed from the created status buffer 
        
        Args:
            key_suffix (str): Suffix to be match. does not need to start with "." 
        
        Returns:
            new_status_handler (StatusHandler): status_handler with matching keys

        Example::

            > sh = StatusHandler( ['lamp1.lcs.state = Operational','lamp2.lcs.state = Operational']) 
            > sh.restricted( 'lcs.state' )
            StatusHandler(['lamp1 = Operational', 'lamp2 = Operational'])

        """
        output = {}
        dkey_suffix = "."+key_suffx.lstrip(".")
        n = len(dkey_suffix)
        for key, value in self._status.items():
            if key == key_suffx:
                return ScalarStatus( key, value)
            if key.endswith( dkey_suffix):
                output[ key[:-n] ] = value 
        return self.__class__( output )

@dataclass
class ScalarStatus:
    key: str 
    value: Any


@dataclass
class StatusChecker:
    interface: ClientInterfacer
    key: str 
    value: Any
    operator: Callable = all
    def __post_init__(self):
        self.status_cmd = self.interface.command( 'App', 'DevStatus')
        if hasattr( self.value , "__call__"):
            self.check_value = self.value 
        else:
            self.check_value = lambda v: self.value == v 

    def check(self, *devnames):
        with self.status_cmd as devstatus:
            sh = StatusHandler( devstatus(devnames)).restricted(self.key)
        return self.operator( self.check_value(v) for v in sh.values() ) 
    
    async def async_check(self, *devnames):
        async with self.status_cmd as adevstatus:
            status = await adevstatus(devnames)
            sh  = StatusHandler(status).restricted(self.key)
        return self.operator( self.check_value(v) for v in sh.values() ) 




@dataclass
class StatusWaiter:
    interface: ClientInterfacer
    key: str 
    value: Any| Callable
    timeout: int = 60000
    period: int = 500
    operator: Callable = all

    def __post_init__(self):
        self.status_cmd = self.interface.command('App', 'DevStatus') 
        if hasattr( self.value , "__call__"):
            self.check_value = self.value 
        else:
            self.check_value = lambda v: self.value == v 


    def wait(self, *devnames):
        tic = time.time()
        period_sec = self.period / 1000.
        timeout_sec = self.timeout / 1000.
        while True:
            with self.status_cmd as devstatus:
                sh = StatusHandler( devstatus(devnames)).restricted(self.key)
            if self._check(sh):
                return time.time()-tic 
            time.sleep( period_sec  )
            tac = time.time()
            if (tac-tic)>timeout_sec:
                raise RuntimeError(f"Timeout of wait for {self.key}={self.value} on {devnames} after {self.timeout}ms")

    async def async_wait(self, *devnames):
        tic = time.time()
        period_sec = self.period / 1000.
        timeout_sec = self.timeout / 1000.
        while True:
            async with self.status_cmd as adevstatus:
                status = await adevstatus(devnames)
                sh = StatusHandler( status ).restricted(self.key)

            if self._check(sh):
                return time.time()-tic 
            await asyncio.sleep( period_sec  )
            tac = time.time()
            if (tac-tic)>timeout_sec:
                raise RuntimeError(f"Timeout of wait for {self.key}={self.value} on {devnames} after {self.timeout}ms")

    def _check(self, sh: StatusHandler)->bool:
        if not sh:
            raise ValueError( f"Nothing to wait for key suffix: {self.key!r} " )
        if isinstance( sh, ScalarStatus):
            return self.check_value( sh.value)

        return self.operator( self.check_value(v) for v in sh.values() ) 

from __future__ import annotations
from dataclasses import dataclass
from pyfcs.core.define import ClientInterfacer


@dataclass
class DevicesAppCommands:
    """ A set of App commands for one or several devices """  
    interface: ClientInterfacer

    def _get_devnames(self):
        raise NotImplementedError("_get_devnames")
     
    def devstatus(self)->list[str]:
        """ Executes a DevStatus Command  
        
        Return results in a list of string  
        """
        with self.interface.command('App', 'DevStatus') as get_status:
            return get_status( self.get_devnames() ).split("\n")
   
   
    # ~~~~~~~~~~ autogen ~~~~~~~~~~~~~~~~~

    def ignore(self):
        """ Set device(s) in ignored. """
        with self.interface.command('App', 'Ignore') as ignore:
            return ignore( self._get_devnames() )

    def simulate(self):
        """ Set device(s) in simulation. """
        with self.interface.command('App', 'Simulate') as simulate:
            return simulate( self._get_devnames() )

    def stop_ignore(self):
        """ Stop device(s) from being ignored. """
        with self.interface.command('App', 'StopIgn') as stop_ignore:
            return stop_ignore( self._get_devnames() )

    def stop_simulate(self):
        """ Stop  device(s) from being simulated. """
        with self.interface.command('App', 'StopSim') as stop_simulate:
            return stop_simulate( self._get_devnames() )

    def init(self):
        """ Executes RPC Init in the PLC for the device(s). """
        with self.interface.command('App', 'HwInit') as init:
            return init( self._get_devnames() )

    def enable(self):
        """ Executes RPC Enable in the PLC for the device(s). """
        with self.interface.command('App', 'HwEnable') as enable:
            return enable( self._get_devnames() )

    def disable(self):
        """ Executes RPC Disable in the PLC for the device(s). """
        with self.interface.command('App', 'HwDisable') as disable:
            return disable( self._get_devnames() )

    def reset(self):
        """ Executes RPC Reset in the PLC for the the device(s). """
        with self.interface.command('App', 'HwReset') as reset:
            return reset( self._get_devnames() )

@dataclass
class DevicesAppAsyncCommands:
    interface: ClientInterfacer

    def _get_devnames(self):
        raise NotImplementedError("_get_devnames")

    async def devstatus(self)->list[str]:
        """ Async Executes a DevStatus Command 

        Return results in a list of string  
        """
        async with self.interface.command('App', 'DevStatus') as async_get_status:
            return (await async_get_status( self._get_devnames()  )).split("\n")

    # ~~~~~~~~~~ autogen ~~~~~~~~~~~~~~~~~

    async def ignore(self):
        """ Set device(s) in ignored. """
        async with self.interface.command('App', 'Ignore') as aignore:
            return await aignore( self._get_devnames() )

    async def simulate(self):
        """ Set device(s) in simulation. """
        async with self.interface.command('App', 'Simulate') as asimulate:
            return await asimulate( self._get_devnames() )

    async def stop_ignore(self):
        """ Stop device(s) from being ignored. """
        async with self.interface.command('App', 'StopIgn') as astop_ignore:
            return await astop_ignore( self._get_devnames() )

    async def stop_simulate(self):
        """ Stop  device(s) from being simulated. """
        async with self.interface.command('App', 'StopSim') as astop_simulate:
            return await astop_simulate( self._get_devnames() )

    async def init(self):
        """ Executes RPC Init in the PLC for the device(s). """
        async with self.interface.command('App', 'HwInit') as ainit:
            return await ainit( self._get_devnames() )

    async def enable(self):
        """ Executes RPC Enable in the PLC for the device(s). """
        async with self.interface.command('App', 'HwEnable') as aenable:
            return await aenable( self._get_devnames() )

    async def disable(self):
        """ Executes RPC Disable in the PLC for the device(s). """
        async with self.interface.command('App', 'HwDisable') as adisable:
            return await adisable( self._get_devnames() )

    async def reset(self):
        """ Executes RPC Reset in the PLC for the the device(s). """
        async with self.interface.command('App', 'HwReset') as areset:
            return await areset( self._get_devnames() )



##########################################################################
#
#   Dev Helper method generator 
#

if __name__ == "__main__":
    _call_method_ ="""
    def {mname}(self):
        \"\"\" {doc} \"\"\"
        with self.interface.command('App', {cname!r}) as {mname}:
            return {mname}( self._get_devnames() )
    """
    _async_method_ ="""
    async def {prefix}{mname}(self):
        \"\"\" {doc} \"\"\"
        async with self.interface.command('App', {cname!r}) as a{mname}:
            return await a{mname}( self._get_devnames() )
    """

    _command_list_ = [
           ("ignore", "Ignore", 'Set device(s) in ignored.'), 
           ("simulate",   "Simulate", 'Set device(s) in simulation.'),
           ("stop_ignore", "StopIgn", 'Stop device(s) from being ignored.'), 
           ("stop_simulate", "StopSim", 'Stop  device(s) from being simulated.'), 
           ("init", "HwInit", 'Executes RPC Init in the PLC for the device(s).'),
           ("enable","HwEnable", 'Executes RPC Enable in the PLC for the device(s).'), 
           ("disable", "HwDisable",'Executes RPC Disable in the PLC for the device(s).' ), 
           ("reset", "HwReset", 'Executes RPC Reset in the PLC for the the device(s).')
        ]

    for mname,cname, doc in _command_list_:
        print( _call_method_.format(mname=mname, cname=cname, doc=doc) )

    for mname,cname, doc in _command_list_:
        print( _async_method_.format(mname=mname, cname=cname, doc=doc, prefix="") )



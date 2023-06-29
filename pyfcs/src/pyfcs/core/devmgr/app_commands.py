from __future__ import annotations
from dataclasses import dataclass
from pyfcs.core.define import ClientInterfacer

def _parse_devnames( devnames, default=None) :
    devnames =  sum( (ds.split() for ds in devnames), [])
    if not devnames:
        if default is None:
            raise ValueError('no device has been specified')
        else:
            return default 
    return devnames 



@dataclass
class AppCommands:
    interface: ClientInterfacer

    def recover(self)->str:
        """ Execute Recover command - App interface """
        with self.interface.command('App', 'Recover') as recover:
            return recover() 

    def devinfo(self)->str:
        """ Execute DevInfo command - App interface """
        with self.interface.command('App','DevInfo') as devinfo:
            return devinfo()

    def devstatus(self, *devnames)->list[str]:
        """ Executes a DevStatus Command

        Args:
            argv(variable list):  List of devices to inquire status.

        It no devices are provided, the status will include all devices.
        """
        devnames = _parse_devnames(devnames, default=[])
        with self.interface.command('App','DevStatus') as devstatus:
            return devstatus( devnames ).split("\n") 

    # ~~~~~~~~~~~~ Autogen ~~~~~~~~~~~~~~~~~~~~~~~~

    def ignore(self, *devnames)->str:
        """ Set one or more devices in ignored.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'Ignore') as ignore:
            return ignore(devnames)


    def simulate(self, *devnames)->str:
        """ Set one or more devices in simulation.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'Simulate') as simulate:
            return simulate(devnames)


    def stop_ignore(self, *devnames)->str:
        """ Stop one or more devices from being ignored.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'StopIgn') as stop_ignore:
            return stop_ignore(devnames)


    def stop_simulate(self, *devnames)->str:
        """ Stop one or more devices from being simulated.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'StopSim') as stop_simulate:
            return stop_simulate(devnames)


    def hw_init(self, *devnames)->str:
        """ Executes RPC Init in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'HwInit') as hw_init:
            return hw_init(devnames)


    def hw_enable(self, *devnames)->str:
        """ Executes RPC Enable in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'HwEnable') as hw_enable:
            return hw_enable(devnames)


    def hw_disable(self, *devnames)->str:
        """ Executes RPC Disable in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'HwDisable') as hw_disable:
            return hw_disable(devnames)


    def hw_reset(self, *devnames)->str:
        """ Executes RPC Reset in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  'HwReset') as hw_reset:
            return hw_reset(devnames)

@dataclass
class AppAsyncCommands:
    interface: ClientInterfacer

    async def recover(self)->str:
        """ Async Execute Recover command - App interface """
        async with self.interface.command('App','Recover') as arecover:
            return await arecover()

    async def devinfo(self)->str:
        """ Async Execute DevInfo command - App interface """
        async with self.interface.command('App','DevInfo') as adevinfo:
            return await adevinfo()

    async def devstatus(self, *devnames)->list[str]:
        """ Executes a DevStatus Command

        Args:
            argv(variable list):  List of devices to inquire status.

        It no devices are provided, the status will include all devices.
        """

        devnames = _parse_devnames(devnames, default=[])
        async with self.interface.command('App','DevStatus') as adevstatus:
            return (await adevstatus( devnames ) ).split("\n")


    # ~~~~~~~~~~~~ Autogen ~~~~~~~~~~~~~~~~~~~~~~~~
    async def ignore(self, *devnames)->str:
        """ Async Set one or more devices in ignored.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'Ignore') as aignore:
            return await aignore(devnames)


    async def simulate(self, *devnames)->str:
        """ Async Set one or more devices in simulation.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'Simulate') as asimulate:
            return await asimulate(devnames)


    async def stop_ignore(self, *devnames)->str:
        """ Async Stop one or more devices from being ignored.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'StopIgn') as astop_ignore:
            return await astop_ignore(devnames)


    async def stop_simulate(self, *devnames)->str:
        """ Async Stop one or more devices from being simulated.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'StopSim') as astop_simulate:
            return await astop_simulate(devnames)


    async def hw_init(self, *devnames)->str:
        """ Async Executes RPC Init in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'HwInit') as ahw_init:
            return await ahw_init(devnames)


    async def hw_enable(self, *devnames)->str:
        """ Async Executes RPC Enable in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'HwEnable') as ahw_enable:
            return await ahw_enable(devnames)


    async def hw_disable(self, *devnames)->str:
        """ Async Executes RPC Disable in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'HwDisable') as ahw_disable:
            return await ahw_disable(devnames)


    async def hw_reset(self, *devnames)->str:
        """ Async Executes RPC Reset in the PLC for the specified devices.

        Args:
            *devnames (list of string):  List of device names or string of device names space separated
        """
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', 'HwReset') as ahw_reset:
            return await ahw_reset(devnames)


# ------------------------------------------- end --------------------------------------------------

# ##############################
#
#   Dev toops 
#

if __name__ == "__main__":
    # Code Generation, probably to be removed at some point 
    _command_list_ = [
           ("ignore","Ignore", 'Set one or more devices in ignored.'), 
           ("simulate","Simulate", 'Set one or more devices in simulation.'),
           ("stop_ignore", "StopIgn", 'Stop one or more devices from being ignored.'), 
           ("stop_simulate", "StopSim", 'Stop one or more devices from being simulated.'), 
           ("hw_init", "HwInit", 'Executes RPC Init in the PLC for the specified devices.'),
           ("hw_enable","HwEnable", 'Executes RPC Enable in the PLC for the specified devices.'), 
           ("hw_disable", "HwDisable",'Executes RPC Disable in the PLC for the specified devices.' ), 
           ("hw_reset", "HwReset", 'Executes RPC Reset in the PLC for the specified devices.')
        ]


    _w_template_ = """
    def {mname}(self, *devnames)->str:
        \"\"\" {doc} 

        Args:
            *devnames (list of string):  List of device names or string of device names space separated 
        \"\"\"
        devnames = _parse_devnames(devnames)
        with self.interface.command('App',  {cname!r}) as {mname}:
            return {mname}(devnames)
    """
    
    print( "# ~~~~~~~~~~~~ Autogen ~~~~~~~~~~~~~~~~~~~~~~~~")
    for mname,cname , doc in _command_list_:
        print( _w_template_.format(mname=mname, cname=cname, doc=doc) )
    print( "# ~~~~~~~~~~~~")


    _aw_template_ = """
    async def {mname}(self, *devnames)->str:
        \"\"\" Async {doc} 

        Args:
            *devnames (list of string):  List of device names or string of device names space separated 
        \"\"\"
        devnames = _parse_devnames(devnames)
        async with self.interface.command('App', {cname!r}) as a{mname}:
            return await a{mname}(devnames)
    """
    
    print( "# ~~~~~~~~~~~~ Autogen ~~~~~~~~~~~~~~~~~~~~~~~~")
    for mname,cname , doc in _command_list_:
        print( _aw_template_.format(mname=mname, cname=cname, doc=doc) )
    print( "# ~~~~~~~~~~~~")


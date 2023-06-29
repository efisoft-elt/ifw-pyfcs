from __future__ import annotations

from ModFcfif.Fcfif import DeviceUnion
from pyfcs.core.api import (BaseDeviceSetup, ParamProperty, parser,  setup_method,payload_parser, register_device,BaseMalIf)

from .channel import ChannelListParamProperty, Enum, Signals

SETOUT = "SETOUT"

# Some helpers function 
def channel(signal, name, value):
    return {'signal':signal, 'name':name, 'value':value}
def digital(name, value):
    return channel(Signals.DIGITAL, name, value)
def analog(name, value):
    return channel(Signals.ANALOG, name, value)
def integer(name, value):
    return channel(Signals.INTEGER, name, value)


if False:
    from ModFcfif.Fcfif import IODevDevice
    from ModFcfif.Fcfif import ActionIODev

    from ModFcfif.Fcfif import VectorfcfifDigitalElem
    from ModFcfif.Fcfif import VectorfcfifAnalogElem
    from ModFcfif.Fcfif import VectorfcfifIntegerElem
    from ModFcfif.Fcfif import DigitalElem
    from ModFcfif.Fcfif import AnalogElem
    from ModFcfif.Fcfif import IntegerElem

    class IoDevMalIf(BaseMalIf, 
            Device= IODevDevice, getter=DeviceUnion.getIodev, setter=DeviceUnion.setIodev
         ):
        def __init__(self, interface, element=None):
            super().__init__(interface, element)
            if element is None: # newly created  element needs to create Vectors ????? 
                # TODO check it may not be necessary to create them, but it is on original code  
                self.digitals = VectorfcfifDigitalElem()
                self.analogs = VectorfcfifAnalogElem()
                self.integers = VectorfcfifIntegerElem()
                self.device.setDigarray( self.diditals )
                self.device.setAnlgarray( self.analogs )
                self.device.setIntarray( self.integers )
            else:
                self.digitals = self.device.getDigarray()
                self.analogs =  self.device.getAnlgarray()
                self.integers =  self.device.getIntarray()

        def add_integer(self, channel, value):
            elem =  self.interface.get_mal().createDataEntity(IntegerElem)
            elem.setChannel(channel)
            elem.setValue(value)
            self.integers.append( elem ) 

        def add_analog(self, channel, value):
            elem =  self.interface.get_mal().createDataEntity(AnalogElem)
            elem.setChannel(channel)
            elem.setValue(value)
            self.analogs.append( elem ) 

        def add_digital(self, channel, value):
            elem =  self.interface.get_mal().createDataEntity(DigitalElem)
            elem.setChannel(channel)
            elem.setValue(value)
            self.digitals.append( elem )

        def set_values(self, values):
            self.device.setAction( values.get('action', ActionIODev.SETOUT))
            channels = values.get("channels", [])
            for channel in channels:
                signal, name, value = (channel[k] for k in ('signal', 'name', 'value')) 
                if signal == Signals.DIGITAL:
                    self.add_digital( name, value)
                elif signal == Signals.ANALOG:
                    self.add_analog( name, value)
                elif signal == Signals.INTEGER:
                    self.add_integer( name, value)
                else:
                    raise ValueError( f"Bug! {signal!r} is not a valid signal" )
            
        def get_values(self):
            channels = []
        
            for channel in self.digitals:
                channels.append( digital(channel.getName(),channel.getValue()) )

            for channel in self.analogs:
                channels.append ( analog(channel.getName(),channel.getValue()) )

            for channel in self.integers:
                channels.append( integer(channel.getName(),channel.getValue()) )
            return channels 

else:
    class _EL:
        _id = ""
        def setId(self, id):
            self._id = id 
        def getId(self):
            return self._id 
    class _CH:
        _name ="" 
        _value = 0 
        def setName(self, name):
            self._name = name 
        def getName(self):
            return self._name 
        def setValue(self, value):
            self._value = value 
        def getValue(self):
            return self._value 

    class  IoDevMalIf:
        def __init__(self, interface, element=None):
            self.interface= interface 
            self.element = _EL() if element is None else element
            self.container = {}
            self.device = {}
            self.digitals = []
            self.analogs = []
            self.integers = []
         
        def add_integer(self, channel, value):
            elem = _CH()
            elem.setChannel(channel)
            elem.setValue(value)
            self.integers.append( elem ) 

        def add_analog(self, channel, value):
            elem =  _CH()            
            elem.setChannel(channel)
            elem.setValue(value)
            self.analogs.append( elem ) 

        def add_digital(self, channel, value):
            elem =  _CH()
            elem.setChannel(channel)
            elem.setValue(value)
            self.digitals.append( elem ) 

    class ActionIODev(Enum):
        SETOUT = 0

class IoDevSetup(BaseDeviceSetup):
    devtype = "iodev"
    MalIf = IoDevMalIf 

    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionIODev), 
                    description = "IODev action.", 
                    required = True
                    )
    channels = ChannelListParamProperty( 
                description = "Channels definitions",                         
            )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = []
            
    @setup_method
    def write_digital(self, name:str, value: bool|str)->None:
        self.set_output( [ digital(name, value) ] )
        
    @setup_method
    def write_analog(self, name:str, value: float)->None:
        self.set_output( [ analog(name, value)] )
       
    @setup_method
    def write_integer(self, name:str, value: int)->None:
        self.set_output( [ integer(name, value) ] )
        
    @payload_parser(action=SETOUT)
    def set_output(self, channels = None):
        if channels:
            # parse the channels from channels ParamProperty  
            channels = self.__class__.channels.parse_in( channels )
            self.channels.extend( channels )
        self.action = SETOUT 

# register the device 
iodev_classes = register_device( IoDevSetup )
IoDevCommand = iodev_classes.Command 
IoDevAsyncCommand = iodev_classes.AsyncCommand 

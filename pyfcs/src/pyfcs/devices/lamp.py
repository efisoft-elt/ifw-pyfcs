
from ModFcfif.Fcfif import LampDevice
from ModFcfif.Fcfif import ActionLamp 
from ModFcfif.Fcfif import DeviceUnion


from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['LampSetup', 'LampCommand', 'LampAsyncCommand']

# quick create a MalIf class 
LampMalIf = create_mal_if( 
        LampDevice, DeviceUnion.getLamp, DeviceUnion.setLamp, 
        action = ( 'getAction', 'setAction'),
        intensity = ( 'getIntensity', 'setIntensity'),
        time = ( 'getTime', 'setTime'),
        
    )

# This device class is registered at the end of this file 
class LampSetup(BaseDeviceSetup):
    devtype = "lamp"
    MalIf = LampMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionLamp),
                    description = "Lamp action.",
                    required = True
                    )
    intensity = ParamProperty( parser.FloatParser(minimum = 0, maximum = 100),
                    description = "Lamp intensity.",
                    )
    time = ParamProperty( parser.IntParser(minimum = 1),
                    description = "Lamp timer.",
                    )
    
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @setup_method
    @payload_parser(action= 'ON')
    def switch_on(self, intensity, time):
        """ switch_on
        
        Args:
            intensity (float) : Lamp intensity.
            time (int) : Lamp timer.
        """
        self.intensity = intensity
        self.time = time
         
        self.action = "ON" 
        
        
    
    @payload_maker(action= 'ON')
    def dump_switch_on(self):
        """ dump payload when action= 'ON'
        """
        return { 
            "action" : "ON",  
            
            "intensity" : self.intensity,
            "time" : self.time,
        }
    
    @setup_method
    @payload_parser(action= 'OFF')
    def switch_off(self, ):
        """ switch_off 
        """
         
        self.action = "OFF" 
        
        
    
    @payload_maker(action= 'OFF')
    def dump_switch_off(self):
        """ dump payload when action= 'OFF'
        """
        return { 
            "action" : "OFF",  
            
        }
    
    
    
        
# register the device. This will create the Command and AsyncCommand classes  
lamp_classes = register_device( LampSetup )
LampCommand = lamp_classes.Command 
LampAsyncCommand = lamp_classes.AsyncCommand 

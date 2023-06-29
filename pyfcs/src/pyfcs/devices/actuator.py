
from ModFcfif.Fcfif import ActuatorDevice
from ModFcfif.Fcfif import ActionActuator 
from ModFcfif.Fcfif import DeviceUnion


from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['ActuatorSetup', 'ActuatorCommand', 'ActuatorAsyncCommand']

# quick create a MalIf class 
ActuatorMalIf = create_mal_if( 
        ActuatorDevice, DeviceUnion.getActuator, DeviceUnion.setActuator, 
        action = ( 'getAction', 'setAction'),
        
    )

# This device class is registered at the end of this file 
class ActuatorSetup(BaseDeviceSetup):
    devtype = "actuator"
    MalIf = ActuatorMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionActuator),
                    description = "Actuator action.",
                    required = True
                    )
    
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @setup_method
    @payload_parser(action= 'ON')
    def switch_on(self, ):
        """ switch_on 
        """
         
        self.action = "ON" 
        
        
    
    @payload_maker(action= 'ON')
    def dump_switch_on(self):
        """ dump payload when action= 'ON'
        """
        return { 
            "action" : "ON",  
            
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
actuator_classes = register_device( ActuatorSetup )
ActuatorCommand = actuator_classes.Command 
ActuatorAsyncCommand = actuator_classes.AsyncCommand 

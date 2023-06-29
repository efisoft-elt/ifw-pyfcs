
from ModFcfif.Fcfif import ShutterDevice
from ModFcfif.Fcfif import ActionShutter 
from ModFcfif.Fcfif import DeviceUnion


from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['ShutterSetup', 'ShutterCommand', 'ShutterAsyncCommand']

# quick create a MalIf class 
ShutterMalIf = create_mal_if( 
        ShutterDevice, DeviceUnion.getShutter, DeviceUnion.setShutter, 
        action = ( 'getAction', 'setAction'),
        
    )

# This device class is registered at the end of this file 
class ShutterSetup(BaseDeviceSetup):
    devtype = "shutter"
    MalIf = ShutterMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionShutter),
                    description = "Shutter action.",
                    required = True
                    )
    
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @setup_method
    @payload_parser(action= 'OPEN')
    def open(self, ):
        """ open 
        """
         
        self.action = "OPEN" 
        
        
    
    @payload_maker(action= 'OPEN')
    def dump_open(self):
        """ dump payload when action= 'OPEN'
        """
        return { 
            "action" : "OPEN",  
            
        }
    
    @setup_method
    @payload_parser(action= 'CLOSE')
    def close(self, ):
        """ close 
        """
         
        self.action = "CLOSE" 
        
        
    
    @payload_maker(action= 'CLOSE')
    def dump_close(self):
        """ dump payload when action= 'CLOSE'
        """
        return { 
            "action" : "CLOSE",  
            
        }
    
    
    
        
# register the device. This will create the Command and AsyncCommand classes  
shutter_classes = register_device( ShutterSetup )
ShutterCommand = shutter_classes.Command 
ShutterAsyncCommand = shutter_classes.AsyncCommand 

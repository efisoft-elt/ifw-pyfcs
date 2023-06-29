
from ModFcfif.Fcfif import PiezoDevice
from ModFcfif.Fcfif import ActionPiezo 
from ModFcfif.Fcfif import DeviceUnion


from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['PiezoSetup', 'PiezoCommand', 'PiezoAsyncCommand']

# quick create a MalIf class 
PiezoMalIf = create_mal_if( 
        PiezoDevice, DeviceUnion.getPiezo, DeviceUnion.setPiezo, 
        action = ( 'getAction', 'setAction'),
        pos1 = ( 'getPos1', 'setPos1'),
        pos2 = ( 'getPos2', 'setPos2'),
        pos3 = ( 'getPos3', 'setPos3'),
        bit1 = ( 'getBit1', 'setBit1'),
        bit2 = ( 'getBit2', 'setBit2'),
        bit3 = ( 'getBit3', 'setBit3'),
        
    )

# This device class is registered at the end of this file 
class PiezoSetup(BaseDeviceSetup):
    devtype = "piezo"
    MalIf = PiezoMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionPiezo),
                    description = "Piezo action.",
                    required = True
                    )
    pos1 = ParamProperty( parser.FloatParser(),
                    description = "Piezo position 1 in volts.",
                    )
    pos2 = ParamProperty( parser.FloatParser(),
                    description = "Piezo position 2 in volts.",
                    )
    pos3 = ParamProperty( parser.FloatParser(),
                    description = "Piezo position 3 in volts.",
                    )
    bit1 = ParamProperty( parser.IntParser(),
                    description = "Piezo position 1 in bits.",
                    )
    bit2 = ParamProperty( parser.IntParser(),
                    description = "Piezo position 2 in bits.",
                    )
    bit3 = ParamProperty( parser.IntParser(),
                    description = "Piezo position 3 in bits.",
                    )
    
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @setup_method
    @payload_parser(action= 'SET_AUTO')
    def set_auto(self, ):
        """ set_auto 
        """
         
        self.action = "SET_AUTO" 
        
        
    
    @payload_maker(action= 'SET_AUTO')
    def dump_set_auto(self):
        """ dump payload when action= 'SET_AUTO'
        """
        return { 
            "action" : "SET_AUTO",  
            
        }
    
    @setup_method
    @payload_parser(action= 'SET_POS')
    def set_pos(self, ):
        """ set_pos 
        """
         
        self.action = "SET_POS" 
        
        
    
    @payload_maker(action= 'SET_POS')
    def dump_set_pos(self):
        """ dump payload when action= 'SET_POS'
        """
        return { 
            "action" : "SET_POS",  
            
        }
    
    @setup_method
    @payload_parser(action= 'SET_HOME')
    def set_home(self, ):
        """ set_home 
        """
         
        self.action = "SET_HOME" 
        
        
    
    @payload_maker(action= 'SET_HOME')
    def dump_set_home(self):
        """ dump payload when action= 'SET_HOME'
        """
        return { 
            "action" : "SET_HOME",  
            
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_ALL_BITS')
    def move_all_bits(self, ):
        """ move_all_bits 
        """
         
        self.action = "MOVE_ALL_BITS" 
        
        
    
    @payload_maker(action= 'MOVE_ALL_BITS')
    def dump_move_all_bits(self):
        """ dump payload when action= 'MOVE_ALL_BITS'
        """
        return { 
            "action" : "MOVE_ALL_BITS",  
            
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_ALL_POS')
    def move_all_pos(self, ):
        """ move_all_pos 
        """
         
        self.action = "MOVE_ALL_POS" 
        
        
    
    @payload_maker(action= 'MOVE_ALL_POS')
    def dump_move_all_pos(self):
        """ dump payload when action= 'MOVE_ALL_POS'
        """
        return { 
            "action" : "MOVE_ALL_POS",  
            
        }
    
    
    
        
# register the device. This will create the Command and AsyncCommand classes  
piezo_classes = register_device( PiezoSetup )
PiezoCommand = piezo_classes.Command 
PiezoAsyncCommand = piezo_classes.AsyncCommand 

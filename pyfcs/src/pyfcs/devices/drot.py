
from ModFcfif.Fcfif import DrotDevice
from ModFcfif.Fcfif import ActionDrot 
from ModFcfif.Fcfif import DeviceUnion


from .motor import MotorSetup

from ModFcfif.Fcfif import ModeDrot

from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['DrotSetup', 'DrotCommand', 'DrotAsyncCommand']

# quick create a MalIf class 
DrotMalIf = create_mal_if( 
        DrotDevice, DeviceUnion.getDrot, DeviceUnion.setDrot, 
        action = ( 'getAction', 'setAction'),
        pos = ( 'getPos', 'setPos'),
        enc = ( 'getEnc', 'setEnc'),
        unit = ( 'getUnit', 'setUnit'),
        name = ( 'getName', 'setName'),
        speed = ( 'getSpeed', 'setSpeed'),
        posang = ( 'getPos', 'setPos'),
        offset = ( lambda d,v: 0.0, lambda d,v: 'V5 feature!'),
        mode = ( 'getMode', 'setMode'),
        
    )

# This device class is registered at the end of this file 
class DrotSetup(MotorSetup):
    devtype = "drot"
    MalIf = DrotMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionDrot, prefix='DROT_'),
                    description = "Drot action.",
                    required = True
                    )
    pos = ParamProperty( parser.FloatParser(),
                    description = "Motor position in user units.",
                    )
    enc = ParamProperty( parser.IntParser(),
                    description = "Motor position in encoders.",
                    )
    unit = ParamProperty( parser.StringParser(enum = ['UU', 'ENC']),
                    description = "Motor position unit.",
                    )
    name = ParamProperty( parser.StringParser(),
                    description = "Motor named position.",
                    )
    speed = ParamProperty( parser.FloatParser(),
                    description = "Motor speed.",
                    )
    posang = ParamProperty( parser.FloatParser(),
                    description = "Drot position angle.",
                    )
    offset = ParamProperty( parser.FloatParser(),
                    description = "Drot tracking offset.",
                    )
    mode = ParamProperty( parser.EnumNameParser(ModeDrot),
                    description = "Drot mode.",
                    )
    
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @setup_method
    @payload_parser(action= 'MOVE_ABS', unit= 'UU')
    def move_abs_pos(self, pos):
        """ move_abs_pos
        
        Args:
            pos (float) : Motor position in user units.
        """
        self.pos = pos
         
        self.action = "MOVE_ABS" 
        self.unit = "UU" 
        
        
    
    @payload_maker(action= 'MOVE_ABS', unit= 'UU')
    def dump_move_abs_pos(self):
        """ dump payload when action= 'MOVE_ABS', unit= 'UU'
        """
        return { 
            "action" : "MOVE_ABS", 
            "unit" : "UU",  
            
            "pos" : self.pos,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_ABS', unit= 'ENC')
    def move_abs_enc(self, enc):
        """ move_abs_enc
        
        Args:
            enc (int) : Motor position in encoders.
        """
        self.enc = enc
         
        self.action = "MOVE_ABS" 
        self.unit = "ENC" 
        
        
    
    @payload_maker(action= 'MOVE_ABS', unit= 'ENC')
    def dump_move_abs_enc(self):
        """ dump payload when action= 'MOVE_ABS', unit= 'ENC'
        """
        return { 
            "action" : "MOVE_ABS", 
            "unit" : "ENC",  
            
            "enc" : self.enc,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_REL', unit= 'UU')
    def move_rel_pos(self, pos):
        """ move_rel_pos
        
        Args:
            pos (float) : Motor position in user units.
        """
        self.pos = pos
         
        self.action = "MOVE_REL" 
        self.unit = "UU" 
        
        
    
    @payload_maker(action= 'MOVE_REL', unit= 'UU')
    def dump_move_rel_pos(self):
        """ dump payload when action= 'MOVE_REL', unit= 'UU'
        """
        return { 
            "action" : "MOVE_REL", 
            "unit" : "UU",  
            
            "pos" : self.pos,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_REL', unit= 'ENC')
    def move_rel_enc(self, enc):
        """ move_rel_enc
        
        Args:
            enc (int) : Motor position in encoders.
        """
        self.enc = enc
         
        self.action = "MOVE_REL" 
        self.unit = "ENC" 
        
        
    
    @payload_maker(action= 'MOVE_REL', unit= 'ENC')
    def dump_move_rel_enc(self):
        """ dump payload when action= 'MOVE_REL', unit= 'ENC'
        """
        return { 
            "action" : "MOVE_REL", 
            "unit" : "ENC",  
            
            "enc" : self.enc,
        }
    
    
    @payload_parser(action= 'MOVE_ABS')
    def _move_abs(self, unit , __0__, *args):
        raise ValueError("un-complete payload")
        
    
    
    
    @payload_parser(action= 'MOVE_REL')
    def _move_rel(self, unit , __0__, *args):
        raise ValueError("un-complete payload")
        
    
    
    @setup_method
    @payload_parser(action= 'MOVE_BY_SPEED')
    def move_by_speed(self, speed):
        """ move_by_speed
        
        Args:
            speed (float) : Motor speed.
        """
        self.speed = speed
         
        self.action = "MOVE_BY_SPEED" 
        
        
    
    @payload_maker(action= 'MOVE_BY_SPEED')
    def dump_move_by_speed(self):
        """ dump payload when action= 'MOVE_BY_SPEED'
        """
        return { 
            "action" : "MOVE_BY_SPEED",  
            
            "speed" : self.speed,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_BY_NAME')
    def move_name_pos(self, name):
        """ move_name_pos
        
        Args:
            name (str) : Motor named position.
        """
        self.name = name
         
        self.action = "MOVE_BY_NAME" 
        
        
    
    @payload_maker(action= 'MOVE_BY_NAME')
    def dump_move_name_pos(self):
        """ dump payload when action= 'MOVE_BY_NAME'
        """
        return { 
            "action" : "MOVE_BY_NAME",  
            
            "name" : self.name,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_BY_POSANG')
    def move_by_posang(self, posang):
        """ move_by_posang
        
        Args:
            posang (float) : Drot position angle.
        """
        self.posang = posang
         
        self.action = "MOVE_BY_POSANG" 
        
        
    
    @payload_maker(action= 'MOVE_BY_POSANG')
    def dump_move_by_posang(self):
        """ dump payload when action= 'MOVE_BY_POSANG'
        """
        return { 
            "action" : "MOVE_BY_POSANG",  
            
            "posang" : self.posang,
        }
    
    @setup_method
    @payload_parser(action= 'START_TRACK')
    def start_track(self, posang, mode):
        """ start_track
        
        Args:
            posang (float) : Drot position angle.
            mode (str) : Drot mode.
        """
        self.posang = posang
        self.mode = mode
         
        self.action = "START_TRACK" 
        
        
    
    @payload_maker(action= 'START_TRACK')
    def dump_start_track(self):
        """ dump payload when action= 'START_TRACK'
        """
        return { 
            "action" : "START_TRACK",  
            
            "posang" : self.posang,
            "mode" : self.mode,
        }
    
    @setup_method
    @payload_parser(action= 'STOP_TRACK')
    def stop_track(self, ):
        """ stop_track
        
        Args:
            
        """
         
        self.action = "STOP_TRACK" 
        
        
    
    @payload_maker(action= 'STOP_TRACK')
    def dump_stop_track(self):
        """ dump payload when action= 'STOP_TRACK'
        """
        return { 
            "action" : "STOP_TRACK",  
            
        }
    
    @setup_method
    @payload_parser(action= 'TRACK_OFFSET')
    def track_offset(self, offset):
        """ track_offset
        
        Args:
            offset (float) : Drot tracking offset.
        """
        self.offset = offset
         
        self.action = "TRACK_OFFSET" 
        
        
    
    @payload_maker(action= 'TRACK_OFFSET')
    def dump_track_offset(self):
        """ dump payload when action= 'TRACK_OFFSET'
        """
        return { 
            "action" : "TRACK_OFFSET",  
            
            "offset" : self.offset,
        }
    
    
    
        
# register the device. This will create the Command and AsyncCommand classes  
drot_classes = register_device( DrotSetup )
DrotCommand = drot_classes.Command 
DrotAsyncCommand = drot_classes.AsyncCommand 

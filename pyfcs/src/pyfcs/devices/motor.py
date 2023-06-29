
from ModFcfif.Fcfif import MotorDevice
from ModFcfif.Fcfif import ActionMotor 
from ModFcfif.Fcfif import DeviceUnion


from ModFcfif.Fcfif import MotorPosUnit

from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['MotorSetup', 'MotorCommand', 'MotorAsyncCommand']

# quick create a MalIf class 
MotorMalIf = create_mal_if( 
        MotorDevice, DeviceUnion.getMotor, DeviceUnion.setMotor, 
        action = ( 'getAction', 'setAction'),
        pos = ( 'getPos', 'setPos'),
        enc = ( 'getEnc', 'setEnc'),
        unit = ( 'getUnit', 'setUnit'),
        name = ( 'getName', 'setName'),
        speed = ( 'getSpeed', 'setSpeed'),
        
    )

# This device class is registered at the end of this file 
class MotorSetup(BaseDeviceSetup):
    devtype = "motor"
    MalIf = MotorMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionMotor),
                    description = "Motor action.",
                    required = True
                    )
    pos = ParamProperty( parser.FloatParser(),
                    description = "Motor position in user units.",
                    )
    enc = ParamProperty( parser.IntParser(),
                    description = "Motor position in encoders.",
                    )
    unit = ParamProperty( parser.EnumNameParser(MotorPosUnit),
                    description = "Motor position unit.",
                    )
    name = ParamProperty( parser.StringParser(),
                    description = "Motor named position.",
                    )
    speed = ParamProperty( parser.FloatParser(),
                    description = "Motor speed.",
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
    
    
    
    def _set_pos(self, pos_or_enc, unit):
        self.unit = unit 
        if unit == "UU":
            self.pos = pos_or_enc 
        else:
            self.enc = pos_or_enc 

    @setup_method
    def move_abs(self, pos_or_enc: float, unit: str ="UU"):
        """ move in absolute a motor 
        
        Args:
            pos_or_enc (float): position in user unit or encoder according to unit
            unit (str,optional): "UU" (default) or "ENC"
        """
        self.action = "MOVE_ABS"
        self._set_pos( pos_or_enc, unit) 

    @setup_method
    def move_rel(self, pos_or_enc:float , unit: str ="UU"):
        """ move in relatif a motor 
        
        Args:
            pos_or_enc (float): position in user unit or encoder according to unit
            unit (str,optional): "UU" (default) or "ENC"
        """
        self.action = "MOVE_REL"
        self._set_pos( pos_or_enc, unit) 

    @setup_method
    def move(self, pos_or_enc:float , type:str = "abs", unit: str ="uu"):
        """ move to a target position  
        
        Args:
            pos_or_enc (float): target position in user unit or encoder according to unit
            type (str, optional): Type of movement - absolute ("abs", default) or relative ("rel") case unsensitive
            unit (str, optional): User units ("uu") or encoders ("enc") case unsensitive

        """
        type = type.lower()
        unit = unit.lower()
        if type == "rel":
            self.action = "MOVE_REL"
        elif type == "abs":
            self.action = "MOVE_ABS"
        else:
            raise ValueError(f"provided movement type is unknown, expecting 'rel','REL', 'abs' or 'ABS' got {type!r}" )
        if unit == "uu":
            self.unit = "UU"
            self.pos = pos_or_enc
        elif unit == "enc":
            self.unit = "ENC"
            self.enc = pos_or_enc 
        else:
            raise ValueError(f"provided unit is unknown, expecting 'uu', 'UU', 'enc' or 'ENC' got {unit!r}" )

        
# register the device. This will create the Command and AsyncCommand classes  
motor_classes = register_device( MotorSetup )
MotorCommand = motor_classes.Command 
MotorAsyncCommand = motor_classes.AsyncCommand 

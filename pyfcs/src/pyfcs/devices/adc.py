
from ModFcfif.Fcfif import AdcDevice
from ModFcfif.Fcfif import ActionAdc 
from ModFcfif.Fcfif import DeviceUnion


from ModFcfif.Fcfif import AxesAdc

from ModFcfif.Fcfif import ModeAdc

from pyfcs.core.api import (
        BaseDeviceSetup, ParamProperty, 
        ParamProperty,  parser,
        setup_method, payload_maker, payload_parser,
        register_device, create_mal_if 
    )

__all__ = ['AdcSetup', 'AdcCommand', 'AdcAsyncCommand']

# quick create a MalIf class 
AdcMalIf = create_mal_if( 
        AdcDevice, DeviceUnion.getAdc, DeviceUnion.setAdc, 
        action = ( 'getAction', 'setAction'),
        pos = ( 'getPos', 'setPos'),
        enc = ( 'getEnc', 'setEnc'),
        unit = ( 'getUnit', 'setUnit'),
        name = ( 'getName', 'setName'),
        speed = ( 'getSpeed', 'setSpeed'),
        posang = ( 'getPos', 'setPos'),
        axis = ( 'getAxis', 'setAxis'),
        mode = ( 'getMode', 'setMode'),
        
    )

# This device class is registered at the end of this file 
class AdcSetup(BaseDeviceSetup):
    devtype = "adc"
    MalIf = AdcMalIf 
     
    # ~~~~~~~~~~~~~~~  Parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    action = ParamProperty( parser.EnumNameParser( ActionAdc, prefix='ADC_'),
                    description = "Adc action.",
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
                    description = "Motor position angle.",
                    )
    axis = ParamProperty( parser.EnumNameParser(AxesAdc),
                    description = "Adc axis.",
                    )
    mode = ParamProperty( parser.EnumNameParser(ModeAdc, prefix='ADC_'),
                    description = "Adc mode.",
                    )
    
    
    # ~~~~~~~~~~~~~~~ Setup/Payload Methods  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @setup_method
    @payload_parser(action= 'MOVE_ABS', unit= 'UU')
    def move_abs_pos(self, pos, axis):
        """ move_abs_pos
        
        Args:
            pos (float) : Motor position in user units.
            axis (str) : Adc axis.
        """
        self.pos = pos
        self.axis = axis
         
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
            "axis" : self.axis,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_ABS', unit= 'ENC')
    def move_abs_enc(self, enc, axis):
        """ move_abs_enc
        
        Args:
            enc (int) : Motor position in encoders.
            axis (str) : Adc axis.
        """
        self.enc = enc
        self.axis = axis
         
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
            "axis" : self.axis,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_REL', unit= 'UU')
    def move_rel_pos(self, pos, axis):
        """ move_rel_pos
        
        Args:
            pos (float) : Motor position in user units.
            axis (str) : Adc axis.
        """
        self.pos = pos
        self.axis = axis
         
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
            "axis" : self.axis,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_REL', unit= 'ENC')
    def move_rel_enc(self, enc, axis):
        """ move_rel_enc
        
        Args:
            enc (int) : Motor position in encoders.
            axis (str) : Adc axis.
        """
        self.enc = enc
        self.axis = axis
         
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
            "axis" : self.axis,
        }
    
    
    @payload_parser(action= 'MOVE_ABS')
    def _move_abs(self, axis , unit , __0__, *args):
        raise ValueError("un-complete payload")
        
    
    
    
    @payload_parser(action= 'MOVE_REL')
    def _move_rel(self, axis , unit , __0__, *args):
        raise ValueError("un-complete payload")
        
    
    
    @setup_method
    @payload_parser(action= 'MOVE_BY_SPEED')
    def move_by_speed(self, speed, axis):
        """ move_by_speed
        
        Args:
            speed (float) : Motor speed.
            axis (str) : Adc axis.
        """
        self.speed = speed
        self.axis = axis
         
        self.action = "MOVE_BY_SPEED" 
        
        
    
    @payload_maker(action= 'MOVE_BY_SPEED')
    def dump_move_by_speed(self):
        """ dump payload when action= 'MOVE_BY_SPEED'
        """
        return { 
            "action" : "MOVE_BY_SPEED",  
            
            "speed" : self.speed,
            "axis" : self.axis,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_BY_NAME')
    def move_name_pos(self, name, axis):
        """ move_name_pos
        
        Args:
            name (str) : Motor named position.
            axis (str) : Adc axis.
        """
        self.name = name
        self.axis = axis
         
        self.action = "MOVE_BY_NAME" 
        
        
    
    @payload_maker(action= 'MOVE_BY_NAME')
    def dump_move_name_pos(self):
        """ dump payload when action= 'MOVE_BY_NAME'
        """
        return { 
            "action" : "MOVE_BY_NAME",  
            
            "name" : self.name,
            "axis" : self.axis,
        }
    
    @setup_method
    @payload_parser(action= 'MOVE_BY_POSANG')
    def move_by_posang(self, posang):
        """ move_by_posang
        
        Args:
            posang (float) : Motor position angle.
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
    def start_track(self, posang):
        """ start_track
        
        Args:
            posang (float) : Motor position angle.
        """
        self.posang = posang
         
        self.action = "START_TRACK" 
        
        
    
    @payload_maker(action= 'START_TRACK')
    def dump_start_track(self):
        """ dump payload when action= 'START_TRACK'
        """
        return { 
            "action" : "START_TRACK",  
            
            "posang" : self.posang,
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
    def move(self, pos_or_enc:float , type:str = "abs", unit: str ="uu", aux_motor=""):
        """ move to a target position  
        
        Args:
            pos_or_enc (float): target position in user unit or encoder according to unit
            type (str, optional): Type of movement - absolute ("abs", default) or relative ("rel") case unsensitive
            unit (str, optional): User units ("uu") or encoders ("enc") case unsensitive
            aux_motor (str, optional): Auxiliar motor name : 'motor1' or 'motor2'

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
        if aux_motor == "motor1":
            self.axis = "ADC1"
        elif aux_motor == "motor2":
            self.axis = "ADC2"
        else:
            raise ValueError(f"provided auxiliar motor ({aux_motor!r}) is unknown, please use either motor1 or motor2")

        
# register the device. This will create the Command and AsyncCommand classes  
adc_classes = register_device( AdcSetup )
AdcCommand = adc_classes.Command 
AdcAsyncCommand = adc_classes.AsyncCommand 

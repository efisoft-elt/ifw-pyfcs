from pyfcs.core.define import SetupEntity
from pyfcs.core.api import (DeviceProperty, DummyInterface, ConsulInterface, ParamProperty, payload_parser, payload_maker, setup_method, parser, BaseAssemblySetup, BaseAssemblyCommand)

from pyfcs import devices 


class A(BaseAssemblySetup):
    devtype = "source"
    mode_loockup = {
        "NIR" : {'lamp1':1.0, 'lamp2': 0.0},
        "RED" : {'lamp1':0.4, 'lamp2': 0.3},
        "BLUE": {'lamp1':0.0, 'lamp2': 0.8},
    }

    action = ParamProperty( str, required=True )
    mode = ParamProperty( parser.StringParser( enum=list(mode_loockup) ) )
    intensity = ParamProperty( float) 
    time = ParamProperty( int ) 

    lamp1 = DeviceProperty('lamp')
    lamp2 = DeviceProperty('lamp')
    
    @setup_method
    @payload_parser(action="ON")
    def switch_on(self, mode, intensity, time):
        self.action = "ON"
        self.mode  = mode  
        self.intensity = intensity
        self.time = time 
        self.apply()
    
    @payload_maker(action="ON")
    def dump_switch_on(self):
        return { "action" :"ON", "mode":self.mode, "intensity":self.intensity, "time":self.time }
    
    @setup_method
    @payload_parser(action="OFF")
    def switch_off(self):
        self.action = "OFF"
        self.apply()
        
    @payload_maker(action="OFF")
    def dump_switch_off(self):
        return {"action": "OFF"}

    def apply(self, setup):
        if self.action in ["ON", "OFF"]:
            for lamp in self.iter_devices():
                lamp.switch_off()

        if self.action == "ON":
            conf = self.mode_loockup[self.mode] 
            for lamp, proportional_intensity in conf.items():
                if proportional_intensity == 0.0:
                    self.get_device(lamp).switch_off() 
                else:
                    self.get_device(lamp).switch_on(
                        proportional_intensity*self.intensity, 
                        self.time
                    )
        
        setup.add( self.lamp1 )
        setup.add( self.lamp2 )

class Ac(BaseAssemblyCommand, generate_methods=True):
    Setup = A
    

def test_assembly_follows_protocol():
    assert issubclass( BaseAssemblySetup, SetupEntity)

def test_schema():
    schema = A.get_schema()
    assert 'action' in schema['properties']
    assert 'intensity' in schema['properties']
    


def test_assembly_instanciation():
    a = A(DummyInterface())
    # should conserve order 
    # assert a.__devices__ == ("lamp1", "lamp2")
    assert a.lamp1.id == "lamp1"
    a.lamp1.switch_on(50, 20) 

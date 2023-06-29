from pyfcs.core.devmgr.class_maker import create_setup_class, create_command_classes 
import pytest 

def test_setup_class_creation():

    Fcs2Setup = create_setup_class("Fcs2", {'lamp1':'lamp', 'lamp2':'lamp', 'sdm':'motor'})
    fcs2_setup = Fcs2Setup.from_dummy()
    fcs2_setup.lamp1.switch_on(50, 30)
    assert fcs2_setup.lamp1.intensity == 50.0 
    with pytest.raises(AttributeError):
        fcs2_setup.add_shutter_open

def test_command_class_creation():
    
    Fcs2, Fcs2As = create_command_classes("Fcs2", {'lamp1':'lamp', 'lamp2':'lamp', 'sdm':'motor'})
    
    fcs2 = Fcs2.from_dummy()
    fcs2.lamp1.new_setup().switch_on(50,10)
    with pytest.raises(AttributeError):
        fcs2.open

    assert fcs2.get('lamp1').Setup.devtype == 'lamp'


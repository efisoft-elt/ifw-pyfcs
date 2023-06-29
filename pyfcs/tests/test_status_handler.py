from pyfcs.core.tools.status_handler import StatusHandler


status = [
 'lamp1.simulated = true',
 'lamp1.lcs.state = Operational',
 'lamp1.lcs.substate = Off',
 'lamp1.lcs.intensity = 0.000000',
 'lamp2.simulated = true',
 'lamp2.lcs.state = Operational',
 'lamp2.lcs.substate = Off',
 'lamp2.lcs.intensity = 0.000000',
 'sdm.simulated = true',
 'sdm.lcs.state = Operational',
 'sdm.lcs.substate = Standstill',
 'sdm.lcs.pos_target = 0.000000',
 'sdm.lcs.pos_actual = 0.001259',
 'sdm.lcs.vel_actual = 0.000000',
 'sdm.lcs.axis_enable = false',
 "sdm.pos_actual_name = ''",
 'sdm.pos_enc = 0',
 '',
 'OK']


def test_status_handler_value():
    sh = StatusHandler(status)

    assert sh.lamp1.lcs.substate == 'Off'
    assert sh.lamp1.lcs.intensity == 0.0
    assert sh.sdm.pos_actual_name == "" 
    assert not sh.sdm.lcs.axis_enable 


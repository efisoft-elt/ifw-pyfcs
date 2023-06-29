import pytest 

from pyfcs.devmgr_setup import DevMgrSetup
from pyfcs.core.tools  import PayloadReceiver 


SCHEMA = DevMgrSetup.get_schema()
pr = PayloadReceiver(SCHEMA)

def test_some_schema_validation():
    # TODO to be completed by a valid set of schema testing 
    pr = PayloadReceiver(SCHEMA)
    
    
    assert pr.validate([{'id':'lamp1' , 'param': {'lamp':{'action':'ON', 'intensity':1.0, 'time':10}}}] )
    
    assert pr.validate([{'id':'motor1' , 'param': {'motor':{'action':'MOVE_ABS', 'pos':5.3, 'unit':'UU' }}}] )

    assert pr.validate( [{'id':'drot1', 'param':{'drot':{'action':'START_TRACK', 'mode':'SKY', 'posang':0.0 }}}] ) 

    # TODO continue validation 

    


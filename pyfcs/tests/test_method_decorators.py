from pyfcs.core.api  import   payload_parser
from pyfcs.core.device.method_decorator import is_payload_parser, get_payload_parser_info 


def test_is_payload_parser_ondecorated_method():
    @payload_parser()
    def f(self):
        pass 
    assert is_payload_parser(f) 
    assert not is_payload_parser( (lambda x:x))

def test_signature_inspection():
    
    @payload_parser()
    def f(self, p1, p2):
        pass 
    
    i = get_payload_parser_info(f)
    assert i.required == ["p1", "p2"]
    assert i.minProperties == 2 
    assert i.maxProperties == 2 
    
    @payload_parser()
    def f(self, p1, p2, *args):
        pass 
    
    i = get_payload_parser_info(f)
    assert i.required == ["p1", "p2"]
    assert i.minProperties == 2 
    assert i.maxProperties is None 

    @payload_parser()
    def f(self,  **kwargs):
        pass 
    
    i = get_payload_parser_info(f)
    assert i.required == []
    assert i.minProperties is None 
    assert i.maxProperties is None 
    
    @payload_parser(action="MOVE", unit="UU")
    def f(self, pos):
        pass 
    
    i = get_payload_parser_info(f)
    assert i.required == ["pos"]
    assert i.minProperties == 3 # action, unit and pos 
    assert i.maxProperties == 3 




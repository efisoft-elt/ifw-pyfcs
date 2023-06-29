from __future__ import annotations
from pyfcs.core.interface import DummyInterface, ConsulInterface, Interface

class DevMgrFactories:
    """ A set of Handy class method to build Object instances """
    @classmethod
    def from_uri(cls, uri: str, timeout:int =60000):
        """ ClassMethod:  Build the object from an uri 

        Args:
            uri (str): app uri with port 
            timeout (int, optional): default is 60000ms 
        """
        return cls(Interface( uri, timeout))
    
    @classmethod
    def from_consul(cls, 
            service: str, 
            timeout: int = 60000, 
            consul_host: str = "localhost", 
            consul_port: int = 8500, 
        ):
        """ ClassMethod: Build the object from a consul service  

        Args:
            service (str): consul service name
            timeout (int, optional): default is 60000ms 
            consul_host (str, optional): host of consul client. Default is 'localhost'
            consul_port (int, optional): port of consul client. Default is 8500
            id (str, optional): id of the object instance  (Not used yet)
            
        """

        return cls(ConsulInterface( service, timeout, consul_host=consul_host, consul_port=consul_port) )
    
    @classmethod
    def from_dummy(cls):
        """ ClassMethod: Build an instance with a Dummy Interface for test purposes """
        return cls( DummyInterface() )




from __future__ import annotations
from pyfcs.core.interface import ConsulInterface, DummyInterface, Interface

class DeviceFactoryMethods:
    @classmethod
    def from_uri(cls, device_id: str,  uri: str, timeout:int =60000):
        """
        Class Method: build instance from a uri and timeout 
        
        Args:
            device_id (str)
            uri (str): address (with port) of the server 
            timeout (int, optional): timeout in miliseconds. default 60000ms
        
        Returns:
            instancied object (DeviceCommand) 

        """
        return cls( Interface( uri, timeout), device_id)
    
    @classmethod
    def from_consul(cls, 
            device_id: str, 
            service: str, 
            timeout: int = 60000, 
            consul_host: str = "localhost", 
            consul_port: int = 8500
        ):
        """ Class Method: build instance from a consul service 
        
        Args:
            device_id (str)
            service (str): consul service (e.g. 'fcs1-req' )
            timeout (int, optional): timeout in miliseconds. default 60000ms
            consul_host (str, optional): Address of the consul server. default 'localhost' 
            consul_port (int optional): port of the consul server. default 8500

        Returns:
            instancied object (DeviceCommand) 

        """
        interface = ConsulInterface(service, timeout, consul_host=consul_host, consul_port=consul_port)
        return cls( interface, device_id)

    @classmethod
    def from_dummy(cls, device_id:str = "anonymous"):
        """ Class Method: Build an instance with a Dummy Interface 

        Used for test purposes 

        Args:
            device_id (str)
        
        Returns:
            instancied object (DeviceCommand) 

        """
        return cls( DummyInterface(), device_id)


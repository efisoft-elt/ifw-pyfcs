""" 
@copyright EFISOFT 
@brief Fcs Interface object for all Fcs Client objects 
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable
from typing_extensions import Protocol

# elt ~~~~
from ModFcfif.Fcfif.AppCmds import AppCmdsSync, AppCmdsAsync
from  acli.mal_client import MalClient
from elt.pymal import loadMal, CiiFactory
from elt.pymal.rr import ClientModule
from elt.pymal.CiiFactoryModule import CiiFactory
from ModMetadaqif.Metadaqif.MetaDaq import MetaDaqSync, MetaDaqAsync
from ModStdif.Stdif.StdCmds import StdCmdsAsync, StdCmdsSync
from stooUtils.consul import ConsulClient as _ConsulClient 
from  consul import Consul 

# ~~~~
from ..tools import cash_property
from ..define import ClientKind 

from .command import  Command, DummyCommand 

# ### PATCH TO Correct bug in v4 
# TODO: Remove patch at v5 
class ConsulClient(_ConsulClient):
    def __init__(self, host='localhost', port=8500):
       self._cons = Consul(host=host, port=port)       
# ###### ###### ###### ###### ##########


class _InterfacePrivate:
    # Some shared method for creating clients 
    def _create_factory(self)->CiiFactory:
        """ Create a new CiiFactory for the interface """
        mapping = loadMal('zpb', {'zpb.domain': '100'})
        factory = CiiFactory.getInstance()
        factory.registerMal('zpb', mapping)
        return factory 
    
    def _get_app_uri_and_factory(self):
        return '{}/AppCmds'.format(self.uri), self._create_factory() 
    
    def _create_app_cii(self)-> MalClient:
        """ Create a Cii MalClient for the interface with synchronious Command """
        uri, factory = self._get_app_uri_and_factory()
        # Timeout is in milliseconds
        return  MalClient(uri, factory, AppCmdsSync, int(self.timeout) / 1000)
    
    def _create_async_app_cii(self)->MalClient:
        """ Create a Cii MalClient for the interface with asynchronious Command """
        uri, factory = self._get_app_uri_and_factory()
        # Timeout is in milliseconds
        return  MalClient(uri, factory, AppCmdsAsync, int(self.timeout) / 1000)
    
    # ~~~~~ DAQ ~~~~~~~~~~~~~~~~~~~~~~ 
    def _get_daq_uri_and_factory(self):
        return '{}/MetaDaq'.format(self.uri), self._create_factory() 

    def _create_daq_cii(self)->MalClient:
        uri, factory = self._get_daq_uri_and_factory()
        return MalClient(uri, factory, MetaDaqSync, int(self.timeout) / 1000)
     
    def _create_async_daq_cii(self)->MalClient:
        uri, factory = self._get_daq_uri_and_factory() 
        return MalClient(uri, factory, MetaDaqAsync, int(self.timeout) / 1000)
    
    # ~~~~~ Std ~~~~~~~~~~~~~~~~~~~~~~ 
    def _get_std_uri_and_factory(self):
        return '{}/StdCmds'.format(self.uri), self._create_factory() 

    def _create_std_cii(self)->MalClient:
        uri, factory = self._get_std_uri_and_factory() 
        return MalClient(uri, factory, StdCmdsSync, int(self.timeout) / 1000)
    
    def _create_async_std_cii(self)->MalClient:
        uri, factory = self._get_std_uri_and_factory()
        return MalClient(uri, factory, StdCmdsAsync, int(self.timeout) / 1000)

class BaseInterface:
    
    def get_client(self, 
           client_kind: str = ClientKind.App, 
           asynchronous: bool = False
         )->ClientModule.Client:

        if client_kind == ClientKind.App:
            if asynchronous:
                return self.async_client 
            else:
                return self.client 
        if client_kind == ClientKind.Std:
            if asynchronous:
                return self.async_std_client 
            else:
                return self.std_client
        if client_kind == ClientKind.Daq:
            if asynchronous:
                return self.async_daq_client
            else:
                return self.daq_client
        raise ValueError(f"Un expected value for client_kind. Expecting one off {', '.join(ClientKind)} got {client_kind}" )
    
    def get_mal(self, 
            client_kind: str = ClientKind.App,
          )->ClientModule.Client:
        
        if client_kind == ClientKind.App:
            return self.cii.get_mal() 
        if client_kind == ClientKind.Std:
            return self.std_cii.get_mal()
        if client_kind == ClientKind.Daq:
            return self.daq_cii.get_mal()
        raise ValueError(f"Un expected value for client_kind. Expecting one off {', '.join(ClientKind)} got {client_kind}" )


    def command(self, client_kind: str, method_name: str, callback:Callable| None = None)->Command:
        """ Build and return new Mal command for this interface 
    
        Command has context manager which will log debug information and/or errors 
    
        Args:
            client_kind (str): one of 'Std', 'Daq', or 'App'
            method_name (str): Method available on the given client (e.g. 'Init', 'Enable', ...)
            callback (optional, Callable): A callabck called after the method was applied in a 
                context manager. The callback shall have the signature f(err) where err is None
                in case of success of an Excpetion instance in case of error 
        
        Returns:
            command (Command) 

        Exemple::

            with interface.command( 'Std', 'Init') as init:
                init( )
            
            # Equivalent to :
            interface.command( 'Std', 'Init').exec()  

            async with interface.command( 'App', 'HwInit') as a_hw_init:
                await a_hw_init( ['lamp1', 'lamp2'])

            # Equivalent to 
            await interface.command( 'App', 'HwInit').async_exec( ['lamp1', 'lamp2'])

        """
        if callback:
            return Command(self, client_kind, method_name, callback=callback) 
        try:
            return self.__dict__[(client_kind,method_name)]
        except KeyError:
            cmd = Command(self, client_kind, method_name)
            self.__dict__[(client_kind,method_name)] = cmd 
            return cmd 

    @cash_property
    def cii(self)->MalClient:
        """ App Cii / Mal Client """
        return self._create_app_cii()

    @cash_property
    def client(self)->ClientModule.Client:
        """ App Client """
        return self.cii.get_mal_client()
    
    @cash_property
    def async_cii(self)->MalClient:
        """ Async App Cii / Mal Client """
        return self._create_async_app_cii()

    @cash_property
    def async_client(self)->ClientModule.Client:
        """ Async App client """
        return self.async_cii.get_mal_client()
    
    @cash_property
    def std_cii(self)->MalClient:
        """ Standard Cii / Mal Client """
        return self._create_std_cii()

    @cash_property
    def std_client(self)->ClientModule.Client:
        """ Standard command Client """
        return self.std_cii.get_mal_client()
    
    @cash_property
    def async_std_cii(self)->MalClient:
        """ Async Standard Cii / Mal Client """
        return self._create_async_std_cii()

    @cash_property
    def async_std_client(self)->ClientModule.Client:
        """ Async Standard command client """
        return self.async_std_cii.get_mal_client()
    
    @cash_property
    def daq_cii(self)->MalClient:
        """ DAQ Cii / Mal Client """
        return self._create_daq_cii()

    @cash_property
    def daq_client(self)->ClientModule.Client:
        """ DAQ command Client """
        return self.daq_cii.get_mal_client()
    
    @cash_property
    def async_daq_cii(self)->MalClient:
        """ Async DAQ Cii / Mal Client """
        return self._create_async_daq_cii()

    @cash_property
    def async_daq_client(self)->ClientModule.Client:
        """ Async DAQ command  client """
        return self.async_daq_cii.get_mal_client()
    




@dataclass(frozen=True) # Frozen assure hashable object 
class Interface(_InterfacePrivate, BaseInterface):
    """ Fcs Interface based on an input uri """
    uri: str 
    timeout: int = 10000


@dataclass(frozen=True)
class ConsulInterface(_InterfacePrivate, BaseInterface):
    """ Fcs Interface based on a consul service id """
    service: str 
    timeout: int = 10000
    consul_host: str = 'localhost' 
    consul_port: int = 8500

    @cash_property
    def uri(self)->str:
        """ server uri from consul service """
        return ConsulClient(
                self.consul_host, 
                self.consul_port
            ).get_uri(self.service) 



class DummyMal:
    # attempt to do dummy, it will not work 
    # not sure how to create a data entity without client 
    def createDataEntity(self, cls):
        return cls()

@dataclass(frozen=True)
class DummyInterface(BaseInterface):
    """ Dummy interface for testing purpose """ 
    @property
    def timeout(self)->int:
        return 0 

    def command(self, client_kind: str, method_name: str, callback:Callable| None = None)->Command:
        return DummyCommand( self, client_kind, method_name, callback=callback)
    
    def get_mal(self, client_kind: str = ClientKind.App) -> ClientModule.Client:
        return DummyMal()

    @property
    def uri(self)->str:
        return 'dummy' 
       
    @property 
    def cii(self):
        """ Dummy -> Raise RuntimeError  """
        raise RuntimeError("This is a dummy interface: cannot instanciate a cii")

    @property
    def client(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a client")
    
    @property
    def async_cii(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a async_cii")

    @property
    def async_client(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a async_client")

    @property 
    def std_cii(self):
        """ Dummy -> Raise RuntimeError  """
        raise RuntimeError("This is a dummy interface: cannot instanciate a cii")

    @property
    def std_client(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a client")
    
    @property
    def async_std_cii(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a async_cii")

    @property
    def async_std_client(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a async_client")

    @property 
    def daq_cii(self):
        """ Dummy -> Raise RuntimeError  """
        raise RuntimeError("This is a dummy interface: cannot instanciate a cii")

    @property
    def daq_client(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a client")
    
    @property
    def async_daq_cii(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a async_cii")

    @property
    def async_daq_client(self):
        raise RuntimeError("This is a dummy interface: cannot instanciate a async_client")


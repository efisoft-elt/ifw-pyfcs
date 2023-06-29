from __future__ import annotations
from ModFcfif.Fcfif import SetupElem

from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import EnumMeta
from typing import Any, Callable
from pyfcs.core.define import ClientInterfacer

class BaseValueProperty:
    pass 

@dataclass
class ValueProperty(BaseValueProperty):
    getter: Callable
    setter: Callable
    
    def __get__(self, malif, cls):
        if malif is None: 
            return self 
        return self.getter( malif.device )
    
    def __set__(self, malif, value):
        self.setter( malif.device, value) 

@dataclass
class EnumValueProperty(BaseValueProperty):
    enumerator: EnumMeta
    getter: Callable
    setter: Callable
    prefix: str = ""
    
    def __get__(self, malif, cls):
        if malif is None: 
            return self 
        device_value = self.getter( malif.device )
        np = len(self.prefix)
        return self.enumerator(device_value).name[np:]
    
    def __set__(self, malif, value):
        device_value = getattr( self.enumerator, self.prefix+value)
        self.setter( malif.device, device_value) 


class MalIfMeta(ABCMeta):
    def __new__(mcs, 
          clsname, bases, namespace, 
          Device: type|None = None, 
          getter: Callable |None = None,
          setter: Callable |None = None
        ):  
        values = set() 
        for cls in bases:
            try:
                values.update ( cls.__values__)
            except AttributeError:
                pass 

        for key,obj in namespace.items():
            if isinstance( obj, BaseValueProperty):
                values.add( key ) 
        namespace['__values__'] = values

        if Device:
            if 'create_device' in namespace:
                raise ValueError("conflic between class Device and create_device function definition")

            def create_device(self):
                return self.interface.get_mal().createDataEntity( Device )
            namespace['create_device'] = create_device 
        if getter:
            if 'get_device' in namespace:
                raise ValueError("conflic between class getter and get_device function definition")

            def get_device(self):
                return getter( self.container )
            namespace['get_device'] = get_device 
        if setter:
            if 'set_device' in namespace:
                raise ValueError("conflic between class setter and set_device function definition")
            def set_device(self, device):
                setter(self.container, device) 
            namespace['set_device'] = set_device 


        return type.__new__( mcs, clsname, bases, namespace)

class BaseMalIf(ABC, metaclass=MalIfMeta): # must follow DeviceInterface Protocol
    def __init__(self, interface: ClientInterfacer, element: SetupElem|None = None):
        self.interface = interface 
        if element is None:
            fcfmal = interface.get_mal()
            self.element = fcfmal.createDataEntity(SetupElem)
            self.container = self.element.getDevice()
            
            # yes we need to do that to set the dataentity correctly 
            self.set_device(  self.create_device() )
            self.device = self.get_device() 
        else:
            self.element = element 
            self.container = self.element.getDevice()
            self.device = self.get_device()

    @abstractmethod        
    def create_device(self):
        # e.g. for a lamp 
        # fcfmal = self.interface.get_mal()
        # retrun fcfmal.createDataEntity( LampDevice )
        raise NotImplementedError
    
    @abstractmethod
    def get_device(self):
        # e.g. self.container.getLamp() 
        raise NotImplementedError 

    @abstractmethod
    def set_device(self, device):
        # e.g. self.container.setLamp( device ) 
        raise NotImplementedError
    
    def set_id(self, id:str)->None:
        """ set the element id """
        self.element.setId(id) 

    def get_id(self)->str:
        """ get the element id """
        return self.element.getId() 

    def set_values(self, values:dict[str, Any])->None:
        """ Set a dictionary of key/values pairs into Mal device object """
        for key, value in values.items():
            try:
                getattr(self, key)
            except AttributeError:
                raise ValueError( f"Unknow parameter {key!r}")
            setattr(self, key, value)

    def get_values(self)->dict[str, Any]:
        """ Get a dictionary of all key/values pairs stored in Mal device object """
        return {key:getattr(self, key) for key in self.__values__}

    



def create_mal_if(Device, getter, setter, auto_list=[], **values):
    """ helper method to create a mal interface class 
    
    The 4 following exemples will give the LampMalIf the same functionalities 
    
    LampMalIf = create_mal_if( 
                    LampDevice, DeviceUnion.getLamp, DeviceUnion.setLamp, 
                    ['action', 'intensity']
            ) 
    
    LampMalIf = create_mal_if( 
                    LampDevice, DeviceUnion.getLamp, DeviceUnion.setLamp, 
                    action =    ("getAction", "getAction"),
                    intensity = ("getIntensity", "getIntensity") 
            ) 

    LampMalIf = create_mal_if( 
                    LampDevice, DeviceUnion.getLamp, DeviceUnion.setLamp, 
                    action =    (LampDevice.getAction, LampDevice.getAction),
                    intensity = (LampDevice.getIntensity, LampDevice.getIntensity)
            ) 
    
    class LampMalIf(BaseMalIf):
        def create_device(self):
            fcfmal = self.interface.get_mal()
            retrun fcfmal.createDataEntity( LampDevice )
        
        def get_device(self):
            self.container.getLamp() 

        def set_device(self, device):
            self.container.setLamp( device ) 

        def set_values(self, values):
            for key, value in values.items():
                if key == "action":
                    self.device.setAction(value)
                elif key == "intensity":
                    self.device.setIntensity(value)
                else:
                    raise ValueError(f"Unknown parameter {key!r}")
        def get_values(self):
            return {
                'action':self.device.getAction(), 
                'intensity':self.device.getIntensity()
            }

    """
    base = values.pop("__base__", BaseMalIf)
    namespace = {}
    
    for name in auto_list:
        namespace[name] = ValueProperty( getattr(Device, "get"+name.capitalize()), 
                                         getattr(Device, "set"+name.capitalize())
                                    )

    for name, (vget, vset) in values.items():
        if isinstance(vget, str): vget = getattr(Device, vget)
        if isinstance(vset, str): vset = getattr(Device, vset)

        namespace[name] = ValueProperty( vget, vset )
    return MalIfMeta( Device.__name__+"MalIF", (base,), namespace, Device=Device, getter=getter, setter=setter)

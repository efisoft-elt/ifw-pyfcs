from typing import Callable


class CashProperty:
    def __init__(self, constructor: Callable):
        self._constructor = constructor
        self._name = None 
    
    def __get__(self, parent, cls):
        if parent is None:
            return self 

        if self._name is None:
            raise ValueError("Property name is not set") 

        value = self._constructor(parent)
        parent.__dict__[self._name] = value
        return value

    def __set_name__(self, _, name):
        self._name = name 

def cash_property(constructor: Callable):
    return CashProperty( constructor )

if __name__ == "__main__":

    class A:
        x = 2.0 

        @cash_property
        def xs(self):
            return self.x 

    a = A()
    assert a.xs == 2.0 
    a.x=10.0 
    assert a.xs == 2.0
    del a.xs
    assert a.xs == 10.0


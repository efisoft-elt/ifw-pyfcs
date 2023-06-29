
class EmptyMeta(type):
    # modify type rendering for template method signatures
    def __str__(cls):
        return "Empty"
    def __repr__(cls):
        return "Empty"

class Empty(metaclass=EmptyMeta):
    """ Empty Argument type """
    ...

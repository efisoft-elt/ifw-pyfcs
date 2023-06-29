from dataclasses import dataclass

from ModFcfif.Fcfif import  VectorfcfifSetupElem

@dataclass
class BufferHolder:
    """ A simple class holding a buffer """
    _buffer:  VectorfcfifSetupElem 
    def get_buffer(self):
        """ Get the buffer """
        return self._buffer







# from . import lamp # register the lamp
# from . import motor 
# from . import shutter 
from ._custom import BaseCustomDeviceSetup 

from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not basename(f).startswith('__')]
exec( "\n".join( "from . import "+m for m in __all__ ))  

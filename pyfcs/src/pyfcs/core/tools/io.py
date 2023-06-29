from __future__ import annotations

import os 
from elt.configng import CiiConfigClient 

def find_config_file(file: str)->str:
    """ Find a configfile within the directories defined in $CFGPATH

    Params:
        file_name (str): config file relative path 
    Returns:
        file_path (str): Absolute file path
    Raises:
        ValueError if no file found 
    """
    if os.path.exists(file):
        return file

    cfgpath = os.environ['CFGPATH'].split(":")
    for directory in cfgpath:
        if os.path.exists(  os.path.join( directory, file) ):
            return  os.path.join( directory, file)
    raise ValueError(f"Cannot find config file {file!r} in any of the $CFGPATH directories")



def load_cfgfile(file:str):
    """ Load a config file with the Cii Config File parser """
     # save current search path
    saved_search_path = CiiConfigClient.get_search_path()
    CiiConfigClient.set_search_path(os.environ["CFGPATH"])
    try:
        cfg = CiiConfigClient.load( file )
    finally:
        CiiConfigClient.set_search_path(saved_search_path) 
    return cfg 

def get_devtypes_from_cfgfile(file: str)->dict[str,str]:
    """ Return a mapping of device name -> device type (lower case) for a given fcs config file 

    Params:
        file_name (str): config file relative path 
    Returns:
        map (dict): dictionary where keys are device name and value device type (string, lower case)

    """
    # save current search path
    devices = load_cfgfile(file).instances.server.devices.as_value()
    return { d['name']:d['type'].lower() for d in devices }

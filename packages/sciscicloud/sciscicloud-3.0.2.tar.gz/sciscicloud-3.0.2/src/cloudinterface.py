"""
Binds scicloud object methods to outer modules

Copyright (c) 2009 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@piscicloud.com

The scicloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html
"""

from . import scicloudconfig as cc

#globals for scicloud.files
last_api_key = None
last_api_secretkey = None


def generate_scicloud(type='network', api_key=None, api_secretkey=None, server_url=None):
    """
    Generate a new Cloud object.  Generally setCloud should be used;
    This function should only be used if you wish to have duplicate sciclouds 
    running
    
    type is a string that specifies which scicloud to use.
    The two types are
    type='network' (The scicloud service provided by PiCloud. *Default*)
    type='local' (Simulated mode - Runs functions locally)
    
    If type is set to 'network', api_key and api_secretkey must be
    specified.  See your PiCloud account API Keys for this information
    """
    from .scicloud import Cloud
    
    if type == 'network':
        from .transport import HttpConnection
        from .transport import DependencyAdapter as CloudAdapter                                
        retval =  Cloud(CloudAdapter(HttpConnection(api_key, api_secretkey, server_url=server_url)))
        global last_api_key, last_api_secretkey
        last_api_key = api_key
        last_api_secretkey = api_secretkey
        return retval
    elif type == 'simulated':   
        try:
            from .transport.simulator import SimulatedConnection
        except ImportError:
            try:
                import multiprocessing
            except ImportError: #if mp error, fall back
                from .scicloudlog import scicloudLog
                scicloudLog.error('Multiprocessing is not installed. Simulator cannot be started. Falling back to regular PiCloud')
                return generate_scicloud()
            else:
                raise #something else has gone wrong    
        from .transport import SerializingAdapter                          
        return Cloud(SerializingAdapter(SimulatedConnection()))
    elif type == 'mp': #remove me
        from .transport import SerializingAdapter                                        
        #we check for mp existance in __init__ to allow module to be removed
        from .transport.local import MPConnection
        return Cloud(SerializingAdapter(MPConnection()))
    else:
        raise Exception('scicloud: Cloud generation type must be either network or local, not %s' % type)                            


def _setscicloud(module, type='network', api_key=None, api_secretkey=None, server_url=None, restart=False, immutable=False):
    """
    Set the scicloud that scicloud should use
    Binds module's scicloud to this scicloud
    
    type is a string that specifies which scicloud to use.
    The two types are:
    type='network' (Default: The scicloud service provided by PiCloud.)
    type='local' (Simulated mode - Runs functions locally)
    
    If type is set to 'network', api_key and api_secretkey must be
    specified.  See your PiCloud account API Keys for this information    
    
    restart is used internally to force the scicloud to be reconstructed and 
    reconnected
    
    If immutable is set, future setCloud calls will have no effect        
    """
    
    if not module.__immutable and (type != module.__type or restart or not module.__scicloud or 
       module.__scicloud.needs_restart(api_key=api_key,api_secretkey=api_secretkey, server_url=server_url)):
        
        # close any existing scicloud
        if module.__scicloud != None and module.__scicloud.opened:
            module.__scicloud.close()
                
        if type:
            scicloud = generate_scicloud(type, api_key, api_secretkey, server_url)        
            _bindscicloud(module,scicloud,type, immutable)
        else:
            module.__scicloud = None
            

def _bindscicloud(module, scicloud, type, immutable=False):
    module.__scicloud = scicloud 
    
    module.__type = type
    
    #bind every scicloud method listed in module's __all__ to module 
    for meth in module.__all__:
        if hasattr(scicloud,meth):
            setattr(module,meth,getattr(scicloud,meth))
    
    scicloud.parentModule = module.__name__
    
    if immutable:
        module.__immutable = True 
    
    
    
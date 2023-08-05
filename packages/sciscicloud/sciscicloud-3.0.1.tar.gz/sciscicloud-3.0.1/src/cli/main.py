#!/usr/bin/python
"""
Entry Point for the Science VM Command-Line Interface (CLI)
"""
# since this module sits in the scicloud package, we use absolute_import
# so that we can easily import the top-level package, rather than the
# scicloud module inside the scicloud package
from __future__ import absolute_import
"""
Copyright (c) 2011 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

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

import sys
import logging
import traceback

try:
    import json
except:
    # Python 2.5 compatibility
    import simplejson as json

import scicloud
from UserDict import DictMixin

from . import argparsers
from .util import list_of_dicts_printer, dict_printer, list_printer,\
    key_val_printer, volume_ls_printer, scicloud_info_printer,\
    scicloud_result_printer, scicloud_result_json_printer, bucket_info_printer,\
    no_newline_printer
from .setup_machine import setup_machine
from . import functions


def main(args=None):
    """Entry point for PiCloud CLI. If *args* is None, it is assumed that main()
    was called from the command-line, and sys.argv is used."""
    
    args = args or sys.argv[1:]
        
    # special case: we want to provide the full help information
    # if the cli is run with no arguments
    if len(args) == 0:
        argparsers.scivm_parser.print_help()
        sys.exit(1)
    
    # special case: if --version is specified at all, print it out
    if '--version' in args:
        print 'scicloud %s' % scicloud.__version__
        print 'running under python %s' % sys.version
        sys.exit(0)
        
    # parse_args is an object whose attributes are populated by the parsed args
    parsed_args = argparsers.scivm_parser.parse_args(args)
    module_name = getattr(parsed_args, '_module', '')
    command_name = getattr(parsed_args, '_command', '')
    function_name = module_name + ('.%s' % command_name if command_name else '')
        
    if function_name != 'setup':
        # using showhidden under setup will cause config to be flushed with hidden variables
        scicloud.config._showhidden()
        scicloud.config.verbose = parsed_args._verbose
        # suppress log messages
        scicloud.config.print_log_level = logging.getLevelName(logging.CRITICAL)

    if parsed_args._api_key:
        scicloud.config.api_key = parsed_args._api_key
    if parsed_args._api_secretkey:
        scicloud.config.api_secretkey = parsed_args._api_secretkey
    if parsed_args._simulate:
        scicloud.config.use_simulator = parsed_args._simulate     
    scicloud.config.commit()
        
    # we take the attributes from the parsed_args object and pass them in
    # as **kwargs to the appropriate function. attributes with underscores
    # are special, and thus we filter them out.
    kwargs = dict([(k, v) for k,v in parsed_args._get_kwargs() if not k.startswith('_')])
                
    # handle post-op 
    for key, value in kwargs.items():
        if callable(value):
            kwargs[key] = value(**kwargs)

    
    # we keep function_mapping and printer_mapping here to prevent
    # circular imports
    
    # maps the output of the parser to what function should be called
    function_mapping = {'setup': setup_machine,
                        'exec': functions.execute,
                        'mapexec': functions.execute_map,
                        'status': functions.status,
                        'join': functions.join,
                        'result': functions.result,
                        'info': functions.info,
                        'kill': functions.kill,                        
                        'delete': functions.delete,
                        'ssh-info': scicloud.shortcuts.ssh.get_ssh_info,
                        'ssh' : functions.ssh,
                        'exec-shell' : functions.exec_shell,
                        'rest.publish': functions.rest_publish, # move to rest?
                        'rest.remove' : scicloud.rest.remove,
                        'rest.list' : scicloud.rest.list,
                        'rest.info' : scicloud.rest.info,
                        'rest.invoke' : functions.rest_invoke,
                        'rest.mapinvoke' : functions.rest_invoke_map,                                                
                        'files.get': scicloud.files.get,
                        'files.put': scicloud.files.put,
                        'files.list': scicloud.files.list,
                        'files.delete': scicloud.files.delete,
                        'files.get-md5': scicloud.files.get_md5,
                        'files.sync-from-scicloud': scicloud.files.sync_from_scicloud,
                        'files.sync-to-scicloud': scicloud.files.sync_to_scicloud,
                        'bucket.get': scicloud.bucket.get,
                        'bucket.put': scicloud.bucket.put,
                        'bucket.iterlist': scicloud.bucket.iterlist,
                        'bucket.list': scicloud.bucket.list,
                        'bucket.info': scicloud.bucket.info,
                        'bucket.remove': scicloud.bucket.remove,
                        'bucket.remove-prefix': scicloud.bucket.remove_prefix,
                        'bucket.get-md5': scicloud.bucket.get_md5,
                        'bucket.sync-from-scicloud': scicloud.bucket.sync_from_scicloud,
                        'bucket.sync-to-scicloud': scicloud.bucket.sync_to_scicloud,
                        'bucket.make-public' : functions.bucket_make_public,
                        'bucket.make-private' : scicloud.bucket.make_private,
                        'bucket.is-public' : scicloud.bucket.is_public,
                        'bucket.public-url-folder' : scicloud.bucket.public_url_folder,
                        'bucket.mpsafe-get' : scicloud.bucket.mpsafe_get,
                        'realtime.request': scicloud.realtime.request,
                        'realtime.release': scicloud.realtime.release,
                        'realtime.list': scicloud.realtime.list,
                        'volume.list': scicloud.volume.get_list,
                        'volume.create': scicloud.volume.create,
                        'volume.mkdir': scicloud.volume.mkdir,
                        'volume.sync': scicloud.volume.sync,
                        'volume.delete': scicloud.volume.delete,
                        'volume.ls': scicloud.volume.ls,
                        'volume.rm': scicloud.volume.rm,
                        'env.list': scicloud.environment.list_envs,
                        'env.list-bases': scicloud.environment.list_bases,
                        'env.create': scicloud.environment.create,
                        'env.edit-info': scicloud.environment.edit_info,
                        'env.clone': scicloud.environment.clone,
                        'env.modify': scicloud.environment.modify,
                        'env.get-hostname': scicloud.environment.get_setup_hostname,
                        'env.get-keypath': scicloud.environment.get_key_path,
                        'env.save': scicloud.environment.save,
                        'env.shutdown': scicloud.environment.shutdown,
                        'env.save-shutdown': scicloud.environment.save_shutdown,
                        'env.delete': scicloud.environment.delete,
                        'env.ssh': scicloud.environment.ssh,
                        'env.rsync': scicloud.environment.rsync,
                        'env.run-script': scicloud.environment.run_script,
                        #'queue.list': scicloud.queue.list,
                        #'queue.create': scicloud.queue.create,
                        #'queue.delete': scicloud.queue.delete,
                        'cron.register': functions.cron_register, # move to rest?
                        'cron.deregister' : scicloud.cron.deregister,
                        'cron.list' : scicloud.cron.list,
                        'cron.run' : scicloud.cron.manual_run,
                        'cron.info' : scicloud.cron.info,
                        'wait-for.status' : scicloud.wait_for.status,
                        'wait-for.port' : scicloud.wait_for.port,
                        }
    
    # maps the called function to another function for printing the output
    printer_mapping = {'status' : key_val_printer('jid', 'status'),
                       'info' : scicloud_info_printer,
                       'result' : scicloud_result_printer,
                       'ssh-info' : dict_printer(['address', 'port', 'username', 'identity']),
                       'rest.list' : list_printer('label'),
                       'rest.info' : dict_printer(['label', 'uri', 'signature', 'output_encoding', 'description']),
                       'realtime.request': dict_printer(['request_id', 'type', 'cores', 'start_time']),
                       'realtime.list': list_of_dicts_printer(['request_id', 'type', 'cores', 'start_time']),
                       'files.list': list_printer('filename'),
                       'bucket.list': list_printer('filename'),
                       'bucket.iterlist': list_printer('filename'),
                       'bucket.info': bucket_info_printer,
                       'volume.list': list_of_dicts_printer(['name', 'mnt_path', 'created', 'desc']),
                       'volume.ls': volume_ls_printer,
                       'env.list': list_of_dicts_printer(['name', 'status', 'action', 'created', 'last_modified']),
                       'env.list-bases': list_of_dicts_printer(['name', 'distro', 'python_version']),
                       'env.get-hostname': no_newline_printer,
                       'env.get-keypath': no_newline_printer,
                       'env.ssh': no_newline_printer,
                       'env.run-script': no_newline_printer,
                       'queue.list' : list_printer('label'),
                       'cron.list' : list_printer('label'),
                       'cron.info' : dict_printer(['label', 'schedule', 'last_run', 'last_jid', 'created', 'creator_host', 'func_name']),
                       'wait-for.port' : dict_printer(['address', 'port']),
                       }
    
    json_printer_mapping = {'result' : scicloud_result_json_printer}

    try:
        # execute function
        ret = function_mapping[function_name](**kwargs) 

        if parsed_args._output == 'json':
            # ordereddict issue.. fix once we on 2.7 only
            if (isinstance(ret, dict) or isinstance(ret, DictMixin)) and type(ret) != dict: 
                ret = dict(ret)
            json_printer = json_printer_mapping.get(function_name)
            if json_printer:
                json_printer(ret, parsed_args._output != 'no-header', kwargs)
            else:
                print json.dumps(ret)
        else:
            if function_name in printer_mapping:
                # use a printer_mapping if it exists
                # this is how dict/tables and lists with columns are printed
                printer_mapping[function_name](ret, parsed_args._output != 'no-header', kwargs)
            else:
                if isinstance(ret, (tuple, list)):
                    # if it's just  list with no mapping, just print it
                    for item in ret:
                        print item
                elif ret or isinstance(ret, bool):
                    # cases where the output is just a string or number or bool
                    print ret
                else:
                    # if the output is None, print nothing
                    pass
            
    except scicloud.CloudException, e:
        if parsed_args._output == 'json':
            sys.stderr.write( json.dumps(e.args ) )
        else:
            # error thrown by scicloud client library)
            sys.stderr.write(str(e)+'\n')
            sys.exit(3)
        
    except Exception, e:
        # unexpected errors
        sys.stderr.write('Got unexpected error\n')
        traceback.print_exc(file = sys.stderr)
        sys.exit(1)
        
    else:
        sys.exit(0)

# -*- coding: utf-8 -*-
"""
Command line action
"""
import datetime, os

from requests.exceptions import HTTPError, ConnectionError, InvalidSchema

from argh import arg, ArghParser
from argh.exceptions import CommandError

from gestus_client import logging_handler
from gestus_client import __version__ as client_version
from gestus_client.config import GestusConfig
from gestus_client.client import GestusClient, ENVIRONMENT_KIND_CHOICES

@arg('-u', '--user', default=None, help="Username to connect to the service")
@arg('-p', '--password', default=None, help="Password to connect to the service")
@arg('-o', '--host', default=None, help="Http(s) address to connect to the service")
@arg('-c', '--config', default='gestus.cfg', help="Path to the Gestus-client config file")
@arg('--passive', default=False, action='store_true', help="Disable config saving")
@arg('-l', '--loglevel', default='info', choices=['debug','info','warning','error','critical'], help="The minimal verbosity level to limit logs output")
@arg('--logfile', default=None, help="A filepath that if setted, will be used to save logs output")
@arg('-t', '--timer', default=False, action='store_true', help="Display elapsed time at the end of execution")
@arg('-g', '--eggs', default=None, help="Path to the eggs directory to scan")
@arg('--name', default=None, help="Website name")
@arg('--url', default=None, help="Website url")
@arg('--env', default=None, choices=[k for k,v in ENVIRONMENT_KIND_CHOICES], help="Environnment name")
@arg('--server', default=None, help="Environnment server address/hostname")
def register(args):
    """
    Register current environnment
    """
    starttime = datetime.datetime.now()
    # Init, load and builds
    root_logger = logging_handler.init_logging(args.loglevel.upper(), logfile=args.logfile)
    
    # Open config file if exists
    config = GestusConfig()
    config.open(args.config)
    configdatas = config.get_datas()
    # Merge config in arguments for empty argument only
    for item in GestusConfig.options:
        if item in configdatas:
            val = getattr(args, item, None) or configdatas[item]
            setattr(args, item, val)
            root_logger.debug("Set config value '%s' to: %s", item, val)
    
    # Validate required argument to connect
    if not args.user or not args.password or not args.host:
        root_logger.error("'user', 'password' and 'hostname' are required arguments to connect to the service")
        raise CommandError('Error exit')
    # Validate required argument to register
    if not args.name or not args.url or not args.env:
        root_logger.error("'name', 'url' and 'env' are required arguments to register the current environnment")
        raise CommandError('Error exit')
    # Validate eggs path argument
    if args.eggs and not os.path.exists(args.eggs):
        root_logger.error("The given eggs path does not exists")
        raise CommandError('Error exit')
    if args.eggs and not os.path.isdir(args.eggs):
        root_logger.error("The given eggs path is not a directory")
        raise CommandError('Error exit')
    
    # Open client
    con = GestusClient(args.host, (args.user, args.password))
    
    # Connect to the service
    try:
        con.connect()
    except (HTTPError, ConnectionError, InvalidSchema) as e:
        import traceback
        top = traceback.extract_stack()[-1]
        root_logger.error("%s: %s", type(e).__name__, e)
        raise CommandError('Error exit')
        
    # Register meta datas
    register_args = [args.name, args.url, args.env]
    if args.server:
        register_args.append(args.server)
    args.website_id, args.environment_id = con.register(*register_args)
    # Update server host
    args.server = con.environment_server
        
    # Register egg list
    if args.eggs:
        con.register_eggs(args.eggs)
    
    # Save config with current values
    if not args.passive:
        root_logger.debug("Saving config")
        values = {}
        for item in GestusConfig.options:
            if hasattr(args, item):
                values[item] = getattr(args, item)
        
        config.set_datas(values)
        config.save()
    
    if args.timer:
        endtime = datetime.datetime.now()
        root_logger.info('Done in %s', str(endtime-starttime))


@arg('-w', '--website', default=None, help="Website ID")
@arg('-e', '--environnment', default=None, help="Environnment ID")
def update(args):
    """
    Update current environnment
    """
    starttime = datetime.datetime.now()
    # Init, load and builds
    root_logger = logging_handler.init_logging(args.loglevel.upper(), logfile=args.logfile)
    
    print "Hello world!"
    
    if args.timer:
        endtime = datetime.datetime.now()
        root_logger.info('Done in %s', str(endtime-starttime))

def main():
    """
    Main entrypoint for console_script (commandline script)
    """
    parser = ArghParser()
    parser.add_argument('-v', '--version', action='version', version=client_version)
    enabled_commands = [register]
    
    parser.add_commands(enabled_commands)
    parser.dispatch()

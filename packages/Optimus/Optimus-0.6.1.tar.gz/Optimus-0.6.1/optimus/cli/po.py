# -*- coding: utf-8 -*-
"""
Command line action to manage translation PO files with pybabel
"""
import datetime, os

from argh import arg

from optimus.logs import init_logging
from optimus.i18n import I18NManager

@arg('-i', '--init', default=False, help="Initialize structure, create template catalog (POT) and initialize catalogs (PO)")
@arg('-u', '--update', default=False, help="Extract translations, update the template catalog (POT) and update the catalogs (PO)")
@arg('-c', '--compile', default=False, help="Process to compilation of catalogs")
@arg('-b', '--backup', default=False, help="Make a backup of the locale directory before doing anything")
@arg('-s', '--settings', default='settings', help="Python path to the settings module")
@arg('-l', '--loglevel', default='info', choices=['debug','info','warning','error','critical'], help="The minimal verbosity level to limit logs output")
@arg('--logfile', default=None, help="A filepath that if setted, will be used to save logs output")
def po(args, init=False, update=False, compile=False):
    """
    Manage catalog for all knowed languages
    """
    starttime = datetime.datetime.now()
    # Init, load and builds
    root_logger = init_logging(args.loglevel.upper(), logfile=args.logfile)
    
    # Only load optimus stuff after the settings module name has been retrieved
    os.environ['OPTIMUS_SETTINGS_MODULE'] = args.settings
    from optimus.conf import settings, import_project_module
    from optimus.utils import display_settings
    
    display_settings(settings, ('DEBUG', 'PROJECT_DIR','SOURCES_DIR','TEMPLATES_DIR','LOCALES_DIR'))
    
    i18n = I18NManager(root_logger, settings)
    
    # TODO: * Copy the actual locale directory to a temporary directory
    #       * If process is success, remove previous backup dir if exists then promote the temp backup dir as the current backup
    #       * If process goes wrong, just remove the temp backup dir
    #       -> Always keeping only one backup dir and allways for a successful process
    if args.backup:
        pass
        
    # NOTE: Should we do this automatically to prevent error on missing files
    #       OR should we only do checking before and abort on the first missing file ?
    if args.init or args.update or args.compile:
        i18n.init_locales_dir()
        i18n.extract()
        i18n.init_catalogs()
    
    if args.update:
        i18n.update_catalogs()
    
    if args.compile:
        i18n.compile_catalogs()
    
    endtime = datetime.datetime.now()
    root_logger.info('Done in %s', str(endtime-starttime))

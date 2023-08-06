#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psbase - shared base helper functions
# Copyright (C) 2010-2011  The pypastset project lead by Brian Vinter
#
# This file is part of pypastset.
#
# pypastset is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pypastset is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# -- END_HEADER ---
#

"""PastSet shared base helper functions"""

import ConfigParser
import os
import subprocess
import time

WARNINGS = '__warnings__'
DEFAULT_TIMEOUT = 60

allowed_log_levels = ['debug', 'info', 'warning', 'error', 'critical']


def graceful_exit(nodes, sleep_secs=1):
    """Graceful exit and clean up after each subprocess in nodes dict with
    name as key and subprocess Popen instance as value.
    """

    clean_rounds = ['check', 'terminate', 'kill', 'wait']
    for action in clean_rounds:
        for name in nodes.keys():
            if nodes[name].poll() == None:
                if action == 'terminate':
                    nodes[name].terminate()
                elif action == 'kill':
                    nodes[name].kill()
                elif action == 'wait':
                    nodes[name].wait()
            else:
                nodes[name].wait()
                del nodes[name]
        time.sleep(sleep_secs)

def load_defaults():
    """Load default settings values"""
    defaults = {}
    defaults['psssh'] = 'ssh'
    defaults['pspython'] = 'python'
    defaults['pspkill'] = 'pkill -9 -f'
    defaults['psprocs'] = '1'
    defaults['psmaster'] = ''
    defaults['pshosts'] = ''
    defaults['psbin'] = os.getcwd()
    defaults['psroot'] = os.path.dirname(__file__)
    defaults['pswaitprocs'] = '-1'
    defaults['pslogpath'] = ''
    defaults['psloglevel'] = 'warning'
    defaults['psconfhelp'] = ''
    return defaults

def configuration_paths():
    """Return a list of configuration paths in the order they are loaded"""
    conf_name = "pypastset.conf"
    # UNIX global system conf dir, but harmless on other platforms
    system_dir = "/etc"
    system_conf = os.path.abspath(os.path.join(system_dir, conf_name))
    install_dir = os.path.dirname(__file__)
    install_conf = os.path.abspath(os.path.join(install_dir, conf_name))
    user_dir = os.path.expanduser("~")
    user_conf = os.path.abspath(os.path.join(user_dir, ".%s" % conf_name))
    return [system_conf, install_conf, user_conf]

def load_environment(defaults):
    """Load settings values from environment"""
    settings = {}
    for key in defaults.keys():
        val = os.getenv(key.upper(), '').strip()
        if val:
            settings[key] = val
    return settings

def load_configuration(defaults):
    """Load settings values from configuration files if available"""
    settings = {}
    parser = ConfigParser.SafeConfigParser()
    conf_paths = configuration_paths()
    parser.read(conf_paths)
    raw_settings = parser.defaults()
    for (key, val) in raw_settings.items():
        if val and (key in defaults.keys() or key.startswith("PYRO_")):
            settings[key] = val
    return settings

def apply_helper(settings):
    """Apply additional dynamic environment settings using optional helper
    module.
    """
    helper_cmd = os.path.expanduser(settings.get('psconfhelp', ''))
    if not helper_cmd:
        return []
    try:
        execfile(helper_cmd)
    except Exception, exc:
        return ["Error running PSCONFHELP script: %s" % exc]
    return []

def validate_settings(defaults, settings):
    """Validate raw settings from conf and environment. Fix any errors and
    return parsed setting dictionary and list of warning messages for local
    logging to handle.
    Missing or invalid values are replaced with values from defaults
    dictionary.
    """
    warnings = []
    # Parse and check values with limits
    settings['psssh'] = settings.get('psssh', defaults['psssh'])
    settings['pspython'] = settings.get('pspython', defaults['pspython'])
    settings['pspkill'] = settings.get('pspkill', defaults['pspkill'])
    try:
        settings['psprocs'] = int(settings.get('psprocs', defaults['psprocs']))
        if settings['psprocs'] < 1:
            raise ValueError('must be a positive integer')
    except ValueError, verr:
        settings['psprocs'] = int(defaults['psprocs'])
        warnings.append('PSPROCS: %s' % verr)
        warnings.append('using default value: %s' % settings['psprocs'])
    settings['psbin'] = settings.get('psbin', defaults['psbin'])
    settings['psroot'] = settings.get('psroot', defaults['psroot'])
    try:
        settings['pswaitprocs'] = int(settings.get('pswaitprocs',
                                      defaults['pswaitprocs']))
        # Bump pswaitprocs tp psprocs if unset
        if settings['pswaitprocs'] < 0:
            settings['pswaitprocs'] = settings['psprocs']
        if settings['pswaitprocs'] < 1 or \
               settings['psprocs'] < settings['pswaitprocs']:
            raise ValueError('must be in range 1 to PSPROCS')
    except ValueError, verr:
        settings['pswaitprocs'] = settings['psprocs']
        warnings.append('PSWAITPROCS: %s' % verr)
        warnings.append('using PSPROCS value: %s' % settings['pswaitprocs'])
    if not settings['psloglevel']:
        settings['psloglevel'] = defaults['psloglevel']
    if not settings['psloglevel'] in allowed_log_levels:
        settings['psloglevel'] = defaults['psloglevel']
        warnings.append('PSLOGLEVEL: must be one of: %s' % \
                        ', '.join(allowed_log_levels))
    # Expand paths
    for name in ('psbin', 'psroot', 'pslogpath'):
        settings[name] = os.path.expanduser(settings.get(name, ''))
    return (settings, warnings)

def load_settings():
    """Load settings using chained updates from optional configuration file
    values overriden with environment variables and with missing or invalid
    values replaced by defaults. The optional PSCONFHELP setting is used to run
    a dynamic update of environment variables right before the PS* environments
    are parsed.
    Any errors or warnings encountered are passed in the WARNINGS fields of the
    resulting settings dictionary.
    """
    raw_settings = {}
    warnings = []
    defaults = load_defaults()
    raw_settings.update(defaults)
    # Load conf and env settings
    conf_settings = load_configuration(defaults)
    raw_settings.update(conf_settings)
    env_settings = load_environment(defaults)
    raw_settings.update(env_settings)
    # Apply env updates from optional conf helper and reload env settings
    help_warn = apply_helper(raw_settings)
    warnings += help_warn
    env_settings = load_environment(defaults)
    raw_settings.update(env_settings)
    (settings, validate_warn) = validate_settings(defaults, raw_settings)
    warnings += validate_warn
    # Pass PYRO_* envs verbatim, too
    for name in os.environ:
        if name.startswith('PYRO_'):
            settings[name] = os.getenv(name)
    settings[WARNINGS] = warnings            
    return settings

def settings_doc():
    """Returns PastSet settings information"""
    conf_paths = configuration_paths()
    return '''Supported PastSet environment values:
PSBIN:       which directory path to search for your application (default ".")
PSROOT:      path of directory with PastSet installation (default ".")
PSMASTER:    name of the master server (default ""), empty means current host
PSHOSTS:     path of hosts file (default ""), empty means use only localhost
PSPROCS:     number of clients to launch using hosts file order (default "1")
PSSSH:       ssh command used to run application on nodes (default "ssh")
PSPYTHON:    python command used to run application on nodes (default "python")
PSPKILL:     pkill command used to kill process by name (default "pkill -9 -f")
PSWAITPROCS: number of clients ready before scheduling jobs (default "PSPROCS")
PSLOGPATH:   where to write internal log (default ""), empty means no log
PSLOGLEVEL:  log level: debug/info/warning/error/critical (default "warning")
PSCONFHELP:  path to the optional PastSet configuration helper (default "")

All settings have internal defaults but can be overriden with configuration
values, which are in turn overriden by any environment settings. If PSCONFHELP
is set to the path of a python script it will be executed inline during
initialization in time for it to override other environment variables.

Configuration files are optional and they are loaded in the following order:
%s

Additionally all Pyro environments described in the Install section of the
Pyro manual can be used to change Pyro defaults like port numbers:
http://www.xs4all.nl/~irmen/pyro3/manual/3-install.html
E.g. use
PYRO_NS_PORT=7777 PYRO_PORT=8888 PYRO_PORT_RANGE=1 PYRO_BC_TIMEOUT=0
to use only the ports 7777 and 8888 and minimize broadcast overhead.
'''.strip() % ', '.join(conf_paths)

def init_logging(conf, logging):
    """Initialize logging based on conf settings"""
    log_format = '%(asctime)s %(module)s %(levelname)s %(message)s'
    log_level = eval("logging.%s" % conf['psloglevel'].upper())
    if conf["pslogpath"]:
        logging.basicConfig(filename=conf["pslogpath"], level=log_level,
                            format=log_format)
    else:
        logging.basicConfig(level=log_level, format=log_format)

def extract_warnings(conf):
    """Delayed extraction of default parsing warnings"""
    return conf.get(WARNINGS, [])

def check_ns_status(conf, operation, success_output):
    """Check if name server operation receives success_output within default
    of 3 attempts.
    """

    # query name server - use pyro client (pyro-nsc) without wrapper script
    # implicitly uses any PYRO_* environments

    nsc_args = [operation]
    pyro_nsc = 'import Pyro.nsc,sys; Pyro.nsc.main(%s)' % nsc_args
    nsc = subprocess.Popen(conf['pspython'].split() + ['-tt', '-c', pyro_nsc],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE
                           )
    _ = nsc.wait()
    nsc_out = nsc.stdout.read()
    if success_output in nsc_out:
        return True
    else:
        return False

def check_ns_ready(conf):
    """Check if name server is online"""
    return check_ns_status(conf, 'ping', 'NS is up and running')

def check_pastset_ready(conf):
    """Check if name server is online"""
    return check_ns_status(conf, 'list', 'PastSet')

def wait_for_ns(conf, timeout=DEFAULT_TIMEOUT):
    """Block until name server is online or timeout seconds have passed. A
    negative timeout value means never time out.
    """
    start_time = time.time()
    while timeout < 0 or time.time() - start_time < timeout:
        if check_ns_ready(conf):
            return True
    return False

def wait_for_pastset(conf, timeout=DEFAULT_TIMEOUT):
    """Block until PastSet tuple server is online or timeout seconds have
    passed. A negative timeout value means never time out.
    """
    start_time = time.time()
    while timeout < 0 or time.time() - start_time < timeout:
        if check_pastset_ready(conf):
            return True
    return False

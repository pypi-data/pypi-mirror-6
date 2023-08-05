#!/usr/bin/env python


"""
This is the MySQL submodule for the nori library; see __main__.py
for license and usage information.


DOCSTRING CONTENTS:
-------------------

    1) About and Requirements
    2) API Classes


1) ABOUT AND REQUIREMENTS:
--------------------------

    This submodule provides MySQL connectivity.  It requires the MySQL
    Connector package.  If the package is not available, the module will
    load, but MySQL connectivity will not be available.


2) API CLASSES:
---------------

    MySQL(DBMS)
        This class adapts the DBMS functionality to MySQL.
        Only differences from the DBMS class are listed below.

        Startup and Config File Processing
        ----------------------------------

        apply_config_defaults_extra()
            Apply configuration defaults that are
            last-minute/complicated.


        DBAPI 2.0 Cursor/Connection Methods
        -----------------------------------

        nextset() is not supported.

        setinputsizes() is not supported.

        setoutputsize() is not supported.

"""


########################################################################
#                               IMPORTS
########################################################################

#########
# system
#########

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from pprint import pprint as pp  # for debugging

import sys
import copy


#########
# add-on
#########

try:
    import mysql.connector
except ImportError:
    pass  # see the status and meta variables section


###############
# this package
###############

from .. import core
from .dbms import DBMS


########################################################################
#                              VARIABLES
########################################################################

##################
# status and meta
##################

# supported / available features
core.supported_features['dbms.mysql'] = 'MySQL support'
if 'mysql.connector' in sys.modules:
    core.available_features.append('dbms.mysql')


########################################################################
#                               CLASSES
########################################################################

class MySQL(DBMS):

    """This class adapts the DBMS functionality to MySQL."""

    #############################
    # class variables: constants
    #############################

    # what the DBMS is called
    DBMS_NAME = 'MySQL'

    # required feature(s) for config settings, etc.
    REQUIRES = DBMS.REQUIRES + ['dbms.mysql']

    # module object containing connect(), etc.
    MODULE = mysql.connector

    # local and remote ports for tunnels (remote is also for direct
    # connections)
    DEFAULT_LOCAL_PORT = 4306
    DEFAULT_REMOTE_PORT = 3306

    # where to look for the socket file, to set the default
    # this is a list of file paths, not directories
    SOCKET_SEARCH_PATH = [
        '/var/run/mysqld/mysqld.sock',
        '/tmp/mysql.sock',
    ]

    # methods and features supported by this DBMS;
    # see below for removals
    _SUPPORTED = copy.copy(DBMS._SUPPORTED)


    #####################################
    # startup and config file processing
    #####################################

    def create_settings(self, heading='', extra_text='', ignore=None,
                        extra_requires=[],
                        tunnel=True if 'ssh' in core.available_features
                                    else False):

        """
        Add a block of DBMS config settings to the script.

        Parameters:
            see DBMS.create_settings()

        Dependencies:
            class vars: DEFAULT_REMOTE_PORT, SOCKET_SEARCH_PATH
            instance vars: _prefix, _delim
            methods: settings_extra_text(),
                     apply_config_defaults_extra()
            config settings: [_prefix+_delim+:] use_ssh_tunnel, port,
                             socket_file
            modules: core, dbms.DBMS

        """

        # first do the generic stuff
        DBMS.create_settings(self, heading, extra_text, ignore,
                             extra_requires, tunnel)

        pd = self._prefix + self._delim

        if tunnel:
            # add notes about SSL
            core.config_settings[pd + 'use_ssh_tunnel']['descr'] = (
'''
Use an SSH tunnel for the {0} connection (True/False)?

If True, specify the host in {1}ssh_host and the port in
{1}remote_port instead of {1}host and
{1}port.

Note: to use {0}'s SSL support, you will need to add the
necessary options to {1}connect_options:
    ssl_ca
    ssl_cert
    ssl_key
    ssl_verify_cert
See the {0} documentation for more information.
'''.format(self.DBMS_NAME, pd)
            )

        #
        # fix some defaults
        #

        core.config_settings[pd + 'host']['default'] = (
            '127.0.0.1'  # mysql.connector default
        )

        core.config_settings[pd + 'port']['default'] = (
            self.DEFAULT_REMOTE_PORT
        )
        for f in self.SOCKET_SEARCH_PATH:
            if (core.check_file_type(f, 'MySQL socket', type_char='s',
                                follow_links=True, must_exist=True,
                                use_logger=None, warn_only=True) and
                  core.check_file_access(f, 'MySQL socket', file_rwx='rw',
                                    use_logger=None, warn_only=True)):
                core.config_settings[pd + 'socket_file']['default'] = f
                break

        # fix up descriptions we replaced
        if extra_text:
            setting_list = []
            if tunnel:
                setting_list += ['use_ssh_tunnel']
            self.settings_extra_text(setting_list, extra_text)

        core.apply_config_defaults_hooks.append(
            self.apply_config_defaults_extra
        )


    def apply_config_defaults_extra(self):

        """
        Apply configuration defaults that are last-minute/complicated.

        Dependencies:
            instance vars: _prefix, _delim
            config settings: [_prefix+_delim+:] port, remote_port
            modules: core

        """

        pd = self._prefix + self._delim

        # pd + 'port', pd + 'remote_port': clarify default
        for s_name in [pd + 'port', pd + 'remote_port']:
            if (s_name in core.config_settings and
                  core.config_settings[s_name]['default'] == 3306):
                core.config_settings[s_name]['default_descr'] = (
                    '3306 (the standard port)'
                )


    def validate_config(self):
        """
        Validate DBMS config settings.
        Only does checks that aren't done in DBMS.validate_config().
        Dependencies:
            instance vars: _ignore, _prefix, _delim, _tunnel_config
            config settings: [_prefix+_delim+:] use_ssh_tunnel,
                             protocol, host, port, socket_file
            modules: core, dbms.DBMS
            Python: 2.0/3.2, for callable()
        """
        if callable(self._ignore) and self._ignore():
            return
        pd = self._prefix + self._delim
        if not self._tunnel_config or not core.cfg[pd + 'use_ssh_tunnel']:
            core.setting_check_list(pd + 'protocol', ['tcp', 'socket'])
            if core.cfg[pd + 'protocol'] == 'tcp':
                core.setting_check_is_set(pd + 'host')
                core.setting_check_is_set(pd + 'port')
            elif core.cfg[pd + 'protocol'] == 'socket':
                core.setting_check_is_set(pd + 'socket_file')
        DBMS.validate_config(self)


    #############################
    # logging and error handling
    #############################

    def render_exception(self, e):
        """
        Return a formatted string for a DBMS-related exception.
        Parameters:
            e: the exception to render
        Dependencies:
            class vars: MODULE
        """
        if hasattr(self.MODULE, '__version__'):  # 1.1+
            return 'Error code: {0}\nDetails: {1}'.format(e.errno, e.msg)
        else:
            return 'Error Code / Details: {0}'.format(e)


    ######################################
    # DBAPI 2.0 cursor/connection methods
    ######################################

    # unsupported methods
    _SUPPORTED.remove('nextset')
    _SUPPORTED.remove('setinputsizes')
    _SUPPORTED.remove('setoutputsize')


    ###########################
    # DBAPI extension wrappers
    ###########################

    def _autocommit(self, what=None):
        """
        Get or set the built-in autocommit status of a DBMS connection.
        If what is True or False, returns True on success, False on
        error.  If what is None, returns True/False, or None on error.
        This internal method handles (only) the DBMS's autocommit
        functionality.
        Parameters:
            what: if True, turn autocommit on; if False, turn it off;
                  if None, return the current status
        Dependencies:
            instance vars: conn
            modules: (conn's module)
        """
        if what is None:
            return self.conn.autocommit
        self.conn.autocommit = what
        return True


    ##################
    # nori extensions
    ##################

    def get_db_list(self, cur):
        """
        Get the list of databases from a DBMS.
        Returns a tuple: (success?, fetched_rows)
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        Dependencies:
            methods: execute(), fetchall()
        """
        if not self.execute(cur, 'SHOW DATABASES;', has_results=True):
            return (False, None)
        return self.fetchall(cur)


    def change_db(self, cur, db_name):
        """
        Change the current database used by a cursor.
        Returns False on error, otherwise True.
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            db_name: the database to change to
        Dependencies:
            methods: execute()
        """
        # do string interpolation because execute()'s parameter
        # substitution only works for data, not db/table/column names
        # (it forces '' around the string)
        return self.execute(cur, 'USE `{0}`;'.format(db_name))


    def get_table_list(self, cur):
        """
        Get the list of tables in the current database.
        Returns a tuple: (success?, fetched_rows)
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        Dependencies:
            methods: execute(), fetchall()
        """
        if not self.execute(cur, 'SHOW TABLES;', has_results=True):
            return (False, None)
        return self.fetchall(cur)


    def get_last_id(self, cur):
        """
        Get the last auto-increment ID inserted into the database.
        Returns a tuple: (success?, last_id)
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        """
        cur = cur if cur else self.cur
        # could use 'SELECT LAST_INSERT_ID();' instead
        return (True, cur.lastrowid)

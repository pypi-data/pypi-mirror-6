#!/usr/bin/env python


"""
This is the DBMS submodule for the nori library; see __main__.py
for license and usage information.


DOCSTRING CONTENTS:
-------------------

    1) About and Requirements
    2) API Classes
    3) Usage in Scripts


1) ABOUT AND REQUIREMENTS:
--------------------------

    This submodule provides database connectivity, including DBAPI 2.0
    wrappers and a few extensions.  It requires a submodule for each
    specific DBMS.


2) API CLASSES:
---------------

    DBMS(object)
        This class wraps all of the DBMS functionality.
        DO NOT INSTANTIATE; USE SUBCLASSES ONLY.

        Class Variables: Constants
        --------------------------

        DBMS_NAME
            What the DBMS is called.

        REQUIRES
            Required feature(s) for config settings, etc.

        MODULE
            Module object containing connect(), etc.

        DEFAULT_LOCAL_PORT
        DEFAULT_REMOTE_PORT
            Local and remote ports for tunnels (remote is also for
            direct connections).

        SOCKET_SEARCH_PATH
            Where to look for the socket file, to set the default.


        Instance Variables
        ------------------

        err_use_logger
        err_warn_only
        err_no_exit
        warn_use_logger
        warn_warn_only
        warn_no_exit
            How to handle errors and warnings; see __init__().

        ssh
            SSH object for the DBMS connection.

        conn
            DBMS connection object.

        cur
            Main DBMS cursor object.


        Housekeeping
        ------------

        supports()
            Class method: Test if a method or feature is supported by a
            DBMS.

        __init__()
            Populate instance variables.

        close_conns()
            Class method: Close all DBMS connections.

        close_cursors()
            Class method: Close all DBMS cursors.

        close_conn_cursors()
            Close all cursors for this DBMS connection.


        Startup and Config File Processing
        ----------------------------------

        create_settings()
            Add a block of DBMS config settings to the script.

        settings_extra_text()
            Add extra text to config setting descriptions.

        validate_config()
            Validate DBMS config settings.

        populate_conn_args()
            Turn the config settings into a dictionary of connection
            args.

        read_password_file()
            Get and the password from the password file.


        Logging and Error Handling
        --------------------------

        error_handler()
            Handle DBMS exceptions with various options.

        render_exception()
            Return a formatted string for a DBMS-related exception.

        save_err_warn()
            Save the err.* and warn.* settings before temporary changes.

        restore_err_warn()
            Restore the err.* and warn.* settings after temporary
            changes.

        check_supports_method()
            Class method: Check if a method is supported by a DBMS, else
            error/exit.

        wrap_call()
            Wrap a DBMS function call in error handling.


        DBMS Connections and Cursors
        ----------------------------

        connect()
            Connect to the DBMS, including any SSH tunnel.

        close()
            Close the DBMS connection, including any SSH tunnel.

        cursor()
            Get a cursor for the DBMS connection.

        close_cursor()
            Close a DBMS cursor.

        auto_cursor()
            Automatically create the main cursor if there isn't one.

        auto_close_cursor()
            Close the main cursor if it was automatically created.


        DBAPI 2.0 Cursor/Connection Methods
        -----------------------------------

        callproc()
            Wrapper: call a stored procedure.

        execute()
            Wrapper: execute a DBMS query.

        executemany()
            Wrapper: execute a DBMS query on multiple parameter sets.

        fetchone()
            Wrapper: fetch the next row of a query result set.

        fetchmany()
            Wrapper: fetch the next set of rows of a query result set.

        fetchall()
            Wrapper: fetch all (remaining) rows of a query result set.

        nextset()
            Wrapper: skip to the next query result set.

        setinputsizes()
            Wrapper: predefine parameter sizes.

        setoutputsize()
            Wrapper: set a large-column buffer size.

        commit()
            Wrapper: commit any pending transaction.

        rollback()
            Wrapper: roll back any pending transaction.


        DBAPI Extension Wrappers
        ------------------------

        autocommit()
            Get or set the autocommit status of the DBMS connection.


        Nori Extensions
        ---------------

        get_db_list()
            Get the list of databases from the DBMS.

        change_db()
            Change the current database used by a cursor.

        get_table_list()
            Get the list of tables in the current database.

        fetchone_generator()
            Wrapper: fetchone() as a generator.

        get_last_id()
            Get the last auto-increment ID inserted into the database.


3) USAGE IN SCRIPTS:
--------------------

    Minimal usage (with the MySQL submodule) looks like this:
        [settings in the config file]
        db = nori.MySQL('mysqlstuff')
        db.create_settings()
        def run_mode_hook():
            db.connect()
            db.execute(None, 'SELECT * FROM table where col=%s;',
                       ['col_value'], has_results=True)
            print(db.fetchall())
            db.execute(None, 'INSERT INTO table (col) VALUES (%s);',
                       ['col_value'], has_results=False)
            db.close()

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
import getpass
import atexit


###############
# this package
###############

from .. import core
from ..ssh import SSH


########################################################################
#                              VARIABLES
########################################################################

##################
# status and meta
##################

#
# exit values
#

core.exitvals['dbms_connect'] = dict(
    num=30,
    descr=(
'''
Error connecting to or disconnecting from a database;
also used for cursors.
'''
    ),
)

core.exitvals['dbms_execute'] = dict(
    num=31,
    descr=(
'''
Error executing a database query/command/function.
'''
    ),
)

# supported / available features
core.supported_features['dbms'] = (
    'generic database support; subfeatures for each DBMS also required'
)
core.available_features.append('dbms')


########################################################################
#                               CLASSES
########################################################################

class DBMS(object):

    """
    This class wraps all of the DBMS functionality.

    DO NOT INSTANTIATE; USE SUBCLASSES ONLY.

    """

    #############################
    # class variables: constants
    #############################

    # what the DBMS is called; subclasses must be define this
    # (e.g.: 'MySQL')
    DBMS_NAME = ''

    # required feature(s) for config settings, etc.
    # subclasses should override and add to this, e.g.:
    #     REQUIRES = DBMS.REQUIRES + ['dbms.mysql']
    REQUIRES = ['dbms']

    # module object containing connect(), etc.
    MODULE = None

    # local and remote ports for tunnels (remote is also for direct
    # connections); must be set by subclasses
    DEFAULT_LOCAL_PORT = None
    DEFAULT_REMOTE_PORT = None

    # where to look for the socket file, to set the default;
    # format can vary by subclass (e.g., files vs. directories)
    SOCKET_SEARCH_PATH = []

    # methods and features supported by this DBMS;
    # subclasses must override this and remove unsupported items, e.g.:
    #     _SUPPORTED = copy.copy(DBMS._SUPPORTED)
    #     _SUPPORTED.remove('nextset')
    _SUPPORTED = [
        'callproc', 'execute', 'executemany', 'fetchone', 'fetchmany',
        'fetchall', 'nextset', 'setinputsizes', 'setoutputsize', 'commit',
        'rollback', 'get_db_list', 'change_db', 'get_table_list',
        'autocommit', 'get_last_id',
    ]


    ################################
    # class variables: housekeeping
    ################################

    # these are used to keep track of all connections/cursors for last-
    # minute cleanup; see close_conns() and close_cursors()
    # NOTE: * do not override them in subclasses
    #       * refer to them with DBMS.var
    _atexit_close_conns_registered = False
    _atexit_close_cursors_registered = False
    _open_conns = []  # actually contains DBMS objects with open conns
    _open_cursors = []    # contains tuples: (DBMS obj, cur obj)


    ###############
    # housekeeping
    ###############

    @classmethod
    def supports(cls, name):
        """
        Test if a method or feature is supported by a DBMS.
        Parameters:
            name: the name of the method or feature to check.
        Dependencies:
            class vars: _SUPPORTED
        """
        return name in cls._SUPPORTED


    def __init__(self, prefix, delim='_', err_use_logger=True,
                 err_warn_only=False, err_no_exit=False,
                 warn_use_logger=True, warn_warn_only=True,
                 warn_no_exit=False):
        """
        Populate instance variables.
        See also save_err_warn() / restore_err_warn().
        Parameters:
            prefix, delim: prefix and delimiter that start the setting
                           names to use
            err_no_exit: if True, don't exit the script on DBMS / tunnel
                         errors (assuming warn_only is False; this is
                         the equivalent of passing exit_val=None to
                         core.generic_error_handler())
            warn_no_exit: like err_no_exit, but for DBMS warnings
            see core.generic_error_handler() for the rest;
                err_* apply to DBMS errors, and warn_* apply to DBMS
                warnings
                note that if warn_warn_only is False, warnings will be
                treated as errors
        Dependencies:
            instance vars: _prefix, _delim, _tunnel_config, _ignore,
                           err_use_logger, err_warn_only, err_no_exit,
                           warn_use_logger, warn_warn_only,
                           warn_no_exit, ssh, conn, cur, _cur_is_auto,
                           _fake_autocommit
        """
        self._prefix = prefix
        self._delim = delim
        self._tunnel_config = False  # see create_settings()
        self._ignore = None  # see create_settings()
        self._conn_args = {}  # see populate_conn_args()
        self.err_use_logger = err_use_logger
        self.err_warn_only = err_warn_only
        self.err_no_exit = err_no_exit
        self.warn_use_logger = warn_use_logger
        self.warn_warn_only = warn_warn_only
        self.warn_no_exit = warn_no_exit
        self.ssh = None  # see create_settings()
        self.conn = None  # see connect()
        self.cur = None  # see cursor()
        self._cur_is_auto = False  # see auto_cursor
        self._fake_autocommit = False  # see autocommit()


    @classmethod
    def close_conns(cls):
        """
        Close all DBMS connections.
        NOTE: * do not override in subclasses
              * call with DBMS.close_conns()
        Dependencies:
            class vars: _open_conns
            instance methods: close()
        """
        # have to use a copy because close() changes the list
        for dbms_obj in cls._open_conns[:]:
            dbms_obj.close()


    @classmethod
    def close_cursors(cls):
        """
        Close all DBMS cursors.
        NOTE: * do not override in subclasses
              * call with DBMS.close_cursors()
        Dependencies:
            class vars: _open_cursors
            instance methods: close_cursor()
        """
        # have to use a copy because close_cursor() changes the list
        for (dbms_obj, cur) in cls._open_cursors[:]:
            dbms_obj.close_cursor(cur)


    def close_conn_cursors(self, force_no_exit=True):
        """
        Close all cursors for this DBMS connection.
        Parameters:
            force_no_exit: if True, don't exit on errors/warnings,
                           regardless of the values of err_no_exit and
                           warn_no_exit
        Dependencies:
            class vars: _open_cursors
            instance methods: close_cursor()
        """
        # have to use a copy because close_cursor() changes the list
        for (dbms_obj, cur) in DBMS._open_cursors[:]:
            if dbms_obj == self:
                dbms_obj.close_cursor(cur, force_no_exit)


    #####################################
    # startup and config file processing
    #####################################

    def create_settings(self, heading='', extra_text='', ignore=None,
                        extra_requires=[],
                        tunnel=True if 'ssh' in core.available_features
                                    else False):

        """
        Add a block of DBMS config settings to the script.

        When modifying, remember to keep the setting_list at the bottom
        and validate_config() in sync with the config settings.

        Parameters:
            heading: if not blank, a heading entry with this value will
                     be added to the config settings
            extra_text: if not blank, this value is added to each
                        setting description (prepended with a blank
                        line; does not include the heading)
                        this is mainly intended to be used for things
                        like 'Ignored if [some setting] is False.'
            ignore: if not None, a function; when this function is true,
                    don't bother validating the settings
            extra_requires: a list of features to be added to the
                            settings' requires attributes
            tunnel: if true, add SSH-tunnel settings

        Dependencies:
            class vars: DBMS_NAME, REQUIRES, DEFAULT_REMOTE_PORT,
                        DEFAULT_LOCAL_PORT
            instance vars: _prefix, _delim, _tunnel_config, _ignore, ssh
            methods: _ignore_ssh_settings, settings_extra_text(),
                     validate_config(), populate_conn_args()
            config settings: [_prefix+_delim+:] (heading),
                             use_ssh_tunnel, protocol, host, port,
                             socket_file, user, password, pw_file,
                             connect_db, connect_options, cursor_options
            modules: getpass, core, ssh.SSH

        """

        pd = self._prefix + self._delim
        self._tunnel_config = tunnel
        self._ignore = ignore

        if heading:
            core.config_settings[pd + 'heading'] = dict(
                heading=heading,
            )

        if tunnel:
            core.config_settings[pd + 'use_ssh_tunnel'] = dict(
                descr=(
'''
Use an SSH tunnel for the {0} connection (True/False)?

If True, specify the host in {1}ssh_host and the port in
{1}remote_port instead of {1}host and
{1}port.
'''.format(self.DBMS_NAME, pd)
                ),
                default=False,
                cl_coercer=core.str_to_bool,
                requires=['ssh'],  # see below for the rest
            )

            ssh_extra_text = ("Ignored if cfg['{0}'] is False." .
                              format(pd + 'use_ssh_tunnel'))
            if extra_text:
                ssh_extra_text += '\n\n' + extra_text
            self.ssh = SSH(self._prefix, self._delim)
            self.ssh.create_settings(
                extra_text=ssh_extra_text,
                ignore=self._ignore_ssh_settings,
                extra_requires=(self.REQUIRES + extra_requires),
                tunnel=True,
                default_local_port=self.DEFAULT_LOCAL_PORT,
                default_remote_port=self.DEFAULT_REMOTE_PORT
            )

        core.config_settings[pd + 'protocol'] = dict(
            descr=(
'''
Protocol to use for the {0} connection.

Can be:
    * 'tcp': use {1}host/port
    * 'socket': use {1}socket_file
'''.format(self.DBMS_NAME, pd) +
('\nIgnored if {0}use_ssh_tunnel is True.'.format(pd) if tunnel else '')
            ),
            default='tcp',
            cl_coercer=str,
        )

        core.config_settings[pd + 'host'] = dict(
            descr=(
'''
Remote hostname for the {0} connection.
'''.format(self.DBMS_NAME, pd) +
('''
Ignored if {0}use_ssh_tunnel is True or if
{0}protocol is not 'tcp'.
'''.format(pd) if tunnel else
'''
Ignored if {0}protocol is not 'tcp'.
'''.format(pd))
            ),
            default='localhost',
            cl_coercer=str,
        )

        core.config_settings[pd + 'port'] = dict(
            descr=(
'''
Remote port number for the {0} connection.
'''.format(self.DBMS_NAME, pd) +
('''
Ignored if {0}use_ssh_tunnel is True or if
{0}protocol is not 'tcp'.
'''.format(pd) if tunnel else
'''
Ignored if {0}protocol is not 'tcp'.
'''.format(pd))
            ),
            # no default here; it should be set by subclasses
            cl_coercer=int,
        )

        core.config_settings[pd + 'socket_file'] = dict(
            descr=(
'''
Path to the socket file for the {0} connection.
'''.format(self.DBMS_NAME, pd) +
('''
Ignored if {0}use_ssh_tunnel is True or if
{0}protocol is not 'socket'.
'''.format(pd) if tunnel else
'''
Ignored if {0}protocol is not 'socket'.
'''.format(pd))
            ),
            # no default here; it should be set by subclasses
            cl_coercer=str,
        )

        core.config_settings[pd + 'user'] = dict(
            descr=(
'''
Username for the {0} connection.
'''.format(self.DBMS_NAME)
            ),
            # see below for default
            cl_coercer=str,
        )
        try:
            core.config_settings[pd + 'user']['default'] = getpass.getuser()
            core.config_settings[pd + 'user']['default_descr'] = (
'''
the username the script is being run under
'''
            )
        except ImportError:
            core.config_settings[pd + 'user']['default_descr'] = (
'''
[none, because the current username could not be found]
'''
            )

        core.config_settings[pd + 'password'] = dict(
            descr=(
'''
Password for the {0} connection.

See also {1}pw_file, below.
'''.format(self.DBMS_NAME, pd)
            ),
            # no default
            cl_coercer=str,
        )

        core.config_settings[pd + 'pw_file'] = dict(
            descr=(
'''
Path to the password file for the {0} connection.

File must contain nothing but the password; leading/trailing whitespace will
be trimmed.

Recommended filename: '/etc/{1}/{2}.pw'.

Ignored if {3}password is set.
'''.format(self.DBMS_NAME, core.script_shortname, self._prefix, pd)
            ),
            # no default
            cl_coercer=str,
        )

        core.config_settings[pd + 'connect_db'] = dict(
            descr=(
'''
Initial database for the {0} connection.
'''.format(self.DBMS_NAME)
            ),
            # no default here; it can be set by subclasses
            cl_coercer=str,
        )

        core.config_settings[pd + 'connect_options'] = dict(
            descr=(
'''
Additional options for the {0} connection.

Options must be supplied as a dict.
'''.format(self.DBMS_NAME)
            ),
            default={},
        )

        core.config_settings[pd + 'cursor_options'] = dict(
            descr=(
'''
Additional options for creating {0} cursors.

Options must be supplied as a dict.
'''.format(self.DBMS_NAME)
            ),
            default={},
        )

        setting_list = [
            'protocol', 'host', 'port', 'socket_file', 'user', 'password',
            'pw_file', 'connect_db', 'connect_options', 'cursor_options',
        ]
        if tunnel:
            setting_list += [
                'use_ssh_tunnel',
            ]
        if extra_text:
            self.settings_extra_text(setting_list, extra_text)
        for s_name in setting_list:
            if 'requires' in core.config_settings[pd + s_name]:
                core.config_settings[pd + s_name]['requires'] += (
                    self.REQUIRES + extra_requires
                )
            else:
                core.config_settings[pd + s_name]['requires'] = (
                    self.REQUIRES + extra_requires
                )

        core.validate_config_hooks.append(self.validate_config)
        core.process_config_hooks.append(self.populate_conn_args)


    def _ignore_ssh_settings(self):
        """
        If true, ignore the SSH config settings.
        Dependencies:
            instance vars: _prefix, _delim
            config settings: [_prefix+_delim+:] use_ssh_tunnel
            instance vars: _ignore
            modules: core
            Python: 2.0/3.2, for callable()
        """
        pd = self._prefix + self._delim
        if callable(self._ignore) and self._ignore():
            return True
        return not core.cfg[pd + 'use_ssh_tunnel']


    def settings_extra_text(self, setting_list, extra_text):
        """
        Add extra text to config setting descriptions.
        Pulled out for use by subclasses that replace descriptions.
        Parameters:
            setting_list: a list of settings to modify
            extra_text: if not blank, added to the descriptions of the
                        settings in setting_list (preceded by a blank
                        line)
                        this is mainly intended to be used for things
                        like 'Ignored if [some setting] is False.'
        Dependencies:
            instance vars: _prefix, _delim
            modules: core
        """
        pd = self._prefix + self._delim
        if extra_text:
            for s_name in setting_list:
                if 'descr' in core.config_settings[pd + s_name]:
                    core.config_settings[pd + s_name]['descr'] += (
                        '\n' + extra_text
                    )
                else:
                    core.config_settings[pd + s_name]['descr'] = (
                        extra_text
                    )


    def validate_config(self):
        """
        Validate DBMS config settings.
        Only does checks that are likely to be relevant for all DBMSes;
        it's easy to be more restrictive in subclasses, but hard to be
        more lenient.
        Dependencies:
            instance vars: _ignore, _prefix, _delim, _tunnel_config
            config settings: [_prefix+_delim+:] use_ssh_tunnel,
                             protocol, host, port, socket_file, user,
                             password, pw_file, connect_db,
                             connect_options, cursor_options
            modules: core
            Python: 2.0/3.2, for callable()
        """
        if callable(self._ignore) and self._ignore():
            return
        pd = self._prefix + self._delim
        if self._tunnel_config:
            core.setting_check_type(pd + 'use_ssh_tunnel', (bool, ))
        if not self._tunnel_config or not core.cfg[pd + 'use_ssh_tunnel']:
            # have to allow for DBMSes that don't have a protocol
            if (pd + 'protocol' not in core.config_settings or
                  (pd + 'protocol' in core.cfg and
                   core.cfg[pd + 'protocol'] == 'tcp')):
                if pd + 'host' in core.cfg:
                    core.setting_check_not_blank(pd + 'host')
                if pd + 'port' in core.cfg:
                    core.setting_check_num(pd + 'port', 1, 65535)
            # have to allow for DBMSes that don't have a protocol
            if (pd + 'protocol' not in core.config_settings or
                  (pd + 'protocol' in core.cfg and
                   core.cfg[pd + 'protocol'] == 'socket')):
                if pd + 'socket_file' in core.cfg:
                    core.setting_check_file_type(pd + 'socket_file', 's')
                    core.setting_check_file_access(pd + 'socket_file', 'rw')
        if pd + 'user' in core.cfg:
            core.setting_check_not_blank(pd + 'user')
        if pd + 'password' in core.cfg:
            core.setting_check_type(pd + 'password', core.STRING_TYPES)
        if pd + 'password' not in core.cfg and pd + 'pw_file' in core.cfg:
            core.setting_check_file_read(pd + 'pw_file')
        if pd + 'connect_db' in core.cfg:
            core.setting_check_not_blank(pd + 'connect_db')
        if pd + 'connect_options' in core.cfg:
            core.setting_check_kwargs(pd + 'connect_options')
        if pd + 'cursor_options' in core.cfg:
            core.setting_check_kwargs(pd + 'cursor_options')


    def populate_conn_args(self):
        """
        Turn the config settings into a dictionary of connection args.
        Dependencies:
            instance vars: _prefix, _delim, _tunnel_config, _conn_args
            methods: read_password_file()
            config_settings: [_prefix+_delim+:] use_ssh_tunnel,
                             local_host, local_port, protocol, host,
                             port, socket_file, user, password, pw_file,
                             connect_db, connect_options
            modules: core
        """
        pd = self._prefix + self._delim
        self._conn_args = {}
        if self._tunnel_config and core.cfg[pd + 'use_ssh_tunnel']:
            self._conn_args['host'] = core.cfg[pd + 'local_host']
            self._conn_args['port'] = core.cfg[pd + 'local_port']
        else:
            # have to allow for DBMSes that don't have a protocol
            if (pd + 'protocol' not in core.config_settings or
                  (pd + 'protocol' in core.cfg and
                   core.cfg[pd + 'protocol'] == 'tcp')):
                if pd + 'host' in core.cfg:
                    self._conn_args['host'] = core.cfg[pd + 'host']
                if pd + 'port' in core.cfg:
                    self._conn_args['port'] = core.cfg[pd + 'port']
            # have to allow for DBMSes that don't have a protocol
            if (pd + 'protocol' not in core.config_settings or
                  (pd + 'protocol' in core.cfg and
                   core.cfg[pd + 'protocol'] == 'socket')):
                if pd + 'socket_file' in core.cfg:
                    self._conn_args['unix_socket'] = (
                        core.fix_path(core.cfg[pd + 'socket_file'])
                    )
        if pd + 'user' in core.cfg:
            self._conn_args['user'] = core.cfg[pd + 'user']
        if pd + 'password' in core.cfg:
            self._conn_args['password'] = core.cfg[pd + 'password']
        elif pd + 'pw_file' in core.cfg:
            self._conn_args['password'] = self.read_password_file()
        if pd + 'connect_db' in core.cfg:
            self._conn_args['database'] = core.cfg[pd + 'connect_db']
        if pd + 'connect_options' in core.cfg:
            self._conn_args.update(core.cfg[pd + 'connect_options'])


    def read_password_file(self):
        """
        Get and the password from the password file.
        Dependencies:
            instance vars: _prefix, _delim
            config_settings: [_prefix+_delim+:] pw_file
            modules: core
        """
        pd = self._prefix + self._delim
        try:
            with open(core.fix_path(core.cfg[pd + 'pw_file']), 'r') as pf:
                return pf.read().strip()
        except IOError as e:
            core.file_error_handler(
                e, 'read', 'password file', cfg[pd + 'pw_file'],
                must_exist=True, use_logger=True, warn_only=False,
                exit_val=core.exitvals['startup']['num']
            )


    #############################
    # logging and error handling
    #############################

    def error_handler(self, e, err_verb, warn_verb, exit_val):

        """
        Handle DBMS exceptions with various options.

        If it returns, returns False.

        Parameters:
            err_verb: a string describing the action that failed, for
                      errors (e.g., 'connect to')
            warn_verb: a string describing the action that failed, for
                       warnings (e.g., 'connecting to')
            see core.generic_error_handler() for the rest

        Dependencies:
            class vars: DBMS_NAME, MODULE
            instance vars: _prefix, _delim, err_use_logger,
                           err_warn_only, err_no_exit, warn_use_logger,
                           warn_warn_only, warn_no_exit
            methods: render_exception()
            modules: (contents of MODULE), core

        """

        pd = self._prefix + self._delim

        if isinstance(e, self.MODULE.Warning):
            use_logger = self.warn_use_logger
            warn_only = self.warn_warn_only
            exit_val = None if self.warn_no_exit else exit_val
        if isinstance(e, self.MODULE.Error):
            use_logger = self.err_use_logger
            warn_only = self.err_warn_only
            exit_val = None if self.err_no_exit else exit_val

        if warn_only:
            msg = ('problem {0} {1} DBMS '
                   '(config prefix/delim {2})' .
                   format(warn_verb, self.DBMS_NAME, core.pps(pd)))
        else:
            msg = ('could not {0} {1} DBMS '
                   '(config prefix/delim {2})' .
                   format(err_verb, self.DBMS_NAME, core.pps(pd)))

        return core.generic_error_handler(
            e, msg, self.render_exception, use_logger, warn_only, exit_val
        )


    def render_exception(self, e):
        """
        Return a formatted string for a DBMS-related exception.
        Parameters:
            e: the exception to render
        """
        return 'Details: {0}'.format(e)


    def save_err_warn(self):
        """
        Save the err.* and warn.* settings before temporary changes.
        Dependencies:
            instance vars: err_use_logger, err_warn_only, err_no_exit,
                           warn_use_logger, warn_warn_only,
                           warn_no_exit, _err_use_logger_saved,
                           _err_warn_only_saved, _err_no_exit_saved,
                           _warn_use_logger_saved,
                           _warn_warn_only_saved, _warn_no_exit_saved
        """
        self._err_use_logger_saved = self.err_use_logger
        self._err_warn_only_saved = self.err_warn_only
        self._err_no_exit_saved = self.err_no_exit
        self._warn_use_logger_saved = self.warn_use_logger
        self._warn_warn_only_saved = self.warn_warn_only
        self._warn_no_exit_saved = self.warn_no_exit


    def restore_err_warn(self):
        """
        Restore the err.* and warn.* settings after temporary changes.
        Dependencies:
            instance vars: err_use_logger, err_warn_only, err_no_exit,
                           warn_use_logger, warn_warn_only,
                           warn_no_exit, _err_use_logger_saved,
                           _err_warn_only_saved, _err_no_exit_saved,
                           _warn_use_logger_saved,
                           _warn_warn_only_saved, _warn_no_exit_saved
        """
        self.err_use_logger = self._err_use_logger_saved
        self.err_warn_only = self._err_warn_only_saved
        self.err_no_exit = self._err_no_exit_saved
        self.warn_use_logger = self._warn_use_logger_saved
        self.warn_warn_only = self._warn_warn_only_saved
        self.warn_no_exit = self._warn_no_exit_saved
        del(self._err_use_logger_saved)
        del(self._err_warn_only_saved)
        del(self._err_no_exit_saved)
        del(self._warn_use_logger_saved)
        del(self._warn_warn_only_saved)
        del(self._warn_no_exit_saved)


    @classmethod
    def check_supports_method(cls, method_name):
        """
        Check if a method is supported by a DBMS, else error/exit.
        Parameters:
            method_name: the name of the method to check.
        Dependencies:
            class vars: DBMS_NAME
            methods: supports()
            modules: sys, core
        """
        if not cls.supports(method_name):
            core.email_logger.error(
                "Internal Error: {0}() was called on a {1} object,\n"
                "which doesn't support it; exiting." .
                format(method_name, cls.DBMS_NAME)
            )
            sys.exit(core.exitvals['internal']['num'])


    def wrap_call(self, func, err_verb='call function on',
                  warn_verb='calling function on', *args, **kwargs):
        """
        Wrap a DBMS function call in error handling.
        Returns a tuple: (success?, function_return_value)
        Parameters:
            func: the function to wrap
            args/kwargs: arguments to pass to the function
            see error_handler() for the rest
        Dependencies:
            class vars: MODULE
            instance vars: err_warn_only
            methods: error_handler()
            modules: (module containing func), core
        """
        core.status_logger.debug('Calling DBMS function {0} with '
                                 'args:\n{1}\nand kwargs:\n{2}' .
                                 format(func, args, kwargs))
        err = False
        ret = None
        try:
            ret = func(*args, **kwargs)
        except (self.MODULE.Warning, self.MODULE.Error) as e:
            self.error_handler(
                e, err_verb, warn_verb,
                core.exitvals['dbms_execute']['num']
            )
            if isinstance(e, self.MODULE.Error) and not self.err_warn_only:
                err = True
        return (not err, ret)


    ###############################
    # DBMS connections and cursors
    ###############################

    def connect(self):

        """
        Connect to the DBMS, including any SSH tunnel.

        Returns False on error, otherwise True.

        Dependencies:
            class vars: DBMS_NAME, MODULE,
                        _atexit_close_conns_registered, _open_conns
            instance vars: _prefix, _delim, _tunnel_config, ssh,
                           _conn_args, conn, err_use_logger,
                           err_warn_only, err_no_exit
            methods: close_conns(), error_handler()
            config settings: [_prefix+_delim+:] use_ssh_tunnel
            modules: atexit, (contents of MODULE), core, (ssh.SSH)

        """

        pd = self._prefix + self._delim

        # SSH tunnel
        if self._tunnel_config and core.cfg[pd + 'use_ssh_tunnel']:
            if self.err_no_exit:
                # atexit_reg = True, exit_val = None
                self.ssh.open_tunnel(self.DBMS_NAME + ' connection',
                                     True, self.err_use_logger,
                                     self.err_warn_only, None)
            else:
                # atexit_reg = True
                self.ssh.open_tunnel(self.DBMS_NAME + ' connection',
                                     True, self.err_use_logger,
                                     self.err_warn_only)

        # DBMS connection
        core.status_logger.info(
            'Connecting to {0} DBMS (config prefix/delim {1})...' .
            format(self.DBMS_NAME, core.pps(pd))
        )
        try:
            self.conn = self.MODULE.connect(**self._conn_args)
        except (self.MODULE.Warning, self.MODULE.Error) as e:
            self.error_handler(e, 'connect to', 'connecting to',
                               core.exitvals['dbms_connect']['num'])
            if isinstance(e, self.MODULE.Error):
                self.conn = None
                if self._tunnel_config and core.cfg[pd + 'use_ssh_tunnel']:
                    self.ssh.close_tunnel()
                return False
        if self not in DBMS._open_conns:
            DBMS._open_conns.append(self)
        if not DBMS._atexit_close_conns_registered:
            atexit.register(DBMS.close_conns)
            DBMS._atexit_close_conns_registered = True
        core.status_logger.info('{0} connection established.' .
                                format(self.DBMS_NAME))
        return True


    def close(self, force_no_exit=True):

        """
        Close the DBMS connection, including any SSH tunnel.

        Returns False on error, otherwise True.

        Parameters:
            force_no_exit: if True, don't exit on errors/warnings,
                           regardless of the values of err_no_exit and
                           warn_no_exit

        Dependencies:
            class vars: DBMS_NAME, MODULE, _open_conns
            instance vars: _prefix, _delim, _tunnel_config, ssh, conn,
                           err_warn_only, err_no_exit, warn_no_exit
            methods: close_conn_cursors(), save_err_warn(),
                     restore_err_warn(), error_handler()
            config settings: [_prefix+_delim+:] use_ssh_tunnel
            modules: (contents of MODULE), core, (ssh.SSH)

        """

        pd = self._prefix + self._delim

        # already closed?
        if self.conn is None:
            core.status_logger.info(
                '{0} connection (config prefix/delim {1})\n'
                'was already closed.' .
                format(self.DBMS_NAME, core.pps(pd))
            )
            return True

        # cursors
        self.close_conn_cursors(force_no_exit)

        # DBMS connection
        err = False
        try:
            self.conn.close()
        except (self.MODULE.Warning, self.MODULE.Error) as e:
            if force_no_exit:
                self.save_err_warn()
                self.err_no_exit = True
                self.warn_no_exit = True
            self.error_handler(e, 'close connection to',
                               'closing connection to',
                               core.exitvals['dbms_connect']['num'])
            if force_no_exit:
                self.restore_err_warn()
            if (isinstance(e, self.MODULE.Error) and
                  not self.err_warn_only):
                err = True
        self.conn = None
        if not err:
            core.status_logger.info(
                '{0} connection (config prefix/delim {1})\n'
                'has been closed.' .
                format(self.DBMS_NAME, core.pps(pd))
            )
        if self in DBMS._open_conns:
            DBMS._open_conns.remove(self)

        # SSH tunnel
        if self._tunnel_config and core.cfg[pd + 'use_ssh_tunnel']:
            self.ssh.close_tunnel()

        return not err


    def cursor(self, main=True):

        """
        Get a cursor for the DBMS connection.

        Returns the cursor object, or None on error.

        Close with close_cursor(), NOT directly.

        Parameters:
            main: if True, treat this as the main cursor: store it in
                  the object and use it by default in other methods

        Dependencies:
            class vars: DBMS_NAME, MODULE,
                        _atexit_close_cursors_registered, _open_cursors
            instance vars: _prefix, _delim, conn, cur
            methods: close_cursors(), error_handler()
            config settings: [_prefix+_delim+:] cursor_options
            modules: atexit, (contents of MODULE), core

        """

        pd = self._prefix + self._delim

        try:
            cur = self.conn.cursor(**core.cfg[pd + 'cursor_options'])
        except (self.MODULE.Warning, self.MODULE.Error) as e:
            self.error_handler(e, 'get cursor for', 'getting cursor for',
                               core.exitvals['dbms_connect']['num'])
            if isinstance(e, self.MODULE.Error):
                cur = None

        if main:
            self.cur = cur
        if cur:
            if main:
                if (self, None) not in DBMS._open_cursors:
                    DBMS._open_cursors.append((self, None))
            else:
                if (self, cur) not in DBMS._open_cursors:
                    DBMS._open_cursors.append((self, cur))
            if not DBMS._atexit_close_cursors_registered:
                atexit.register(DBMS.close_cursors)
                DBMS._atexit_close_cursors_registered = True
            core.status_logger.debug('Got {0}{1} cursor.' .
                                     format('main ' if main else '',
                                            self.DBMS_NAME))

        return cur


    def close_cursor(self, cur=None, force_no_exit=True):

        """
        Close a DBMS cursor.

        Can be called more than once for the main cursor, but calling
        on an already-closed non-main cursor will cause an error.

        Returns False on error, otherwise True.

        Parameters:
            cur: the cursor to close; if None, the main cursor is
                 closed
            force_no_exit: if True, don't exit on errors/warnings,
                           regardless of the values of err_no_exit and
                           warn_no_exit

        Dependencies:
            class vars: DBMS_NAME, MODULE, _open_cursors
            instance vars: _prefix, _delim, cur, err_warn_only,
                           err_no_exit, warn_no_exit
            methods: save_err_warn(), restore_err_warn(),
                     error_handler()
            modules: (contents of MODULE), core

        """

        pd = self._prefix + self._delim

        # main and already closed?
        if cur is None and self.cur is None:
            core.status_logger.debug(
                'Main {0} cursor (config prefix/delim {1})\n'
                'was already closed.' .
                format(self.DBMS_NAME, core.pps(pd))
            )
            return True

        main_str = 'main ' if cur is None else ''
        err = False
        try:
            if cur is None:
                self.cur.close()
            else:
                cur.close()
        except (self.MODULE.Warning, self.MODULE.Error) as e:
            if force_no_exit:
                self.save_err_warn()
                self.err_no_exit = True
                self.warn_no_exit = True
            self.error_handler(
                e, 'close {0}cursor for'.format(main_str),
                'closing {0}cursor for'.format(main_str),
                core.exitvals['dbms_connect']['num']
            )
            if force_no_exit:
                self.restore_err_warn()
            if (isinstance(e, self.MODULE.Error) and
                  not self.err_warn_only):
                err = True

        if cur is None:
            self.cur = None
        # no else; otherwise, we'd be setting cur = None, and then
        # calling this function again with the same value of cur would
        # refer to the main cursor

        if not err:
            core.status_logger.debug(
                '{0}{1} cursor (config prefix/delim {2})\n'
                'has been closed.' .
                format(main_str.capitalize(), self.DBMS_NAME, core.pps(pd))
            )

        if cur is None:
            if (self, None) in DBMS._open_cursors:
                DBMS._open_cursors.remove((self, None))
        else:
            if (self, cur) in DBMS._open_cursors:
                DBMS._open_cursors.remove((self, cur))

        return not err


    def auto_cursor(self):
        """
        Automatically create the main cursor if there isn't one.
        Dependencies:
            instance vars: cur, _cur_is_auto
            methods: cursor()
        """
        if self.cur is None:
            if self.cursor() is not None:
                self._cur_is_auto = True


    def auto_close_cursor(self):
        """
        Close the main cursor if it was automatically created.
        Dependencies:
            instance vars: _cur_is_auto
            methods: close_cursor()
        """
        if self._cur_is_auto:
            self.close_cursor()
            self._cur_is_auto = False


    ######################################
    # DBAPI 2.0 cursor/connection methods
    ######################################

    #
    # Not all of these methods are implemented by every DBMS.  Methods
    # that are particularly DBMS-dependent are noted, but if in doubt,
    # check using supports() before using.
    #

    def callproc(self, cur, procname, param=None, has_results=False):
        """
        Wrapper: call a stored procedure.
        If using the main cursor, and it has not been created yet,
        creates it.  If has_results is False, also closes it when
        finished.  If using fake autocommit (see autocommit()) and
        has_results is False, does a commit after the query.
        Returns False on error, otherwise True.
        Warning: this method is optional in DBAPI 2.0.  Test for its
        existence in your DBMS first with:
            if dbms_obj.supports('callproc'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            procname: the name of the stored procedure to call
            param: if not None, a sequence or mapping containing the
                   parameters to pass to the stored procedure
            has_results: if False, assume the stored procedure does not
                         return a result set, and close the cursor if it
                         was created automatically
        Dependencies:
            instance vars: cur, _fake_autocommit
            methods: check_supports_method(), auto_cursor(),
                     auto_close_cursor(), wrap_call(), commit()
            modules: (cur's module)
        """
        self.check_supports_method('callproc')
        self.auto_cursor()
        cur = cur if cur else self.cur
        if param is None:
            ret = self.wrap_call(cur.callproc, 'call stored procedure on',
                                 'calling stored procedure on',
                                 procname)[0]
        else:
            ret = self.wrap_call(cur.callproc, 'call stored procedure on',
                                 'calling stored procedure on', procname,
                                 param)[0]
        if not has_results:
            self.auto_close_cursor()
            if self._fake_autocommit:
                if not self.commit():
                    return False
        return ret


    def execute(self, cur, query, param=None, has_results=False):
        """
        Wrapper: execute a DBMS query.
        If using the main cursor, and it has not been created yet,
        creates it.  If has_results is False, also closes it when
        finished.  If using fake autocommit (see autocommit()) and
        has_results is False, does a commit after the query.
        Returns False on error, otherwise True.
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            query: the query to execute
            param: if not None, a sequence or mapping containing the
                   parameters to substitute into the query
            has_results: if False, assume the stored procedure does not
                         return a result set, and close the cursor if it
                         was created automatically
        Dependencies:
            instance vars: cur, _fake_autocommit
            methods: check_supports_method(), auto_cursor(),
                     auto_close_cursor(), wrap_call(), commit()
            modules: (cur's module)
        """
        self.check_supports_method('execute')
        self.auto_cursor()
        cur = cur if cur else self.cur
        if param is None:
            ret = self.wrap_call(cur.execute, 'execute query on',
                                 'executing query on', query)[0]
        else:
            ret = self.wrap_call(cur.execute, 'execute query on',
                                 'executing query on', query, param)[0]
        if not has_results:
            self.auto_close_cursor()
            if self._fake_autocommit:
                if not self.commit():
                    return False
        return ret


    def executemany(self, cur, query, param_seq, has_results=False):
        """
        Wrapper: execute a DBMS query on multiple parameter sets.
        If using the main cursor, and it has not been created yet,
        creates it.  If has_results is False, also closes it when
        finished.  If using fake autocommit (see autocommit()) and
        has_results is False, does a commit after the query.
        Returns False on error, otherwise True.
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            query: the query to execute
            param: if not None, a sequence of sequences or mappings
                   containing the parameters to substitute into the
                   query
            has_results: if False, assume the stored procedure does not
                         return a result set, and close the cursor if it
                         was created automatically
                         (in most cases, cur.executemany() can't return
                         results, but True is allowed here just in case)
        Dependencies:
            instance vars: cur, _fake_autocommit
            methods: check_supports_method(), auto_cursor(),
                     auto_close_cursor(), wrap_call(), commit()
            modules: (cur's module)
        """
        self.check_supports_method('executemany')
        self.auto_cursor()
        cur = cur if cur else self.cur
        ret = self.wrap_call(cur.executemany, 'execute queries on',
                             'executing queries on', query, param_seq)[0]
        if not has_results:
            self.auto_close_cursor()
            if self._fake_autocommit:
                if not self.commit():
                    return False
        return ret


    def fetchone(self, cur):
        """
        Wrapper: fetch the next row of a query result set.
        If using the main cursor, and it was automatically created, and
        the last row has been fetched, closes the cursor.  If using fake
        autocommit (see autocommit()), does a commit when the last row
        has been fetched.
        Returns a tuple: (success?, fetched_row)
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        Dependencies:
            instance vars: cur, _fake_autocommit
            methods: check_supports_method(), auto_close_cursor(),
                     wrap_call(), commit()
            modules: (cur's module)
        """
        self.check_supports_method('fetchone')
        cur = cur if cur else self.cur
        ret = self.wrap_call(cur.fetchone, 'retrieve data from',
                             'retrieving data from')
        if ret[1] is None:
            self.auto_close_cursor()
            # even SELECTs need COMMIT to prevent taking up resources;
            # see:
            # http://initd.org/psycopg/docs/connection.html#connection.autocommit
            if self._fake_autocommit:
                if not self.commit():
                    ret[0] = False
        return ret


    def fetchmany(self, cur, size=None):
        """
        Wrapper: fetch the next set of rows of a query result set.
        If using the main cursor, and it was automatically created, and
        the last row has been fetched, closes the cursor.  If using fake
        autocommit (see autocommit()), does a commit when the last row
        has been fetched.
        Returns a tuple: (success?, fetched_rows)
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            size: if not None, the number of rows to fetch
        Dependencies:
            instance vars: cur, _fake_autocommit
            methods: check_supports_method(), auto_close_cursor(),
                     wrap_call(), commit()
            modules: (cur's module)
        """
        self.check_supports_method('fetchmany')
        cur = cur if cur else self.cur
        if size is None:
            ret = self.wrap_call(cur.fetchmany, 'retrieve data from',
                                 'retrieving data from')
        else:
            ret = self.wrap_call(cur.fetchmany, 'retrieve data from',
                                 'retrieving data from', size)
        if not ret[1]:
            self.auto_close_cursor()
            # even SELECTs need COMMIT to prevent taking up resources;
            # see:
            # http://initd.org/psycopg/docs/connection.html#connection.autocommit
            if self._fake_autocommit:
                if not self.commit():
                    ret[0] = False
        return ret


    def fetchall(self, cur):
        """
        Wrapper: fetch all (remaining) rows of a query result set.
        If using the main cursor, and it was automatically created, and
        the last row has been fetched, closes the cursor.  If using fake
        autocommit (see autocommit()), does a commit.
        Returns a tuple: (success?, fetched_rows)
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        Dependencies:
            instance vars: cur, _fake_autocommit
            methods: check_supports_method(), auto_close_cursor(),
                     wrap_call(), commit()
            modules: (cur's module)
        """
        self.check_supports_method('fetchall')
        cur = cur if cur else self.cur
        ret = self.wrap_call(cur.fetchall, 'retrieve data from',
                             'retrieving data from')
        self.auto_close_cursor()
        # even SELECTs need COMMIT to prevent taking up resources;
        # see:
        # http://initd.org/psycopg/docs/connection.html#connection.autocommit
        if self._fake_autocommit:
            if not self.commit():
                ret[0] = False
        return ret


    def nextset(self, cur):
        """
        Wrapper: skip to the next query result set.
        Returns False on error, None if there are no more sets,
        otherwise True.
        Warning: this method is optional in DBAPI 2.0.  Test for its
        existence in your DBMS first with:
            if dbms_obj.supports('nextset'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        Dependencies:
            instance vars: cur
            methods: check_supports_method(), wrap_call()
            modules: (cur's module)
        """
        self.check_supports_method('nextset')
        cur = cur if cur else self.cur
        ret = self.wrap_call(cur.nextset, 'skip to the next set on',
                             'skipping to the next set on')
        if ret[1] is None:
            return None
        else:
            return ret[0]


    def setinputsizes(self, cur, sizes):
        """
        Wrapper: predefine parameter sizes.
        Returns False on error, otherwise True.
        Warning: this method is part of DBAPI 2.0, but is frequently
        omitted.  Test for its existence in your DBMS first with:
            if dbms_obj.supports('setinputsizes'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            sizes: a sequence of parameter sizes
        Dependencies:
            instance vars: cur
            methods: check_supports_method(), wrap_call()
            modules: (cur's module)
        """
        self.check_supports_method('setinputsizes')
        cur = cur if cur else self.cur
        return self.wrap_call(cur.setinputsizes, 'set input sizes on',
                              'setting input sizes on', sizes)[0]


    def setoutputsize(self, cur, size, column=None):
        """
        Wrapper: set a large-column buffer size.
        Returns False on error, otherwise True.
        Warning: this method is part of DBAPI 2.0, but is frequently
        omitted.  Test for its existence in your DBMS first with:
            if dbms_obj.supports('setoutputsize'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            size: the column-buffer size
            column: if not None, the index of the column in the result
                    sequence
        Dependencies:
            instance vars: cur
            methods: check_supports_method(), wrap_call()
            modules: (cur's module)
        """
        self.check_supports_method('setoutputsize')
        cur = cur if cur else self.cur
        if column is None:
            return self.wrap_call(cur.setoutputsize, 'set output size on',
                                  'setting output size on', size)[0]
        else:
            return self.wrap_call(cur.setoutputsize, 'set output size on',
                                  'setting output size on', size, column)[0]


    def commit(self):
        """
        Wrapper: commit any pending transaction.
        Applies to all of the connection's cursors.
        Returns False on error, otherwise True.
        Dependencies:
            instance vars: conn
            methods: check_supports_method(), wrap_call()
            modules: (conn's module)
        """
        self.check_supports_method('commit')
        return self.wrap_call(self.conn.commit, 'commit transaction on',
                              'committing transaction on')[0]


    def rollback(self):
        """
        Wrapper: roll back any pending transaction.
        Applies to all of the connection's cursors.
        Returns False on error, otherwise True.
        Warning: this method is optional in DBAPI 2.0.  Test for its
        existence in your DBMS first with:
            if dbms_obj.supports('rollback'):
                ...
        Dependencies:
            instance vars: conn
            methods: check_supports_method(), wrap_call()
            modules: (conn's module)
        """
        self.check_supports_method('rollback')
        return self.wrap_call(self.conn.rollback,
                              'roll back transaction on',
                              'rolling back transaction on')[0]


    ###########################
    # DBAPI extension wrappers
    ###########################

    def autocommit(self, what=None):

        """
        Get or set the autocommit status of a DBMS connection.

        If what is True or False, returns True on success, False on
        error.  If what is None, returns True/False, or None on error.

        If the DBMS does not support autocommit, simulates it; see the
        call and fetch wrappers, above.

        DBMSes that support autocommit must have 'autocommit' in
        _SUPPORTS, and implement the _autocommit() internal method.

        Parameters:
            what: if True, turn autocommit on; if False, turn it off;
                  if None, return the current status

        Dependencies:
            instance vars: _fake_autocommit
            methods: supports(), _autocommit()

        """

        # built-in support?
        if self.supports('autocommit'):
            return self._autocommit(what)

        if what is None:
            return self._fake_autocommit

        self._fake_autocommit = what
        return True


    ##################
    # nori extensions
    ##################

    def get_db_list(self, cur):
        """
        Get the list of databases from a DBMS.
        Returns a tuple: (success?, fetched_rows)
        May not be possible or even coherent for all DBMSes; subclasses
        should override or delete this method.
        Warning: test for its existence in your DBMS first with:
            if dbms_obj.supports('get_db_list'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        """
        self.check_supports_method('get_db_list')
        return (False, None)  # no generic version of this function


    def change_db(self, cur, db_name):
        """
        Change the current database used by a cursor.
        Returns False on error, otherwise True.
        May not be possible or even coherent for all DBMSes; subclasses
        should override or delete this method.
        Warning: test for its existence in your DBMS first with:
            if dbms_obj.supports('change_db'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
            db_name: the database to change to
        """
        self.check_supports_method('change_db')
        return False  # no generic version of this function


    def get_table_list(self, cur):
        """
        Get the list of tables in the current database.
        Returns a tuple: (success?, fetched_rows)
        May not be possible or even coherent for all DBMSes; subclasses
        should override or delete this method.
        Warning: test for its existence in your DBMS first with:
            if dbms_obj.supports('get_table_list'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        """
        self.check_supports_method('get_table_list')
        return (False, None)  # no generic version of this function


    def fetchone_generator(self, cur):
        """
        Wrapper: fetchone() as a generator.
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        Dependencies:
            instance methods: fetchone()
        """
        while True:
            f_ret = self.fetchone(cur)
            if not f_ret[0] or (f_ret[1] is None):
                break  # remember, fetchone() includes error handling
            yield f_ret[1]


    def get_last_id(self, cur):
        """
        Get the last auto-increment ID inserted into the database.
        Returns a tuple: (success?, last_id)
        May not be possible or even coherent for all DBMSes; subclasses
        should override or delete this method.
        Warning: test for its existence in your DBMS first with:
            if dbms_obj.supports('get_last_id'):
                ...
        Parameters:
            cur: the cursor to use; if None, the main cursor is used
        """
        self.check_supports_method('get_last_id')
        return (False, None)  # no generic version of this function

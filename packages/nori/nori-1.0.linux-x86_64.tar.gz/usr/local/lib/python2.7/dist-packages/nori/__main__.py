#!/usr/bin/env python


"""
DOCSTRING CONTENTS:
-------------------

    1) About and Requirements
    2) General Information
    3) Usage in Scripts
    4) Submodule Creation


1) ABOUT AND REQUIREMENTS:
--------------------------

    This is the nori library for wrapping scripts.  It provides tools
    such as powerful lockfile checking, logging, command-line
    processing, and config setting validation, and is particularly
    helpful for scripts that need to be run from cron with minimal
    intervention and maximal stability (although it can also be helpful
    in other cases.)

    It was originally factored out of the Aeolus backup script, then
    ported to Python; the original and the port are by Daniel Malament.

    The library requires Python 2.7/3.2, and will exit the script upon
    import (with an error message) if this requirement is not met.

    Submodules may have additional requirements; see their docstrings
    for more information.


2) GENERAL INFORMATION:
-----------------------

    Many aspects of the library are self-documenting; to get
    information, options can be supplied to either the package itself,
    (with, e.g., 'python -m nori OPTIONS'), or to scripts that use the
    library.

    For command-line usage information, run with '--help'.

    For config setting information, run with '-n create' or
    '-n createall'.

    For exit value information, run with 'exitvals'.

    For license information, run with 'license' or see the LICENSE file.

    In scripts that use the library, the output from these commands will
    include script-specific changes.

    For more end-user information, see the USAGE file.


3) USAGE IN SCRIPTS:
--------------------

    (These are some pointers for using the library; however, there are
    many features and options left out.  See the comments and
    docstrings, below, for more information.)

    To use the library to wrap a task, the minimum setup that should be
    done is as follows:
        * redefine task_article, task_name, and tasks_name
        * redefine license_str
        * add to config_settings, as necessary, and add a function to
          validate_config_hooks
        * add a function to run_mode_hooks

    In most cases, these will also be necessary:
        * add to exitvals
        * redefine default_config_files
        * copy and edit/expand the USAGE file, replacing 'nori' with the
          name of the script

    To use the output log feature:
        * run config_settings_no_print_output_log(False)
        * set these (in most cases):
          config_settings['exec_path']['no_print'] = False
          config_settings['log_cmds']['no_print'] = False

    To add command-line modes:
        * add to script_modes


4) SUBMODULE CREATION:
----------------------

    Adding a submodule will typically involve:

        * adding to exitvals
        * adding to supported_features
        * testing functionality and adding to available_features
        * adding to config_settings and adding a function to
          validate_config_hooks (and possibly adding to bogus_config
          and apply_default_hooks)
        * expanding the USAGE file
        * adding the submodule to the imports, below

    This is not an exhaustive list; see, for example, the other hooks
    in core.py.

    Note that references from one submodule to another should be done
    with:
        from . import submodule
        submodule.function()
    so that it's clear which function is in which module.  However, this
    module (__main__) should put all of the other submodules' namespaces
    directly in its own, so that scripts that use the library can do:
        import nori
        nori.function()
    regardless of which module the function is in.  (See the imports
    section, below.)  This means that there should not be any name
    clashes between any of the submodules.

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


###############
# this package
###############

#
# add all submodules here; the global namespace of this module will be
# accessible as 'nori' after doing 'import nori' in a script
#
# use absolute imports (e.g., .core), and import *
#

from .core import *
from .ssh import *
from .dbms import *


########################################################################
#                           RUN STANDALONE
########################################################################

def main():
    process_command_line()

if __name__ == '__main__':
    main()

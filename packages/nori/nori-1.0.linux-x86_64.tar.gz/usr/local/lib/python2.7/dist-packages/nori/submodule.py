#!/usr/bin/env python


"""
This is the SUBMODULE submodule for the nori library; see __main__.py
for license and usage information.


DOCSTRING CONTENTS:
-------------------

    1) About and Requirements
    2) API Variables
    3) API Functions
    4) API Classes
    5) Usage in Scripts
    6) Modification Notes


1) ABOUT AND REQUIREMENTS:
--------------------------


2) API VARIABLES:
-----------------


3) API FUNCTIONS:
-----------------


4) API CLASSES:
---------------


5) USAGE IN SCRIPTS:
--------------------


6) MODIFICATION NOTES:
----------------------

"""


########################################################################
#                             MAIN IMPORTS
########################################################################
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


#########
# add-on
#########

try:
    import paramiko
except ImportError:
    pass  # see the status and meta variables section


###############
# this package
###############

from . import core


########################################################################
#                         PYTHON VERSION CHECK
########################################################################

# minimum versions for the imports and code below
core.pyversion_check(7, 2)


########################################################################
#                           DEFERRED IMPORTS
########################################################################


########################################################################
#                              VARIABLES
########################################################################

############
# constants
############


##################
# status and meta
##################

# exit values
core.exitvals['submodule'] = dict(
    num=999,
    descr=(
'''
error doing submodule stuff
'''
    ),
)

# supported / available features
core.supported_features['submodule'] = 'submodule stuff'
if 'paramiko' in sys.modules:
    core.available_features.append('submodule')


#########################
# configuration settings
#########################

#
# available config settings
#

if 'submodule' in core.available_features:
    core.config_settings['submodule_heading'] = dict(
        heading='Submodule',
    )

    core.config_settings['submodule_setting'] = dict(
        descr=(
'''
Submodule stuff.
'''
        ),
        default='submodule stuff',
        requires=['submodule'],
    )


#############
# hook lists
#############


############
# resources
############


########################################################################
#                               CLASSES
########################################################################
########################################################################
#                        FUNCTIONS AND CLASSES
########################################################################
########################################################################
#                              FUNCTIONS
########################################################################

#####################################
# startup and config file processing
#####################################

def validate_config():
    """
    Validate submodule-specific config settings.
    """
    pass


####################
# [submodule stuff]
####################


########################################################################
#                           RUN STANDALONE
########################################################################

def main():
    core.process_command_line()

if __name__ == '__main__':
    main()

#!/usr/bin/python3

"""
Verify HTCondor-CE configuration before service startup
"""

import os
import re
import sys

from collections import defaultdict


def error(msg):
    """Exit with error 'msg'
    """
    sys.exit("ERROR: " + msg)


def warn(msg):
    """Print warning 'msg'
    """
    print("WARNING: " + msg)


def debug(msg):
    """Print debug 'msg'
    """
    print("DEBUG: " + msg)


# Verify that the HTCondor Python bindings are in the PYTHONPATH
try:
    import htcondor2 as htcondor
except ImportError:
    error("Could not load HTCondor Python bindings. "
          + "Please ensure that the 'htcondor' and 'classad' are in your PYTHONPATH")


def main():
    """Main function
    """
    is_osg = htcondor.param.get('OSG_CONFIGURE_PRESENT', '').lower() in ('true', 'yes', '1')

    # Create dict whose values are lists of ads specified in the relevant JOB_ROUTER_* variables
    jr_transforms = {key : value for key, value in htcondor.param.items() if key.startswith("JOB_ROUTER_ROUTE_")}

    # If JOB_ROUTER_ROUTE_<name> rules are defined, verify that these transforms exist
    if jr_transforms:
        route_names = htcondor.param.get("JOB_ROUTER_ROUTE_NAMES", "")
        for name in re.split(r'[, \t]+', route_names):
            route_def = htcondor.param.get(f"JOB_ROUTER_ROUTE_{name}", "")
            if not route_def:
                warn(f"The route {name} is specified in JOB_ROUTER_ROUTE_NAMES, but no corresponding JOB_ROUTER_ROUTE_{name} exists")

    # Warn users on OSG CEs if osg-configure has not been run
    if is_osg:
        try:
            htcondor.param['OSG_CONFIGURED']
        except KeyError:
            warn("osg-configure has not been run, degrading the functionality " +
                 "of the CE. Please run 'osg-configure -c' and restart condor-ce.")

    # Ensure that HTCondor back-ends have QUEUE_SUPER_USER_MAY_IMPERSONATE set correctly
    # and that JOB_ROUTER_SCHEDD2_SPOOL matches the back-end HTCondor's SPOOL
    try:
        htcondor.param['JOB_ROUTER_SCHEDD2_NAME']
    except KeyError:
        pass
    else:
        ce_spool2 = htcondor.param.get('JOB_ROUTER_SCHEDD2_SPOOL', '')
        os.environ['CONDOR_CONFIG'] = '/etc/condor/condor_config'
        htcondor.reload_config()
        if ce_spool2 != htcondor.param.get('SPOOL', ''):
            error("JOB_ROUTER_SCHEDD2_SPOOL in the HTCondor-CE configuration does not match SPOOL in the HTCondor configuration.")
        su_attr = 'QUEUE_SUPER_USER_MAY_IMPERSONATE'
        if htcondor.param.get(su_attr, '') != '.*':
            error("HTCondor batch system is improperly configured for use with HTCondor CE. "
                  + "Please verify that '%s = .*' is set in your HTCondor configuration." % su_attr)
    finally:
        os.environ['CONDOR_CONFIG'] = '/etc/condor-ce/condor_config'


if __name__ == "__main__":
    main()

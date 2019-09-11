#!/bin/env python

"""
Verify HTCondor-CE configuration before service startup
"""

import os
import re
import sys


def error(msg):
    sys.exit("ERROR: " + msg)


def warn(msg):
    print "WARNING: " + msg


def condorpp(param):
    syntax = [';', '[', ']']
    out = "".join(param.split())  # strip all whitespace
    for elem in syntax:
        out = out.replace(elem, elem+'\n')  # re-print
    return out


def malformedQueues(parsedAds, unparsedAds):
    allqueues = []
    for line in condorpp(unparsedAds).split('\n'):
        if 'name' in line:
            allqueues.append(line.split('=')[1].split(';')[0].strip('\"'))

    goodqueues = []
    for ad in parsedAds:
        goodqueues.append(ad['name'])

    return list(set(allqueues) - set(goodqueues))



# Verify that the HTCondor Python bindings are in the PYTHONPATH
try:
    import classad
    import htcondor
except ImportError:
    error("Could not load HTCondor Python bindings. "
          + "Please ensure that the 'htcondor' and 'classad' are in your PYTHONPATH")

is_osg = htcondor.param.get('OSG_CONFIGURE_PRESENT', '').lower() in ('true', 'yes', '1')

# Create dict whose values are lists of ads specified in the relevant JOB_ROUTER_* variables
JOB_ROUTER_CONFIG = {}
for attr in ['JOB_ROUTER_DEFAULTS', 'JOB_ROUTER_ENTRIES']:
    try:
        ads = classad.parseAds(htcondor.param[attr])
    except KeyError:
        error("Missing required %s configuration value" % attr)
    JOB_ROUTER_CONFIG[attr] = list(ads)  # store the ads (iterating through ClassAdStringIterator consumes them)

# Verify job routes. classad.parseAds() ignores malformed ads so we have to compare the unparsed string to the
# parsed string, counting the number of ads by proxy: the number of opening square brackets, "["
for attr, ads in JOB_ROUTER_CONFIG.items():
    if htcondor.param[attr].count('[') != len(ads):
        print "Could not read %s in the HTCondor CE configuration. Please verify syntax correctness" % attr
        error("The following appear to be malformed: %s" % ", ".join(malformedQueues(ads, htcondor.param[attr])))

# Find all eval_set_ attributes in the JOB_ROUTER_DEFAULTS
EVAL_SET_DEFAULTS = set([x.lstrip('eval_') for x in JOB_ROUTER_CONFIG['JOB_ROUTER_DEFAULTS'][0].keys()
                         if x.startswith('eval_set_')])

# Find all default_ attributes used in expressions in the JOB_ROUTER_DEFAULTS
DEFAULT_ATTR = set([re.sub(r'.*(default_\w*).*', 'eval_set_\\1', str(x))
                    for x in JOB_ROUTER_CONFIG['JOB_ROUTER_DEFAULTS'][0].values()
                    if isinstance(x, classad.ExprTree) and str(x).find('default_') != -1])

for entry in JOB_ROUTER_CONFIG['JOB_ROUTER_ENTRIES']:
    # Warn users if they've set_ attributes that would be overriden by eval_set in the JOB_ROUTER_DEFAULTS
    overriden_attr = EVAL_SET_DEFAULTS.intersection(set(entry.keys()))
    if overriden_attr:
        warn("%s in JOB_ROUTER_ENTRIES will be overriden by the JOB_ROUTER_DEFAULTS."
             % ', '.join(overriden_attr)
             + " Use the 'eval_set_' prefix instead.")

    # Ensure that users don't set the job environment in the Job Router
    if is_osg and any(x.endswith('environment') for x in entry.keys()):
        error("Do not use the Job Router to set the environment. Place variables under "
              + "[Local Settings] in /etc/osg/config.d/40-localsettings.ini")

    # Warn users about eval_set_ default attributes in the ENTRIES since their
    # evaluation may occur after the eval_set_ expressions containg them in the
    # JOB_ROUTER_DEFAULTS
    no_effect_attr = DEFAULT_ATTR.intersection(set([x for x in entry.keys() if x.startswith('eval_set_')]))
    if no_effect_attr:
        warn("%s in JOB_ROUTER_ENTRIES " % ', '.join(no_effect_attr)
             + "may not have any effect. Use the 'set_' prefix instead.")

# Warn users on OSG CEs if osg-configure has not been run
if is_osg:
    try:
        htcondor.param['OSG_CONFIGURED']
    except KeyError:
        warn("osg-configure has not been run, degrading the functionality " +
             "of the CE. Please run 'osg-configure -c' and restart condor-ce.")

# Ensure that HTCondor back-ends have QUEUE_SUPER_USER_MAY_IMPERSONATE set correctly
try:
    htcondor.param['JOB_ROUTER_SCHEDD2_NAME']
except KeyError:
    pass
else:
    os.environ['CONDOR_CONFIG'] = '/etc/condor/condor_config'
    htcondor.reload_config()
    su_attr = 'QUEUE_SUPER_USER_MAY_IMPERSONATE'
    if htcondor.param.get(su_attr, '') != '.*':
        error("HTCondor batch system is improperly configured for use with HTCondor CE. "
              + "Please verify that '%s = .*' is set in your HTCondor configuration." % su_attr)
finally:
    os.environ['CONDOR_CONFIG'] = '/etc/condor-ce/condor_config'

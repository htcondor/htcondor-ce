#!/bin/env python

"""
Verify HTCondor-CE configuration before service startup
"""

import re
import sys

# Verify that the HTCondor Python bindings are in the PYTHONPATH
try:
    import classad
    import htcondor
except ImportError:
    sys.exit("ERROR: Could not load HTCondor Python bindings. " + \
             "Please ensure that the 'htcondor' and 'classad' are in your PYTHONPATH")

# Create dict whose values are lists of ads specified in the relevant JOB_ROUTER_* variables
JOB_ROUTER_CONFIG = {}
for attr in ['JOB_ROUTER_DEFAULTS', 'JOB_ROUTER_ENTRIES']:
    ads = classad.parseAds(htcondor.param[attr])
    JOB_ROUTER_CONFIG[attr] = list(ads) # store the ads (iterating through ClassAdStringIterator consumes them)

# Verify job routes. classad.parseAds() ignores malformed ads so we have to compare the unparsed string to the
# parsed string, counting the number of ads by proxy: the number of opening square brackets, "["
for attr, ads in JOB_ROUTER_CONFIG.items():
    if htcondor.param[attr].count('[') != len(ads):
        sys.exit("ERROR: Could not read %s in the HTCondor CE configuration. Please verify syntax correctness" % attr)

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
        print "WARNING: %s in JOB_ROUTER_ENTRIES will be overriden by the JOB_ROUTER_DEFAULTS." \
            % ', '.join(overriden_attr) \
            + " Use the 'eval_set_' prefix instead."

    # Ensure that users don't set the job environment in the Job Router
    if [x for x in entry.keys() if x.endswith('environment')]:
        sys.exit("ERROR: Do not use the Job Router to set the environment. Place variables under " +\
                 "[Local Settings] in /etc/osg/config.d/40-localsettings.ini")

    # Warn users about eval_set_ default attributes in the ENTRIES since their
    # evaluation may occur after the eval_set_ expressions containg them in the
    # JOB_ROUTER_DEFAULTS
    no_effect_attr = DEFAULT_ATTR.intersection(set([x for x in entry.keys() if x.startswith('eval_set_')]))
    if no_effect_attr:
        print "WARNING: %s in JOB_ROUTER_ENTRIES " % ', '.join(no_effect_attr) + \
            "may not have any effect. Use the 'set_' prefix instead."

# Warn users if osg-configure has not been run
try:
    htcondor.param['OSG_CONFIGURED']
except KeyError:
    print "WARNING: osg-configure has not been run, degrading the functionality " + \
        "of the CE. Please run 'osg-configure -c' and restart condor-ce."

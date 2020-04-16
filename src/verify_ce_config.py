#!/bin/env python

"""
Verify HTCondor-CE configuration before service startup
"""

import os
import re
import sys


def error(msg):
    """Exit with error 'msg'
    """
    sys.exit("ERROR: " + msg)


def warn(msg):
    """Print warning 'msg'
    """
    print "WARNING: " + msg


def parsed_route_names(entries_config):
    """Return names of job routes that can be parsed as proper ClassAds
    """
    return [x['Name'] for x in classad.parseAds(entries_config)]


def malformed_entries(entries_config):
    """Find all unparseable router entries based on the raw JOB_ROUTER_ENTRIES configuration
    """
    unparsed_names = [x.replace('"', '')
                      for x in re.findall(r'''name\s*=\s*["'](\w+)["']''',
                                          entries_config,
                                          re.IGNORECASE)]
    parsed_names = parsed_route_names(entries_config)

    return set(unparsed_names) - set(parsed_names)


# Verify that the HTCondor Python bindings are in the PYTHONPATH
try:
    import classad
    import htcondor
except ImportError:
    error("Could not load HTCondor Python bindings. "
          + "Please ensure that the 'htcondor' and 'classad' are in your PYTHONPATH")


def main():
    """Main function
    """
    is_osg = htcondor.param.get('OSG_CONFIGURE_PRESENT', '').lower() in ('true', 'yes', '1')

    # Create dict whose values are lists of ads specified in the relevant JOB_ROUTER_* variables
    parsed_jr_ads = {}
    for attr in ['JOB_ROUTER_DEFAULTS', 'JOB_ROUTER_ENTRIES']:
        try:
            config_val = htcondor.param[attr]
        except KeyError:
            error("Missing required %s configuration value" % attr)

        # store the ads (iterating through ClassAdStringIterator consumes them)
        parsed_jr_ads[attr] = list(classad.parseAds(config_val))

        # If JRD or JRE can't be parsed, the job router can't function
        if not parsed_jr_ads[attr]:
            error("Could not read %s in the HTCondor-CE configuration." % attr)

        if attr == "JOB_ROUTER_ENTRIES":
            # Warn about routes we can find in the config that don't result in valid ads
            malformed_entry_names = malformed_entries(config_val)
            if malformed_entry_names:
                warn("Could not read JOB_ROUTER_ENTRIES in the HTCondor-CE configuration. " +
                     "Failed to parse the following routes: %s"
                     % ', '.join(malformed_entry_names))

            # Warn about routes specified by JOB_ROUTER_ROUTE_NAMES that don't appear in the parsed JRE.
            # The job router can function this way but it's likely a config error
            route_order = htcondor.param.get('JOB_ROUTER_ROUTE_NAMES', '')
            if route_order:
                missing_route_def = set(route_order).difference(set(parsed_route_names(config_val)))
                if missing_route_def:
                    warn("The following are specified in JOB_ROUTER_ROUTE_NAMES "
                         "but cannot be found in JOB_ROUTER_ENTRIES: %s"
                         % ', '.join(missing_route_def))

    # Find all eval_set_ attributes in the JOB_ROUTER_DEFAULTS
    eval_set_defaults = set([x.lstrip('eval_') for x in parsed_jr_ads['JOB_ROUTER_DEFAULTS'][0].keys()
                             if x.startswith('eval_set_')])

    # Find all default_ attributes used in expressions in the JOB_ROUTER_DEFAULTS
    default_attr = set([re.sub(r'.*(default_\w*).*', 'eval_set_\\1', str(x))
                        for x in parsed_jr_ads['JOB_ROUTER_DEFAULTS'][0].values()
                        if isinstance(x, classad.ExprTree) and str(x).find('default_') != -1])

    for entry in parsed_jr_ads['JOB_ROUTER_ENTRIES']:
        # Warn users if they've set_ attributes that would be overriden by eval_set in the JOB_ROUTER_DEFAULTS
        overriden_attr = eval_set_defaults.intersection(set(entry.keys()))
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
        no_effect_attr = default_attr.intersection(set([x for x in entry.keys() if x.startswith('eval_set_')]))
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


if __name__ == "__main__":
    main()

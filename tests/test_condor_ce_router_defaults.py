#/usr/bin/env python
"""Unit tests for condor_ce_router_defaults"""

import imp
import os
import re
import unittest

EXTATTR_FILE_PATH = 'extattr_table.txt'
UID_FILE_PATH = 'uid_table.txt'
DEFAULTS_PATH = os.path.join('..', 'src', 'condor_ce_router_defaults')

defaults = imp.load_source('condor_ce_router_defaults', DEFAULTS_PATH)

class TestDefaults(unittest.TestCase):
    """Unit tests for condor_ce_router_defaults"""

    def test_parse_extattr(self):
        """Verify extattr_table.txt returns expected list of tuples"""
        dn_prefix = "\\/DC=com\\/DC=DigiCert-Grid\\/O=Open\\ Science\\ Grid\\/OU=People\\/CN="
        extattr = defaults.parse_extattr(EXTATTR_FILE_PATH)
        expected_extattr = [('\\/fermilab\\/Role=pilot', 'group_fermilab'),
                            ('%sMichael\\ Johnson\\ 2274' % dn_prefix, 'group_des'),
                            ('%sBrian\\ Lin\\ 1047' % dn_prefix, 'group_test')]
        self.assertEqual(extattr, expected_extattr, '\nExpected: %s\n\nGot: %s\n' % (expected_extattr, extattr))

    def test_parse_uids(self):
        """Verify uid_table.txt returns expected list of tuples"""
        uids = defaults.parse_uids(UID_FILE_PATH)
        expected_uids = [('uscms02', 'TestGroup'), ('osg', 'other.osgedu')]
        self.assertEqual(uids, expected_uids, '\nExpected: %s\n\nGot: %s\n' % (expected_uids, uids))

    def test_set_accounting_group(self):
        """Verify classad functions have matching closing parentheses"""
        acct_grp_expr = defaults.set_accounting_group(UID_FILE_PATH, EXTATTR_FILE_PATH)
        num_classad_fn = len(re.findall(r'[(?:ifThenElse)(?:regexp)(?:strcat)]\(', acct_grp_expr))
        num_closing_parens = len(re.findall(r'\)', acct_grp_expr))
        self.assertEqual(num_classad_fn, num_closing_parens,
                         'Mismatched "ifThenElse_fn(" + "regexp(" + "strcat(" statements (%s) and closing parentheses (%s)'
                         % (num_classad_fn, num_closing_parens))

#!/usr/bin/env python
"""Unit tests for verify_ce_config.py"""

import imp
import os
import unittest

GOOD_ROUTES = '''[
  Name = "GoodRoute1";
  TargetUniverse = 5;
]
[
  Name = "GoodRoute2";
  TargetUniverse = 5;
]
'''

BAD_ROUTES = '''[
  Name = "GoodRoute";
  TargetUniverse = 5;
]
[
  Name = "MissingSemicolon"
  TargetUniverse = 5;
]
[
  Name = 'SingleQuotedValue';
  TargetUniverse = 5;
]
[
  Name = "MissingClosingBracket";
[
  Name = "AfterMissingClosingBracket";
  TargetUniverse = 5;
]
'''

VERIFY_PATH = os.path.join('..', 'src', 'verify_ce_config.py')
verify = imp.load_source('verify_ce_config', VERIFY_PATH)


class TestVerifyConfig(unittest.TestCase):
    """Unit tests for verify_ce_config.py"""

    def test_good_parsed_route_names(self):
        """Verify that all routes show up in properly formatted JOB_ROUTER_ENTRIES
        """
        self.assertEqual(verify.parsed_route_names(GOOD_ROUTES), ['GoodRoute1', 'GoodRoute2'])

    def test_bad_parsed_route_names(self):
        """Verify that only properly formatted routes in a JOB_ROUTER_ENTRIES containing bad routes
        """
        self.assertEqual(verify.parsed_route_names(BAD_ROUTES), ['GoodRoute'])

    def test_good_malformed_entries(self):
        """Verify that no malformed entries are found for properly formatted JOB_ROUTER_ENTRIES
        """
        self.assertEqual(verify.malformed_entries(GOOD_ROUTES), set([]))

    def test_bad_malformed_entries(self):
        """Verify that route names are found for malformed JOB_ROUTER_ENTRIES
        """
        malformed_entry_names = verify.malformed_entries(BAD_ROUTES)
        self.assertEqual(malformed_entry_names,
                         set(['MissingSemicolon',
                              'SingleQuotedValue',
                              'MissingClosingBracket',
                              'AfterMissingClosingBracket']))

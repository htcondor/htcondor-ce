#!/usr/bin/python3
"""Run HTCondor-CE unit tests"""

import glob
import unittest
import sys

TESTS = [test[:-3] for test in glob.glob('test*.py')]
SUITE = unittest.TestLoader().loadTestsFromNames(TESTS)
RESULTS = unittest.TextTestRunner(verbosity=2).run(SUITE)

if not RESULTS.wasSuccessful():
    sys.exit(1)



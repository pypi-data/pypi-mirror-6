###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 4014 2014-04-04 02:26:01Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt'),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

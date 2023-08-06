# -*- coding: utf-8 -*-
"""

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'))
)
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class IncotermTestCase(unittest.TestCase):
    '''
    Test Incoterm module.
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('incoterm')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('incoterm')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()


def suite():
    """
    Define suite
    """
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(IncotermTestCase)
    )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

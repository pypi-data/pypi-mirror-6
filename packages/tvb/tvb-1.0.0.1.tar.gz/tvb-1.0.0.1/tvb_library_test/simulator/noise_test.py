# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Test for tvb.simulator.noise module

.. moduleauthor:: Paula Sanz Leon <sanzleon.paula@gmail.com>

"""

if __name__ == "__main__":
    from tvb_library_test import setup_test_console_env
    setup_test_console_env()
    
import unittest

from tvb_library_test.base_testcase import BaseTestCase
from tvb.simulator import noise
from tvb.datatypes import equations

class NoiseTest(BaseTestCase):
    def test_stream(self):
        noise_stream = noise.RandomStream()
        self.assertEqual(noise_stream.init_seed, 42)


    def test_additive(self):
        noise_additive = noise.Additive()
        self.assertEqual(noise_additive.ntau,  0.0)
        
        
    def test_multiplicative(self):
        noise_multiplicative = noise.Multiplicative()
        self.assertEqual(noise_multiplicative.ntau,  0.0)
        self.assertTrue(isinstance(noise_multiplicative.b, equations.Linear))
    
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(NoiseTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 
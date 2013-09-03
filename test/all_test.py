import unittest

import animation_test
import model_test

suite = unittest.TestSuite()
suite.addTest(animation_test.suite)
suite.addTest(model_test.suite)

unittest.TextTestRunner(verbosity=2).run(suite)

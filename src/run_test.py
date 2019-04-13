from tests import test_line_follower
import unittest

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_line_follower.TestSimpleLineFollower)

    unittest.TextTestRunner().run(test_suite)

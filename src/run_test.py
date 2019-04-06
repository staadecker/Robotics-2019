from tests import test_movement_controller
import unittest

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_movement_controller.TestMovementController)

    unittest.TextTestRunner().run(test_suite)

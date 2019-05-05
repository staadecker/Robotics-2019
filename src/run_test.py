from tests import test_line_follower
import unittest
import main

if __name__ == '__main__':
    # test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_line_follower.TestSimpleLineFollower)
    #
    # unittest.TextTestRunner().run(test_suite)
    main = main.Main()
    main.prepare()
    main.actions.go_to_drop_off_fibre()
    main.actions.drop_off_fibre()
    main.robot.end()


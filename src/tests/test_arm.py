import unittest
from lib import arm_controller
from tests import util


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestArm(unittest.TestCase):

    def setUp(self):
        self.arm = arm_controller.ArmController()

    def test_raise(self):
        self.arm.raise_arm()
        util.get_user_answer("Did the claw raise?")

    def test_lower_to_device(self):
        self.arm.run_arm_to_device()
        util.get_user_answer("Did the claw lower to device height?")


if __name__ == '__main__':
    unittest.main()

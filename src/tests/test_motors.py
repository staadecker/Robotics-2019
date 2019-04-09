import unittest
from lib import motors
from tests import util


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestArm(unittest.TestCase):

    def setUp(self):
        self.arm = motors.ArmController()

    def test_raise(self):
        self.arm.raise_arm()
        util.get_user_answer("Did the claw raise?")

    def test_lower_to_device(self):
        self.arm.lower_to_device()
        util.get_user_answer("Did the claw lower to device height?")


if __name__ == '__main__':
    unittest.main()


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestMovementController(unittest.TestCase):
    def setUp(self):
        self.movement_controller = motors.Mover()

    def test_move_straight(self):
        self.movement_controller.travel(300)
        self.assertTrue(util.get_user_answer("Did the robot move forward 30cm?"))

    def test_rotate(self):
        self.movement_controller.rotate(degrees=360)
        self.assertTrue(util.get_user_answer("Did the robot rotate 360 degrees clockwise?"))

    def test_rotate_counter_clockwise(self):
        self.movement_controller.rotate(degrees=360, clockwise=False)
        self.assertTrue(util.get_user_answer("Did the robot rotate 360 degrees counter-clockwise?"))

    def test_arc(self):
        self.movement_controller.rotate(degrees=90, arc_radius=100)
        self.assertTrue(util.get_user_answer("Did the robot rotate 90 on a path with arc 10cm?"))

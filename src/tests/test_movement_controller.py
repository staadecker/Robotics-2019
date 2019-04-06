import unittest
from lib import movement_controller
from tests import util


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestMovementController(unittest.TestCase):
    def setUp(self):
        self.movement_controller = movement_controller.MovementController()

    def test_move_straight(self):
        self.movement_controller.travel(30)
        self.assertTrue(util.get_user_answer("Did the robot move forward 10cm?"))

    def test_rotate(self):
        self.movement_controller.rotate(360)
        self.assertTrue(util.get_user_answer("Did the robot rotate 360 degrees counterclockwise?"))


if __name__ == '__main__':
    unittest.main()

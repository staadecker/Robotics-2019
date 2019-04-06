import unittest
import main
from lib import line_follower
from tests import util


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestLineFollower(unittest.TestCase):
    def setUp(self) -> None:
        self.robot = main.Robot()
        self.line_follower = line_follower.LineFollower(self.robot.movement_controller, self.robot.left_color_sensor,
                                                        self.robot.right_color_sensor)

    def test_timed_follow(self):
        input("Press enter when the robot is on a black line")
        self.line_follower.follow_on_left(line_follower.StopAfterTime(5000))
        self.assertTrue(util.get_user_answer("Did the robot follow the line for 5 seconds?"))

    def test_timed_follow_on_right(self):
        input("Press enter when the robot is on a black line")
        self.line_follower.follow_on_right(line_follower.StopAfterTime(5000))
        self.assertTrue(util.get_user_answer("Did the robot follow the line on the right for 5 seconds?"))

    def test_cross_follow(self):
        input("Press enter when the robot is on a black line with a right T-junction")
        self.line_follower.follow_on_left(line_follower.StopAtCrossLine(self.robot.right_color_sensor))
        self.assertTrue(util.get_user_answer("Did the robot follow the line until a T-junction on the right?"))

    def test_follow_merge(self):
        input("Press enter when the robot is on a black line with a right T-junction")

        self.line_follower.follow_on_left(
            line_follower.StopAfterMultiple(
                [line_follower.StopAtCrossLine(self.robot.right_color_sensor),
                 line_follower.StopAfterTime(1000)]
            )
        )

        self.assertTrue(util.get_user_answer("Did the robot follow the line 1 second passed a right T-junction?"))

    def test_cross_multiple(self):
        input("Press enter when the robot is on a black line with a 4 left T-junction")
        self.line_follower.follow_on_right(
            line_follower.get_stop_after_x_intersections(3, self.robot.left_color_sensor))
        self.assertTrue(util.get_user_answer("Did the robot follow the line until reaching the 4th left intersection?"))


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestSimpleLineFollower(unittest.TestCase):
    def test_run_forever(self):
        self.robot = main.Robot()
        self.line_follower = line_follower.LineFollower(self.robot.movement_controller, self.robot.left_color_sensor,
                                                        self.robot.right_color_sensor)
        self.line_follower.follow_on_right(line_follower.StopNever())


if __name__ == '__main__':
    unittest.main()

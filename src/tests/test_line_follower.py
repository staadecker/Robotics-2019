import unittest
import main
from lib import line_follower
from tests import util
import lib.motors
import lib.constants


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestLineFollower(unittest.TestCase):
    def setUp(self) -> None:
        self.robot = main.Robot()
        self.line_follower = line_follower.LineFollower(self.robot.mover)

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
    def test_run_ten_seconds(self):
        self.robot = main.Robot()
        self.line_follower = line_follower.LineFollower(self.robot.mover)
        self.line_follower.follow_on_left(line_follower.StopAfterTime(15000))


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestLineFollowWithIntersections(unittest.TestCase):
    def test_run_ten_seconds(self):
        self.robot = main.Robot()
        self.line_follower = line_follower.LineFollower(self.robot.mover)
        self.line_follower.follow_on_left(
            line_follower.get_stop_after_x_intersections(5, self.robot.right_color_sensor))


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestWithFullSetup(unittest.TestCase):
    def test_full(self):
        m = main.Main()
        lf = line_follower.LineFollower(m.robot.mover)
        lf.follow_on_right(line_follower.get_stop_after_x_intersections(5, m.robot.left_color_sensor))


class TestReverseColorSensor(unittest.TestCase):
    def test_reverse(self):
        mover = lib.motors.Mover(reverse_motors=True)
        lf = line_follower.LineFollower(mover, port=lib.constants.SIDE_COLOR_SENSOR, kp=0.2, kd=0.2, ki=0)
        lf.follow_on_right(line_follower.StopAfterTime(15000))


if __name__ == '__main__':
    unittest.main()

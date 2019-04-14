import lib.line_follower
import lib.robot
from lib.sensors import ColorSensor


class Actions:
    def __init__(self, line_follower: lib.line_follower.LineFollower, robot: lib.robot.Robot):
        self._line_follower = line_follower
        self._robot = robot

    def go_to_first_fibre_from_start(self, color_blocks_callback=None):
        # Go to corner
        self._robot.mover.rotate(degrees=15, arc_radius=600, speed=25, clockwise=False)
        self._robot.mover.rotate(degrees=10, speed=25)
        self._line_follower.follow_on_left(lib.line_follower.StopAtCrossLine(self._robot.left_color_sensor),
                                           callback=color_blocks_callback)

        # Turn
        self._turn_left()

        # Go to end
        self._line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(5, self._robot.left_color_sensor))

    def pickup_fibre_on_left(self):
        self._robot.arm.lower_to_fibre_optic()
        self._robot.mover.rotate(degrees=45, clockwise=False)
        self._robot.mover.travel(80)
        self._robot.mover.rotate(degrees=45)
        self._robot.mover.travel(120)
        self._robot.arm.raise_arm(slow=True)
        self._robot.mover.rotate(degrees=175)
        self._robot.mover.travel(180)
        self._robot.mover.rotate(degrees=25, arc_radius=60)

    def go_to_drop_off_fibre(self):
        self._line_follower.follow_on_left(lib.line_follower.StopAtCrossLine(self._robot.right_color_sensor))
        self._turn_right()
        self._line_follower.follow_on_left(
            lib.line_follower.get_stop_after_x_intersections(1, self._robot.left_color_sensor))
        self._turn_left()
        self._line_follower.follow_on_right(
            lib.line_follower.StopAtColor(self._robot.left_color_sensor, (ColorSensor.RED,)))

    def drop_off_fibre(self):
        # self._robot.mover.rotate(arc_radius=self._robot.mover.CHASSIS_RADIUS, backwards=True, speed=5)
        #
        # while self._robot

        self._robot.arm.lower_to_fibre_optic(slow=True)
        self._robot.mover.travel(150, backwards=True)
        self._robot.arm.raise_arm()
        self._robot.mover.rotate(degrees=180)

    def _turn_left(self):
        self._robot.mover.rotate(degrees=85, arc_radius=30, clockwise=False)

    def _turn_right(self):
        self._robot.mover.rotate(degrees=85)

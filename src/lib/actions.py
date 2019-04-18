import lib.line_follower
import lib.robot
import time
from lib.sensors import ColorSensor


class Actions:
    def __init__(self, line_follower: lib.line_follower.LineFollower, robot: lib.robot.Robot):
        self._line_follower = line_follower
        self._robot = robot

    def go_to_first_fibre_from_start_part_1(self, color_blocks_callback=None):
        # Go to corner
        self._robot.mover.rotate(degrees=15, arc_radius=600, speed=25, clockwise=False)
        self._robot.mover.rotate(degrees=10)
        self._line_follower.follow_on_left(lib.line_follower.StopAtCrossLine(self._robot.left_color_sensor),
                                           callback=color_blocks_callback)

        # Turn
        self._robot.mover.rotate(degrees=85, arc_radius=20, clockwise=False)

        self._line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(2, self._robot.left_color_sensor))

    def get_bonus(self):
        self._robot.mover.rotate(degrees=90, clockwise=False, arc_radius=20)
        self._robot.arm.lower_to_bonus(block=False)
        self._line_follower.follow_on_right(
            lib.line_follower.StopAtColor(self._robot.right_color_sensor, (ColorSensor.RED,)), slow=True)
        self._robot.mover.travel(105)
        self._robot.swivel.point_backwards(speed=5)
        self._robot.swivel.point_forward(block=False)
        self._robot.arm.raise_arm(block=False)
        # self._robot.mover.travel(300, backwards=True)
        self._robot.mover.rotate(degrees=90, arc_radius=245, backwards=True)

    def go_to_first_fibre_from_start_part_2(self):
        # Go to end
        self._line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(3, self._robot.left_color_sensor))

    def pickup_fibre_on_left(self):
        self._robot.arm.lower_to_fibre_optic()
        self._robot.mover.rotate(degrees=45, clockwise=False)
        self._robot.mover.travel(110)
        self._robot.mover.rotate(degrees=45)
        self._robot.mover.travel(70)
        self._robot.arm.raise_arm(slow=True)
        self._robot.mover.rotate(degrees=160)
        self._robot.mover.travel(150)
        self._robot.mover.rotate(degrees=25, arc_radius=60)

    def go_to_drop_off_fibre(self):
        self._line_follower.follow_on_left(lib.line_follower.StopAtCrossLine(self._robot.right_color_sensor), slow=True)
        self._robot.mover.rotate(degrees=90, arc_radius=40)
        self._line_follower.follow_on_left(
            lib.line_follower.get_stop_after_x_intersections(1, self._robot.left_color_sensor), slow=True)
        self._robot.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self._line_follower.follow_on_right(
            lib.line_follower.StopAtColor(self._robot.left_color_sensor, (ColorSensor.RED,)), slow=True)

    def drop_off_fibre_first(self):
        self._robot.mover.travel(35)
        self._robot.mover.rotate(degrees=4, clockwise=False)
        time.sleep(0.5)
        self._robot.arm.lower_to_fibre_optic(slow=True)
        self._robot.arm.wiggle_fibre_optic()
        self._robot.mover.travel(170, backwards=True)
        self._robot.arm.raise_arm()
        self._robot.mover.rotate(degrees=180)

    def go_to_second_fibre(self):
        self._robot.mover.rotate(degrees=85, arc_radius=130, clockwise=False)
        self._line_follower.follow_on_left(
            lib.line_follower.StopAfterMultiple([
                lib.line_follower.StopAfterTime(300),
                lib.line_follower.StopAtCrossLine(self._robot.left_color_sensor)
            ])
        )
        self._robot.mover.rotate(degrees=90, arc_radius=30)
        self._line_follower.follow_on_left(
            lib.line_follower.StopAtCrossLine(self._robot.right_color_sensor)
        )

    def pickup_second_fibre(self):
        self._robot.arm.lower_to_fibre_optic()
        self._robot.mover.rotate(degrees=45)
        self._robot.mover.travel(110)
        self._robot.mover.rotate(degrees=45, clockwise=False)
        self._robot.mover.travel(80)
        self._robot.arm.raise_arm(slow=True)
        self._robot.mover.rotate(degrees=160, clockwise=False)
        self._robot.mover.travel(170)
        time.sleep(1)
        self._robot.mover.rotate(degrees=20, arc_radius=60, clockwise=False)

    def go_to_drop_second_fibre(self):
        self._line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(4, self._robot.left_color_sensor), slow=False
        )
        self._robot.mover.rotate(degrees=90, arc_radius=30, clockwise=False)
        self._line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(1, self._robot.left_color_sensor), slow=True)
        self._robot.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self._line_follower.follow_on_right(
            lib.line_follower.StopAtColor(self._robot.right_color_sensor, (ColorSensor.GREEN,)), slow=True)

    def drop_off_fibre_second(self):
        self._robot.mover.travel(35)
        self._robot.mover.rotate(degrees=4, clockwise=False)
        time.sleep(0.5)
        self._robot.arm.lower_to_fibre_optic(slow=True)
        self._robot.arm.wiggle_fibre_optic()
        self._robot.mover.travel(170, backwards=True)
        self._robot.arm.raise_arm()
        self._robot.mover.rotate(degrees=180)

    def return_to_start(self):
        self._robot.mover.rotate(degrees=90, arc_radius=110)
        self._line_follower.follow_on_left(
            lib.line_follower.get_stop_after_x_intersections(1, self._robot.right_color_sensor, False), slow=True)
        self._robot.mover.rotate(degrees=100, arc_radius=50)
        self._robot.mover.travel(400, backwards=True)

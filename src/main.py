import lib.line_follower
from ev3dev2.button import Button
from lib.robot import Robot

DEBUGGING = True


class Main:
    def __init__(self):
        self.robot = None
        self.line_follower = None

    def setup(self):
        self.robot = Robot()
        self.line_follower = lib.line_follower.LineFollower(
            self.robot.mover,
            self.robot.left_color_sensor,
            self.robot.right_color_sensor
        )

    def run(self):
        self.robot.mover.travel(100)
        self.line_follower.follow_on_right(lib.line_follower.StopAtCrossLine(self.robot.left_color_sensor),
                                           callback=self.read_info_blocks_callback, stop=False)
        self.robot.mover.rotate(degrees=90, clockwise=False, arc_radius=40)
        self.line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(5, self.robot.left_color_sensor))

    def read_info_blocks_callback(self):
        pass  # TODO


if __name__ == '__main__':
    main = Main()

    try:
        main.setup()
        if not DEBUGGING:
            Button.wait_for_released('enter')
        main.run()
    finally:
        robot = main.robot
        if robot is not None:
            robot.tear_down()

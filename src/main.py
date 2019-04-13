import lib.line_follower
from ev3dev2.button import Button
from lib.robot import Robot
import lib.navigator

DEBUGGING = True


class Main:
    def __init__(self):
        self.robot = Robot()
        self.line_follower = lib.line_follower.LineFollower(self.robot.mover)
        self.navigator = lib.navigator.Navigator(self.line_follower, self.robot)

    def run(self):
        self.robot.arm.raise_arm()
        self.robot.swivel.point_forward(block=False)

        self.navigator.go_to_first_fibre_from_start(color_blocks_callback=self.read_info_blocks_callback)

        self.navigator.pickup_fibre_on_left()

        self.navigator.go_to_drop_off_fibre()

    def read_info_blocks_callback(self):
        pass  # TODO


if __name__ == '__main__':
    main = None

    try:
        main = Main()
        if not DEBUGGING:
            Button.wait_for_released('enter')
        main.run()
    finally:
        if main is not None:
            main.robot.tear_down()

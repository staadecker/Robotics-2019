#!/usr/bin/env python3

import lib.line_follower
from ev3dev2.button import Button
from lib.robot import Robot
import lib.actions

DEBUGGING = False


class Main:
    def __init__(self):
        self.robot = Robot()
        self.line_follower = lib.line_follower.LineFollower(self.robot.mover)
        self.actions = lib.actions.Actions(self.line_follower, self.robot)

    def run(self):
        self.prepare()

        self.actions.go_to_first_fibre_from_start(color_blocks_callback=self.read_info_blocks_callback)

        self.actions.pickup_fibre_on_left()

        self.actions.go_to_drop_off_fibre()
        self.actions.drop_off_fibre_first()
        self.actions.go_to_second_fibre()
        self.actions.pickup_second_fibre()
        self.actions.go_to_drop_second_fibre()
        self.actions.drop_off_fibre_second()
        self.actions.return_to_start()

    def prepare(self):
        self.robot.arm.raise_arm(calibrate=True)
        self.robot.swivel.point_forward(block=False)

    def read_info_blocks_callback(self):
        pass  # TODO


if __name__ == '__main__':
    main = None

    try:
        main = Main()
        if not DEBUGGING:
            main.robot.beep()
            while True:
                if Button().enter:
                    break
        main.run()
    finally:
        if main is not None:
            main.robot.tear_down()

#!/usr/bin/env python3

import lib.line_follower
from ev3dev2.button import Button
import lib.motors
import lib.sensors
import lib.ports
import ev3dev2.sound
import time
from lib.sensors import ColorSensor

REQUIRE_ENTER_TO_START = True


class Main:
    def __init__(self):
        self.mover = lib.motors.Mover()
        self.left_line_sensor = lib.sensors.ColorSensor(lib.ports.LEFT_COLOR_SENSOR)
        self.right_line_sensor = lib.sensors.ColorSensor(lib.ports.RIGHT_COLOR_SENSOR)
        self.swivel = lib.motors.Swivel()
        self.lift = lib.motors.Lift()

        self.line_follower = lib.line_follower.LineFollower(self.mover)

    def end(self):
        self.mover.stop()
        self.swivel.back()
        self.lift.up()

    @classmethod
    def beep(cls):
        ev3dev2.sound.Sound().beep(play_type=ev3dev2.sound.Sound.PLAY_NO_WAIT_FOR_COMPLETE)

    def run(self):
        ###########
        # PREPARE #
        ###########
        self.lift.calibrate()

        #####################
        # GO TO FIRST FIBRE #
        #####################
        # Go to corner
        self.mover.rotate(degrees=15, arc_radius=600, speed=25, clockwise=False)
        self.mover.rotate(degrees=10)
        self.line_follower.follow(lib.line_follower.StopAtCrossLine(self.left_line_sensor))

        # Turn
        self.mover.rotate(degrees=85, arc_radius=20, clockwise=False)

        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(4, self.left_line_sensor), on_left=False)

        ################
        # PICKUP FIBRE #
        ################
        self.lift.to_fibre()
        self.mover.rotate(degrees=45, clockwise=False)
        self.mover.travel(110)
        self.mover.rotate(degrees=45)
        self.mover.travel(70)
        self.lift.up()
        self.mover.rotate(degrees=160)
        self.mover.travel(150)
        self.mover.rotate(degrees=25, arc_radius=60)

        ########################
        # GO TO DROP OFF FIBRE #
        ########################
        self.line_follower.follow(lib.line_follower.StopAtCrossLine(self.right_line_sensor))
        self.mover.rotate(degrees=90, arc_radius=40)
        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(1, self.left_line_sensor))
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.StopAtColor(self.left_line_sensor, (ColorSensor.RED,)), on_left=False)

        ##################
        # DROP OFF FIBRE #
        ##################
        self.mover.travel(35)
        self.mover.rotate(degrees=4, clockwise=False)
        time.sleep(0.5)
        self.lift.to_fibre()
        self.mover.travel(170, backwards=True)
        self.lift.up()
        self.mover.rotate(degrees=180)

        ######################
        # GO TO SECOND FIBRE #
        ######################
        self.mover.rotate(degrees=85, arc_radius=130, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.StopAfterMultiple([
                lib.line_follower.StopAfterTime(300),
                lib.line_follower.StopAtCrossLine(self.left_line_sensor)
            ])
        )
        self.mover.rotate(degrees=90, arc_radius=30)
        self.line_follower.follow(
            lib.line_follower.StopAtCrossLine(self.right_line_sensor)
        )

        ##################
        # PICKUP FIBRE 2 #
        ##################
        self.lift.to_fibre()
        self.mover.rotate(degrees=45)
        self.mover.travel(110)
        self.mover.rotate(degrees=45, clockwise=False)
        self.mover.travel(80)
        self.lift.up()
        self.mover.rotate(degrees=160, clockwise=False)
        self.mover.travel(170)
        time.sleep(1)
        self.mover.rotate(degrees=20, arc_radius=60, clockwise=False)

        ######################
        # GO TO DROP FIBRE 2 #
        ######################
        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(4, self.left_line_sensor), on_left=False
        )
        self.mover.rotate(degrees=90, arc_radius=30, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(1, self.left_line_sensor), on_left=False)
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.StopAtColor(self.right_line_sensor, (ColorSensor.GREEN,)), on_left=False)

        ################
        # DROP FIBRE 2 #
        ################
        self.mover.travel(35)
        self.mover.rotate(degrees=4, clockwise=False)
        time.sleep(0.5)
        self.lift.to_fibre()
        self.mover.travel(170, backwards=True)
        self.lift.up()
        self.mover.rotate(degrees=180)

        ###################
        # RETURN TO START #
        ###################
        self.mover.rotate(degrees=90, arc_radius=110)
        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(1, self.right_line_sensor, False))
        self.mover.rotate(degrees=100, arc_radius=50)
        self.mover.travel(400, backwards=True)


if __name__ == '__main__':
    main = Main()
    print("READY")

    # WAIT FOR ENTER
    if REQUIRE_ENTER_TO_START:
        main.beep()
        while True:
            if Button().enter:
                break

    try:
        main.run()
    finally:
        main.end()

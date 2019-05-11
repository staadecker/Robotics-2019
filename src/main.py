#!/usr/bin/env python3


import ev3dev2

import os
import time

import lib.sensors as sensors
import lib.line_follower
import lib.motors
import lib.sensors
import lib.ports

if ev3dev2.is_micropython():
    import lib.micropython_button as micro_button
else:
    import ev3dev2.button as button

REQUIRE_ENTER_TO_START = False


def wait_for_enter():
    if ev3dev2.is_micropython():
        micro_button.Buttons().wait((micro_button.CENTER,), micro_button.State.BUMPED)
    else:
        while True:
            if button.Button().enter:
                break


def beep():
    os.system("/usr/bin/beep")


class Main:
    def __init__(self):
        self.mover = lib.motors.Mover(reverse_motors=True)
        self.left_sensor = lib.sensors.EV3ColorSensor(lib.ports.LEFT_SENSOR)
        self.right_sensor = lib.sensors.HiTechnicSensor(lib.ports.RIGHT_SENSOR)
        self.swivel = lib.motors.Swivel()
        self.lift = lib.motors.Lift()

        self.line_follower = lib.line_follower.LineFollower(self.mover)

    def end(self):
        self.mover.stop()
        self.swivel.reset()
        self.lift.up()

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
        self.line_follower.follow(lib.line_follower.StopAtCrossLine(self.left_sensor))

        # Turn
        self.mover.rotate(degrees=85, arc_radius=20, clockwise=False)

        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(4, self.left_sensor), on_left=False)

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
        self.line_follower.follow(lib.line_follower.StopAtCrossLine(self.right_sensor))
        self.mover.rotate(degrees=90, arc_radius=40)
        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(1, self.left_sensor))
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.StopAtColor(self.left_sensor, (sensors.RED,)), on_left=False)

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
                lib.line_follower.StopAfterTime(0.3),
                lib.line_follower.StopAtCrossLine(self.left_sensor)
            ])
        )
        self.mover.rotate(degrees=90, arc_radius=30)
        self.line_follower.follow(
            lib.line_follower.StopAtCrossLine(self.right_sensor)
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
            lib.line_follower.get_stop_after_x_intersections(4, self.left_sensor), on_left=False
        )
        self.mover.rotate(degrees=90, arc_radius=30, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.get_stop_after_x_intersections(1, self.left_sensor), on_left=False)
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow(
            lib.line_follower.StopAtColor(self.right_sensor, (sensors.GREEN,)), on_left=False)

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
            lib.line_follower.get_stop_after_x_intersections(1, self.right_sensor, False))
        self.mover.rotate(degrees=100, arc_radius=50)
        self.mover.travel(400, backwards=True)


if __name__ == '__main__':
    main = Main()
    print("READY")

    # WAIT FOR ENTER
    if REQUIRE_ENTER_TO_START:
        beep()
        wait_for_enter()

    try:
        main.run()
    finally:
        main.end()

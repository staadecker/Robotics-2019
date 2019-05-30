#!/usr/bin/env micropython


import ev3dev2

import os
import time

import lib.up_sensors as sensors
import lib.up_line_follower as line_follower
import lib.up_motors as motors
import lib.up_sensors as sensors
import lib.up_ports as ports

if ev3dev2.is_micropython():
    import lib.up_micropython_button as micro_button
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
        self.mover = motors.Mover(reverse_motors=True)
        self.left_sensor = sensors.EV3ColorSensor(ports.LEFT_SENSOR)
        self.right_sensor = sensors.HiTechnicSensor(ports.RIGHT_SENSOR)
        self.swivel = motors.Swivel()
        self.lift = motors.Lift()

        self.line_follower = line_follower.LineFollower(self.mover)

    def end(self):
        self.mover.stop()
        self.swivel.reset()
        self.lift.up()

    def test(self):
        self.mover.rotate(6, clockwise=False)
        self.mover.travel(100)
        self.line_follower.follow(line_follower.StopAtIntersectionX(1, self.left_sensor))
        self.mover.rotate(90, clockwise=False, arc_radius=50)
        self.line_follower.follow(line_follower.StopAtIntersectionX(6, self.left_sensor), on_left=False)

        time.sleep(2)
        self.mover.rotate(60, clockwise=False, speed=15)
        time.sleep(2)
        self.mover.travel(70, speed=15)
        time.sleep(2)
        self.mover.rotate(50, speed=15)
        time.sleep(2)
        self.lift.to_fibre()
        self.line_follower.follow(line_follower.StopAtColor(self.left_sensor, (sensors.YELLOW,)), on_left=False,
                                  speed=15, kp=0.8, kd=0)

        # lift.calibrate()

        # lift.to_fibre()

        # lift.up()
        # print("Test")

        # mover.steer(-10)
        # lf.follow(line_follower.StopAtIntersectionX(5, left_color_sensor, include_initial_delay=False), kp=0.3, ki=0, kd=1, on_left=True, backwards=True)
        time.sleep(2)
        
    def run(self):
        ###########
        # PREPARE #
        ###########
        self.lift.calibrate()

        #####################
        # GO TO FIRST FIBRE #
        #####################
        # Go to corner
        self.mover.rotate(6, clockwise=False)
        self.mover.travel(100)
        self.line_follower.follow(line_follower.StopAtIntersectionX(1, self.left_sensor))
        self.mover.rotate(90, clockwise=False, arc_radius=50)
        self.line_follower.follow(line_follower.StopAtIntersectionX(6, self.left_sensor), on_left=False)

        # Turn
        self.mover.rotate(degrees=85, arc_radius=20, clockwise=False)

        self.line_follower.follow(
            line_follower.StopAtIntersectionX(4, self.left_sensor), on_left=False)

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
        self.line_follower.follow(line_follower.StopAtCrossLine(self.right_sensor))
        self.mover.rotate(degrees=90, arc_radius=40)
        self.line_follower.follow(
            line_follower.StopAtIntersectionX(1, self.left_sensor))
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow(
            line_follower.StopAtColor(self.left_sensor, (sensors.RED,)), on_left=False)

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
            line_follower.StopAfterMultiple([
                line_follower.StopAfterTime(0.3),
                line_follower.StopAtCrossLine(self.left_sensor)
            ])
        )
        self.mover.rotate(degrees=90, arc_radius=30)
        self.line_follower.follow(
            line_follower.StopAtCrossLine(self.right_sensor)
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
            line_follower.StopAtIntersectionX(4, self.left_sensor), on_left=False
        )
        self.mover.rotate(degrees=90, arc_radius=30, clockwise=False)
        self.line_follower.follow(
            line_follower.StopAtIntersectionX(1, self.left_sensor), on_left=False)
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow(
            line_follower.StopAtColor(self.right_sensor, (sensors.GREEN,)), on_left=False)

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
            line_follower.StopAtIntersectionX(1, self.right_sensor, False))
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

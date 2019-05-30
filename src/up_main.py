#!/usr/bin/env micropython


import ev3dev2

import os
import time

if ev3dev2.is_micropython():
    import lib.up_micropython_button as micro_button
else:
    import ev3dev2.button as button


from lib.robot import *

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


def end():
    MOVER.stop()
    SWIVEL.reset()
    LIFT.up()


def test():
    prepare()
    go_to_first_fibre()


def run():
    prepare()
    go_to_first_fibre()
    pickup_fibre()
    go_to_drop_off_fibre()
    drop_off_fibre()
    go_to_second_fibre()
    pickup_second_fibre()
    go_to_drop_second_fibre()
    drop_second_fibre()
    return_to_start()


def prepare():
    ###########
    # PREPARE #
    ###########
    LIFT.calibrate()


def go_to_first_fibre():
    #####################
    # GO TO FIRST FIBRE #
    #####################
    # Go to corner
    MOVER.rotate(6, clockwise=False)
    MOVER.travel(100)
    line_follower.follow_until_line(LEFT_SENSOR)
    rotate_until_line(clockwise=False, arc_radius=50)
    line_follower.follow_until_intersenction_x(6, LEFT_SENSOR, on_left=False)
    # Turn
    MOVER.rotate(degrees=85, arc_radius=20, clockwise=False)
    line_follower.follow_until_color()
    LINE_FOLLOWER.follow(
        LINE_FOLLOWER.StopAtIntersectionX(4, LEFT_SENSOR), on_left=False)


def pickup_fibre():
    ################
    # PICKUP FIBRE #
    ################
    LIFT.to_fibre()
    MOVER.rotate(degrees=45, clockwise=False)
    MOVER.travel(110)
    MOVER.rotate(degrees=45)
    MOVER.travel(70)
    LIFT.up()
    MOVER.rotate(degrees=160)
    MOVER.travel(150)
    MOVER.rotate(degrees=25, arc_radius=60)


def go_to_drop_off_fibre():
    ########################
    # GO TO DROP OFF FIBRE #
    ########################
    LINE_FOLLOWER.follow(LINE_FOLLOWER.StopAtCrossLine(RIGHT_SENSOR))
    MOVER.rotate(degrees=90, arc_radius=40)
    LINE_FOLLOWER.follow(
        LINE_FOLLOWER.StopAtIntersectionX(1, LEFT_SENSOR))
    MOVER.rotate(degrees=90, arc_radius=40, clockwise=False)
    LINE_FOLLOWER.follow(
        LINE_FOLLOWER.StopAtColor(LEFT_SENSOR, (sensors.RED,)), on_left=False)


def drop_off_fibre():
    ##################
    # DROP OFF FIBRE #
    ##################
    MOVER.travel(35)
    MOVER.rotate(degrees=4, clockwise=False)
    time.sleep(0.5)
    LIFT.to_fibre()
    MOVER.travel(170, backwards=True)
    LIFT.up()
    MOVER.rotate(degrees=180)


def go_to_second_fibre():
    ######################
    # GO TO SECOND FIBRE #
    ######################
    MOVER.rotate(degrees=85, arc_radius=130, clockwise=False)
    LINE_FOLLOWER.follow(
        line_follower.StopAfterMultiple([
            line_follower.follow_for_time(0.3),
            line_follower.StopAtCrossLine(LEFT_SENSOR)
        ])
    )
    MOVER.rotate(degrees=90, arc_radius=30)
    LINE_FOLLOWER.follow(
        line_follower.StopAtCrossLine(RIGHT_SENSOR)
    )


def pickup_second_fibre():
    ##################
    # PICKUP FIBRE 2 #
    ##################
    LIFT.to_fibre()
    MOVER.rotate(degrees=45)
    MOVER.travel(110)
    MOVER.rotate(degrees=45, clockwise=False)
    MOVER.travel(80)
    LIFT.up()
    MOVER.rotate(degrees=160, clockwise=False)
    MOVER.travel(170)
    time.sleep(1)
    MOVER.rotate(degrees=20, arc_radius=60, clockwise=False)


def go_to_drop_second_fibre():
    ######################
    # GO TO DROP FIBRE 2 #
    ######################
    LINE_FOLLOWER.follow(
        line_follower.StopAtIntersectionX(4, LEFT_SENSOR), on_left=False
    )
    MOVER.rotate(degrees=90, arc_radius=30, clockwise=False)
    LINE_FOLLOWER.follow(
        line_follower.StopAtIntersectionX(1, LEFT_SENSOR), on_left=False)
    MOVER.rotate(degrees=90, arc_radius=40, clockwise=False)
    LINE_FOLLOWER.follow(
        line_follower.StopAtColor(RIGHT_SENSOR, (sensors.GREEN,)), on_left=False)


def drop_second_fibre():
    ################
    # DROP FIBRE 2 #
    ################
    MOVER.travel(35)
    MOVER.rotate(degrees=4, clockwise=False)
    time.sleep(0.5)
    LIFT.to_fibre()
    MOVER.travel(170, backwards=True)
    LIFT.up()
    MOVER.rotate(degrees=180)


def return_to_start():
    ###################
    # RETURN TO START #
    ###################
    MOVER.rotate(degrees=90, arc_radius=110)
    LINE_FOLLOWER.follow(
        LINE_FOLLOWER.StopAtIntersectionX(1, RIGHT_SENSOR, False))
    MOVER.rotate(degrees=100, arc_radius=50)
    MOVER.travel(400, backwards=True)


def rotate_until_line(clockwise=True, arc_radius=0, stop=True, cross_line=False, front=True):
    sensor = FRONT_SENSOR if front else BACK_SENSOR
    MOVER.rotate(clockwise=clockwise, arc_radius=arc_radius, block=False, speed=20)
    while sensor.get_reflected() > 30:
        pass

    if cross_line:
        while sensor.get_reflected() > 20:
            pass

        while sensor.get_reflected() < 30:
            pass

    if stop:
        MOVER.stop()


if __name__ == '__main__':
    print("READY")

    # WAIT FOR ENTER
    if REQUIRE_ENTER_TO_START:
        beep()
        wait_for_enter()

    try:
        run()
    finally:
        end()

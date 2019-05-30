#!/usr/bin/env micropython


import ev3dev2
import lib.up_robot as r
import lib.up_line_follower as lf
import lib.up_old_line_follower as old_lf
import os
import time

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


def end():
    r.MOVER.stop()
    r.SWIVEL.reset()
    r.LIFT.up()


def test():
    old_lf.LineFollower(r.MOVER).follow(old_lf.StopAfterTime(3))
    # lf.follow_for_time(3, on_left=True)
    # lf.follow_until_intersection_x(5, r.LEFT_SENSOR, include_initial_delay=False, on_left=False)
    # rotate_until_line(clockwise=False, arc_radius=50)


def run():
    prepare()
    go_to_first_fibre()


def prepare():
    ###########
    # PREPARE #
    ###########
    r.LIFT.calibrate()


def go_to_first_fibre():
    #####################
    # GO TO FIRST FIBRE #
    #####################
    # Go to corner
    r.MOVER.rotate(8, clockwise=False)
    r.MOVER.travel(100)
    lf.follow_until_line(r.LEFT_SENSOR)
    rotate_until_line(clockwise=False, arc_radius=50)
    # lf.follow_until_intersection_x(6, r.LEFT_SENSOR, on_left=False)
    # Turn


def rotate_until_line(clockwise=True, arc_radius=0, stop=True, cross_line=False, front=True):
    sensor = r.FRONT_SENSOR if front else r.BACK_SENSOR
    r.MOVER.rotate(clockwise=clockwise, arc_radius=arc_radius, block=False, speed=20)

    while sensor.get_reflected() < 60:
        pass

    while sensor.get_reflected() > 30:
        pass

    if cross_line:
        while sensor.get_reflected() > 20:
            pass

        while sensor.get_reflected() < 40:
            pass

    if stop:
        r.MOVER.stop()


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

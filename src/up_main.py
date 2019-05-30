#!/usr/bin/env micropython


import ev3dev2
import lib.up_ports as ports
import lib.up_motors as motors
import lib.up_sensors as sensors
import lib.up_line_follower as line_follower
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


class Main:
    def __init__(self):
        self.mover = motors.Mover(reverse_motors=True)
        self.left_sensor = sensors.EV3ColorSensor(ports.LEFT_SENSOR)
        self.right_sensor = sensors.HiTechnicSensor(ports.RIGHT_SENSOR)
        self.front_sensor = sensors.EV3ColorSensor(ports.FRONT_SENSOR)
        self.back_sensor = sensors.EV3ColorSensor(ports.BACK_SENSOR)
        self.swivel = motors.Swivel()
        self.lift = motors.Lift()

        self.line_follower = line_follower.LineFollower(self.mover, self.front_sensor, self.back_sensor)

    def end(self):
        self.mover.stop()
        self.swivel.reset()
        self.lift.up()

    def test(self):
        self.go_to_first_fibre()

    def go_to_first_fibre(self):
        self.mover.rotate(6, clockwise=False)
        self.mover.travel(100)
        self.line_follower.follow_until_line(self.left_sensor)
        self.mover.rotate(90, clockwise=False, arc_radius=50)
        self.line_follower.follow_until_intersection_x(6, self.left_sensor, on_left=False)
        self.mover.rotate(60, clockwise=False, speed=15)
        self.mover.travel(70, speed=15)
        self.mover.rotate(50, speed=15)
        self.lift.to_fibre()
        self.line_follower.follow_until_color(self.left_sensor, (sensors.YELLOW,), on_left=False,
                                              speed=15, kp=1, kd=0)

    def run(self):
        self.prepare()
        self.go_to_first_fibre()

    def prepare(self):
        ###########
        # PREPARE #
        ###########
        self.lift.calibrate()

    def rotate_until_line(self, clockwise=True, arc_radius=0, stop=True, cross_line=False, front=True):
        sensor = self.front_sensor if front else self.back_sensor
        self.mover.rotate(clockwise=clockwise, arc_radius=arc_radius, block=False, speed=20)

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
            self.mover.stop()


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

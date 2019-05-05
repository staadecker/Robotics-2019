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
        self.prepare()

        self.go_to_first_fibre_from_start_part_1(color_blocks_callback=self.read_info_blocks_callback)
        self.go_to_first_fibre_from_start_part_2()

        self.pickup_fibre_on_left()

        self.go_to_drop_off_fibre()
        self.drop_off_fibre_first()
        self.go_to_second_fibre()
        self.pickup_second_fibre()
        self.go_to_drop_second_fibre()
        self.drop_off_fibre_second()
        self.return_to_start()

    def prepare(self):
        self.lift.calibrate()

    def read_info_blocks_callback(self):
        pass  # TODO
    
    def go_to_first_fibre_from_start_part_1(self, color_blocks_callback=None):
        # Go to corner
        self.mover.rotate(degrees=15, arc_radius=600, speed=25, clockwise=False)
        self.mover.rotate(degrees=10)
        self.line_follower.follow_on_left(lib.line_follower.StopAtCrossLine(self.left_line_sensor),
                                          callback=color_blocks_callback)

        # Turn
        self.mover.rotate(degrees=85, arc_radius=20, clockwise=False)

        self.line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(2, self.left_line_sensor))

    def go_to_first_fibre_from_start_part_2(self):
        # Go to end
        self.line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(3, self.left_line_sensor))

    def pickup_fibre_on_left(self):
        self.lift.to_fibre()
        self.mover.rotate(degrees=45, clockwise=False)
        self.mover.travel(110)
        self.mover.rotate(degrees=45)
        self.mover.travel(70)
        self.lift.up()
        self.mover.rotate(degrees=160)
        self.mover.travel(150)
        self.mover.rotate(degrees=25, arc_radius=60)

    def go_to_drop_off_fibre(self):
        self.line_follower.follow_on_left(lib.line_follower.StopAtCrossLine(self.right_line_sensor), slow=True)
        self.mover.rotate(degrees=90, arc_radius=40)
        self.line_follower.follow_on_left(
            lib.line_follower.get_stop_after_x_intersections(1, self.left_line_sensor), slow=True)
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow_on_right(
            lib.line_follower.StopAtColor(self.left_line_sensor, (ColorSensor.RED,)), slow=True)

    def drop_off_fibre_first(self):
        self.mover.travel(35)
        self.mover.rotate(degrees=4, clockwise=False)
        time.sleep(0.5)
        self.lift.to_fibre()
        self.mover.travel(170, backwards=True)
        self.lift.up()
        self.mover.rotate(degrees=180)

    def go_to_second_fibre(self):
        self.mover.rotate(degrees=85, arc_radius=130, clockwise=False)
        self.line_follower.follow_on_left(
            lib.line_follower.StopAfterMultiple([
                lib.line_follower.StopAfterTime(300),
                lib.line_follower.StopAtCrossLine(self.left_line_sensor)
            ])
        )
        self.mover.rotate(degrees=90, arc_radius=30)
        self.line_follower.follow_on_left(
            lib.line_follower.StopAtCrossLine(self.right_line_sensor)
        )

    def pickup_second_fibre(self):
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

    def go_to_drop_second_fibre(self):
        self.line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(4, self.left_line_sensor), slow=False
        )
        self.mover.rotate(degrees=90, arc_radius=30, clockwise=False)
        self.line_follower.follow_on_right(
            lib.line_follower.get_stop_after_x_intersections(1, self.left_line_sensor), slow=True)
        self.mover.rotate(degrees=90, arc_radius=40, clockwise=False)
        self.line_follower.follow_on_right(
            lib.line_follower.StopAtColor(self.right_line_sensor, (ColorSensor.GREEN,)), slow=True)

    def drop_off_fibre_second(self):
        self.mover.travel(35)
        self.mover.rotate(degrees=4, clockwise=False)
        time.sleep(0.5)
        self.lift.to_fibre()
        self.mover.travel(170, backwards=True)
        self.lift.up()
        self.mover.rotate(degrees=180)

    def return_to_start(self):
        self.mover.rotate(degrees=90, arc_radius=110)
        self.line_follower.follow_on_left(
            lib.line_follower.get_stop_after_x_intersections(1, self.right_line_sensor, False), slow=True)
        self.mover.rotate(degrees=100, arc_radius=50)
        self.mover.travel(400, backwards=True)


if __name__ == '__main__':
    main = None

    try:
        main = Main()
        if not REQUIRE_ENTER_TO_START:
            print("READY")
            main.beep()
            while True:
                if Button().enter:
                    break
        main.run()
    finally:
        if main is not None:
            main.end()

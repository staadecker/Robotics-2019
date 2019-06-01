#!/usr/bin/env micropython

import lib.up_ports as ports
import lib.up_motors as motors
import lib.up_sensors as sensors
import lib.up_line_follower as line_follower
import os
import time

import ev3dev2.button as button

REQUIRE_ENTER_TO_START = True


def wait_for_enter():
    while True:
        time.sleep(0.1)
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

        self.color_codes = []
        self.position_of_top_white = None
        self.position_of_bottom_white = None

        self.setup()

    def setup(self):
        self.lift.calibrate()

    def teardown(self):
        self.mover.stop()
        self.swivel.reset()
        self.lift.up()

    def test(self):
        self.color_codes = [0, 0, 0, sensors.RED, sensors.BLUE]

        self.do_second_fibre()

        # self.position_of_top_white = 2

        # self.do_other_nodes()

        # self.do_other_nodes()
        # self.drop_off_node(sensors.RED)
        # self.go_from_red_drop_to_line_up_third()
        # self.line_follower.follow_until_intersection_x(6, self.left_sensor, on_left=False)

        # self.middle_to_red_drop()

        # self.mover.rotate(clockwise=False, arc_radius=120, block=False)
        # self.wait_for_colors(self.left_sensor, (sensors.BLACK,))
        # self.mover.rotate(clockwise=False, arc_radius=70, block=False)
        # self.wait_for_black_cutoff(self.front_sensor)
        # self.mover.stop()
        # self.mover.rotate(degrees=45, clockwise=False, arc_radius=70)
        # self.mover.rotate(degrees=30, backwards=True, clockwise=False, arc_radius=20)

    def run(self):
        self.go_to_first_fibre()
        self.lift.up()
        self.go_to_fibre_drop_off()  # Also does first node

        self.lift.to_fibre()
        self.lift.up()

        self.do_other_nodes()

        self.do_second_fibre()
        self.return_to_start()

    def go_to_first_fibre(self):
        # Find line
        self.mover.rotate(12, clockwise=False)
        self.mover.travel(150)

        # Scan blocks
        while not self.left_sensor.get_color() == sensors.BLACK:
            self.line_follower.follow(speed=35)

            color = self.right_sensor.get_color()
            if color in (sensors.RED, sensors.BLUE, sensors.YELLOW, sensors.GREEN) and color not in self.color_codes:
                self.color_codes.append(color)

        self.line_follower.reset()
        self.mover.stop()

        if len(self.color_codes) != 4:
            beep()
            beep()

        print(self.color_codes)

        # Turn and go to end
        self.mover.rotate(clockwise=False, arc_radius=60, block=False, speed=20)
        self.wait_for_white_cutoff(self.front_sensor, cutoff=50)
        self.wait_for_black_cutoff(self.front_sensor, cutoff=30)
        self.mover.stop()

        self.line_follower.follow_until_intersection_x(6, self.left_sensor, on_left=False, use_reflection=True,
                                                       speed=60)

        # Line up
        self.mover.rotate(arc_radius=71, clockwise=False, block=False, speed=15)
        self.wait_for_colors(self.right_sensor, (sensors.BLACK,))
        self.mover.rotate(block=False, speed=30)
        self.wait_for_white_cutoff(self.front_sensor)
        self.wait_for_black_cutoff(self.front_sensor, 20)
        self.wait_for_white_cutoff(self.front_sensor)
        self.mover.stop()

        self.lift.to_fibre()
        self.line_follower.follow_until_color(self.left_sensor, (sensors.YELLOW,), on_left=False,
                                              speed=15, kp=1.5, kd=0)

    def go_to_fibre_drop_off(self):
        # Find line
        self.mover.rotate(clockwise=False, degrees=30, speed=20)
        self.mover.travel(backwards=True, distance=130, speed=20)
        self.mover.rotate(degrees=25, speed=20)

        # Follow line and turn
        self.line_follower.follow_for_time(1, backwards=True, speed=40, stop=True, kp=1, kd=0)
        time.sleep(0.5)
        self.line_follower.follow_until_line(self.left_sensor, backwards=True, speed=40)
        self.mover.rotate(degrees=90, clockwise=False, arc_radius=90)

        # Follow across
        time_first_cross = None
        first_node_is_white = True
        while True:
            self.line_follower.follow(on_left=False, speed=30)

            # If hasn't crossed yet
            if time_first_cross is None:
                if self.left_sensor.get_color() == sensors.BLACK:
                    time_first_cross = time.time()
            elif time.time() > time_first_cross + 0.15:
                if self.left_sensor.get_reflected() < 25:
                    self.mover.stop()
                    self.line_follower.reset()
                    break

            if time_first_cross is None or time.time() < time_first_cross + 0.15:
                if self.right_sensor.get_color() == sensors.BLACK:
                    first_node_is_white = False

        second_node_is_white = self.right_sensor.get_color() == sensors.WHITE

        if second_node_is_white and first_node_is_white:
            beep()
            beep()
            print("Error: Detected two whites nodes in top row")
            self.position_of_top_white = 1
        elif second_node_is_white:
            self.position_of_top_white = 1
        elif first_node_is_white:
            self.position_of_top_white = 0
        else:
            self.position_of_top_white = 2

        print("TOP WHITE AT:")
        print(self.position_of_top_white)

        # Do first node
        if self.position_of_top_white != 0:
            self.go_middle_to_line_up_with_first_node()
            self.pickup_node()
            self.turn_around_to_node_line()
            self.drop_off_node(sensors.RED)
            self.go_red_to_middle()
        else:
            # Turn
            self.mover.rotate(clockwise=False, arc_radius=50, block=False)
            time.sleep(0.3)
            self.wait_for_white_cutoff(self.front_sensor)
            self.wait_for_black_cutoff(self.front_sensor)
            self.mover.stop()

        # Follow to drop off
        self.line_follower.follow_until_color(self.left_sensor, (sensors.RED,), on_left=False, speed=20, kp=1.5, kd=0)
        self.mover.travel(speed=15, block=False)
        while not self.left_sensor.get_color() == sensors.WHITE:
            pass
        self.mover.stop()

        self.mover.travel(distance=10)

    def go_middle_to_line_up_with_first_node(self):
        # Reverse into position
        self.mover.rotate(clockwise=True, arc_radius=115, degrees=90, backwards=True)

        # Turn around
        self.mover.rotate(block=False, speed=40)
        time.sleep(0.2)
        self.wait_for_black_cutoff(self.back_sensor, cutoff=20)
        self.mover.stop()
        self.swivel.back()

    def pickup_node(self):
        # Pick up node
        self.swivel.back()
        self.line_follower.follow_until_line(self.right_sensor, backwards=True, speed=20, kp=2, kd=0.5)
        self.lift.to_node()
        self.line_follower.follow_for_time(0.5, speed=20, kp=1, on_left=False)
        self.lift.up()

    def turn_around_to_node_line(self):
        # Move back
        self.line_follower.follow_for_time(0.3, on_left=False, speed=50)

        # Turn around
        self.mover.rotate(clockwise=False, block=False, speed=20)
        self.wait_for_white_cutoff(self.back_sensor, cutoff=50)
        self.wait_for_black_cutoff(self.back_sensor, cutoff=30)
        self.wait_for_white_cutoff(self.back_sensor, cutoff=50)
        self.mover.stop()

    def go_red_to_middle(self):
        # Go back to fibre
        self.line_follower.follow_until_cutoff(self.left_sensor, 20, False, on_left=False)
        self.mover.rotate(clockwise=False, block=False, arc_radius=71)
        self.wait_for_white_cutoff(self.front_sensor)
        self.wait_for_black_cutoff(self.front_sensor)
        self.line_follower.follow_until_line(self.left_sensor, on_left=False)

    def do_other_nodes(self):
        if self.position_of_top_white == 0:
            self.go_fibre_one_to_middle_node()
            self.pickup_node()
            self.middle_to_red_drop()
            self.drop_off_node(sensors.RED)
            self.go_from_red_drop_to_line_up_third()
            self.pickup_node()
            self.turn_around_to_node_line()
            self.drop_off_node(sensors.BLUE)
        elif self.position_of_top_white == 1:
            self.go_to_third_node_from_first_fibre()
            self.pickup_node()
            self.turn_around_to_node_line()
            self.drop_off_node(sensors.BLUE)
        else:
            self.go_fibre_one_to_middle_node()
            self.pickup_node()
            self.go_pickup_middle_to_blue()
            self.drop_off_node(sensors.BLUE)

    def go_to_third_node_from_first_fibre(self):
        self.mover.rotate(clockwise=False, degrees=90, arc_radius=270, backwards=True)
        self.mover.rotate(degrees=90, arc_radius=60)

    def go_pickup_middle_to_blue(self):
        self.mover.rotate(block=False, clockwise=False)
        self.wait_for_white_cutoff(self.back_sensor)
        self.wait_for_black_cutoff(self.back_sensor)
        self.mover.stop()

        self.line_follower.follow_for_time(0.5, backwards=True, stop=False, speed=30, kp=1, kd=0, on_left=False)

        self.mover.rotate(degrees=85, arc_radius=80, backwards=True, clockwise=False)

    def middle_to_red_drop(self):
        self.mover.rotate(block=False)
        self.wait_for_white_cutoff(self.back_sensor)
        self.wait_for_black_cutoff(self.back_sensor)
        self.wait_for_white_cutoff(self.back_sensor)
        self.mover.stop()

        self.line_follower.follow_for_time(0.5, backwards=True, on_left=False, stop=False, speed=30, kp=1, kd=0)
        self.line_follower.follow_until_line(self.left_sensor, backwards=True, on_left=False)

        self.mover.rotate(degrees=80, arc_radius=110, backwards=True)

    def go_from_red_drop_to_line_up_third(self):
        self.line_follower.follow_until_line(self.left_sensor, on_left=False)
        self.mover.rotate(clockwise=False, degrees=90, arc_radius=20)
        # self.mover.rotate(clockwise=False, degrees=90, arc_radius=215)
        # self.line_follower.follow_for_time(0.3, speed=50)
        self.line_follower.follow_until_intersection_x(3, self.left_sensor, on_left=True, speed=50)

        # Reverse into position
        self.mover.rotate(clockwise=True, arc_radius=150, degrees=90, backwards=True)

        # Turn around
        self.mover.rotate(block=False)
        self.wait_for_white_cutoff(self.back_sensor)
        self.wait_for_black_cutoff(self.back_sensor, cutoff=30)
        self.mover.stop()

    def drop_off_node(self, color, use_color_mode=False):
        # TODO Fix drop off

        if use_color_mode:
            self.line_follower.follow_until_color(self.back_sensor, (color,), speed=20, backwards=True, kp=1.5, kd=0.5)
        else:
            self.line_follower.follow_until_constant(speed=20, kp=1.5, kd=0.5, backwards=True, cutoff=15, cycles=9,
                                                     stop=False, use_correction=False)
            print("LOCKED")
            self.line_follower.follow_until_change(speed=20, kp=1.5, kd=0.5, backwards=True, cutoff=20, cycles=2,
                                                   use_correction=False)

        self.mover.travel(distance=20, backwards=True, speed=20)

        # Drop off
        orientation = self.orient_block(color)
        self.place_node_in_slot(orientation)

    def go_fibre_one_to_middle_node(self):
        # Pick up node
        self.line_follower.follow_for_time(0.4, backwards=True, stop=True)

    def place_node_in_slot(self, orientation):
        if orientation == 270:
            time.sleep(2)
            self.lift._lift.on_for_degrees(self.lift._DEFAULT_SPEED, -240)
            self.mover.rotate(degrees=5, speed=20, clockwise=False)
            self.mover.rotate(degrees=10, clockwise=True, speed=20)
            self.mover.rotate(degrees=5, speed=20, clockwise=False)

        if orientation == 180 or orientation == 90:
            time.sleep(2)
            self.lift._lift.on_for_degrees(self.lift._DEFAULT_SPEED, -240)
            self.mover.travel(distance=15, backwards=False, speed=20)
            self.mover.travel(distance=15, speed=20, backwards=True)
            self.mover.rotate(degrees=5, speed=20, clockwise=False)
            self.mover.rotate(degrees=10, clockwise=True, speed=20)
            self.mover.rotate(degrees=5, speed=20, clockwise=False)
        if orientation == 0:
            self.lift._lift.on_for_degrees(self.lift._DEFAULT_SPEED, -240)
            self.mover.travel(distance=15, backwards=False, speed=20)
            self.mover.travel(distance=15, speed=20, backwards=True)
            self.mover.rotate(degrees=10, speed=20, clockwise=False)
            self.mover.rotate(degrees=15, clockwise=True, speed=20)
            self.mover.rotate(degrees=5, speed=20, clockwise=False)

        self.lift._lift.on_for_degrees(self.lift._DEFAULT_SPEED, -275)
        self.swivel._swivel.on_for_degrees(10, 180)
        self.lift._lift.on_for_degrees(self.lift._DEFAULT_SPEED, 520)

    def do_second_fibre(self):

        self.line_follower.follow_until_line(self.left_sensor, on_left=False)
        self.mover.rotate(degrees=90, arc_radius=30, clockwise=False)
        self.line_follower.follow_until_line(self.left_sensor, speed=40)
        self.mover.rotate(degrees=90, arc_radius=60, clockwise=True)
        self.line_follower.follow_until_line(self.right_sensor, speed=30)
        self.mover.rotate(degrees=45)
        self.mover.travel(block=False, speed=20)
        self.wait_for_black_cutoff(self.front_sensor)
        self.wait_for_white_cutoff(self.front_sensor)
        self.mover.stop()
        self.mover.travel(distance=20)
        self.lift.to_fibre()
        self.line_follower.follow_until_color(self.left_sensor, (sensors.YELLOW,), on_left=False,
                                              speed=15, kp=1.5, kd=0)
        self.lift.up()

        self.mover.rotate(clockwise=True, degrees=30, speed=20)
        self.mover.travel(backwards=True, distance=130, speed=20)
        self.mover.rotate(degrees=25, speed=20, clockwise=False)

        self.mover.rotate(clockwise=False, block=False)
        self.wait_for_white_cutoff(self.front_sensor)
        self.wait_for_black_cutoff(self.front_sensor)

        self.line_follower.follow_until_intersection_x(5, self.left_sensor)

        self.mover.rotate(clockwise=False, degrees=90, arc_radius=50)
        self.line_follower.follow_until_intersection_x(2, self.left_sensor, on_left=False)

        # Turn
        self.mover.rotate(clockwise=False, arc_radius=50, block=False)
        time.sleep(0.3)
        self.wait_for_white_cutoff(self.front_sensor)
        self.wait_for_black_cutoff(self.front_sensor)
        self.mover.stop()

        # Follow to drop off
        self.line_follower.follow_until_color(self.left_sensor, (sensors.YELLOW,), on_left=False, speed=20, kp=1.5,
                                              kd=0)
        self.mover.travel(speed=15, block=False)
        while not self.left_sensor.get_color() == sensors.WHITE:
            pass
        self.mover.stop()

        self.mover.travel(distance=10)

        self.lift.to_fibre()
        time.sleep(0.5)
        self.lift.up()

    def return_to_start(self):
        self.mover.rotate(degrees=90, backwards=True, arc_radius=400)
        self.mover.travel(backwards=True, block=False)
        time.sleep(5)
        self.mover.rotate(degrees=90, clockwise=False, arc_radius=75)
        self.mover.travel(backwards=True, block=False)

        # self.line_follower.follow_until_intersection_x(5, self.left_sensor, on_left=False)
        # self.mover.travel(100)
        # self.line_follower.follow_until_line(self.right_sensor)
        # self.mover.rotate(degrees=45)
        # self.mover.travel(block=False)
        # self.wait_for_white_cutoff(self.front_sensor)
        # self.wait_for_black_cutoff(self.front_sensor)
        # self.wait_for_white_cutoff(self.front_sensor)
        # self.line_follower

    ###############
    #  UTILITIES  #
    ###############

    @staticmethod
    def wait_for_black_cutoff(sensor, cutoff=40):
        while sensor.get_reflected() > cutoff:
            pass

    @staticmethod
    def wait_for_white_cutoff(sensor, cutoff=60):
        while sensor.get_reflected() < cutoff:
            pass

    @staticmethod
    def wait_for_colors(sensor, colors):
        while not sensor.get_color() in colors:
            pass

    def orient_block(self, color):
        try:
            index = self.color_codes.index(color)
        except:
            index = 0
            beep()
            beep()

        if color in (sensors.RED, sensors.BLUE):
            orientation = 0
        else:
            orientation = 180

        if index == 0:
            target = 0
        elif index == 1:
            target = 270
        elif index == 2:
            target = 180
        else:
            target = 90

        change = target - orientation

        if change < 0:
            change += 360

        if change == 0:
            self.swivel.forward()
        elif change == 90:
            self.swivel.left()
        elif change == 180:
            self.swivel.back()
        elif change == 270:
            self.swivel.right()

        return change


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
        main.teardown()

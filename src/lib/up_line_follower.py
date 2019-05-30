from lib.up_motors import Mover

import time
from lib.robot import *


class LineFollower:
    """Responsible for following a line using color sensors"""

    _MIDDLE_VALUE = 30

    _DEFAULT_KP = 0.3
    _DEFAULT_KD = 1
    # _DEFAULT_KI = 0
    _DEFAULT_SPEED = 70

    def __init__(self, mover: Mover, front_sensor,
                 back_sensor):
        self.mover = mover
        self.front_sensor = front_sensor
        self.back_sensor = back_sensor
        self.last_error = 0

    def follow(self,
               on_left=True,
               kp=_DEFAULT_KP,
               kd=_DEFAULT_KD,
               # ki=_DEFAULT_KI,
               speed=_DEFAULT_SPEED,
               backwards=False):
        """
        Method used to follow the line.
        """

        # total_error = 0

        if backwards:
            sensor_value = self.back_sensor.get_reflected()
        else:
            sensor_value = self.front_sensor.get_reflected()

        # graph.add_data_point(time.time(), sensor_value, "Sensor value")

        error = self._MIDDLE_VALUE - sensor_value

        # total_error += error

        direction = kp * error + kd * (
                error - self.last_error)  # + ki * total_error

        if on_left != backwards:
            direction *= -1

        if direction > 100:
            direction = 100
            print("Warning: Steering at +100")
        if direction < -100:
            direction = -100
            print("Warning: Steering at -100")

        self.mover.steer(direction, speed=(speed * (-0.8 if backwards else 1)))

        self.last_error = error

        # graph.save_to_file()


def follow_for_time(time_in_sec, **kwargs):
    start_time = time.time()

    while time.time() < start_time + time_in_sec:
        LINE_FOLLOWER.follow(kwargs)


def follow_until_color(color_sensor: sensors.ColorSensor, colours, **kwargs):
    while not color_sensor.get_color() in colours:
        LINE_FOLLOWER.follow(kwargs)


def follow_until_line(color_sensor: sensors.ColorSensor, **kwargs):
    follow_until_color(color_sensor, (sensors.BLACK,), **kwargs)


def follow_until_intersenction_x(number_of_intersections, color_sensor, include_initial_delay=True, **kwargs):
    if include_initial_delay:
        follow_for_time(0.3, **kwargs)

    for i in range(number_of_intersections):
        follow_until_line(color_sensor, **kwargs)

        if i != number_of_intersections - 1:
            follow_for_time(0.3)
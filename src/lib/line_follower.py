from lib.motors import Mover
from lib.sensors import ColorSensor
from typing import List
import lib.ports

import time
import abc
import main


class LineFollower:
    """Responsible for following a line using color sensors"""

    _MIDDLE_VALUE = 0.5

    _DEFAULT_KP = 0.25
    _DEFAULT_KD = 1.25
    _DEFAULT_KI = 0.000
    _DEFAULT_SPEED = 60

    def __init__(self, mover: Mover, port=lib.ports.LINE_FOLLOWER_COLOR_SENSOR):
        self.movement_controller = mover
        self.color_sensor = ColorSensor(port)

    def follow(self,
               callback,
               on_left=True,
               kp=_DEFAULT_KP,
               kd=_DEFAULT_KD,
               ki=_DEFAULT_KI,
               speed=_DEFAULT_SPEED):
        """
        Method used to follow the line.
        """

        last_error = 0
        total_error = 0
        stop_called = False

        def stop():
            nonlocal stop_called
            stop_called = True

        while not stop_called:
            error = self._MIDDLE_VALUE - self.color_sensor.get_reflected()

            total_error += error

            direction = kp * error + kd * (
                    error - last_error) + ki * total_error

            if on_left:
                direction *= -1

            if direction > 100:
                direction = 100
                print("Warning: Steering at +100")
            if direction < -100:
                direction = -100
                print("Warning: Steering at -100")

            self.movement_controller.steer(direction, speed=speed)

            last_error = error

            callback(stop)

        self.movement_controller.stop()


class StopIndicator(abc.ABC):

    @abc.abstractmethod
    def callback(self, stop):
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        pass

    def __call__(self, stop):
        self.callback(stop)


class StopAfterTime(StopIndicator):
    def __init__(self, delay):
        """
        :param delay: Time in seconds to wait before stopping
        """
        self.delay = delay
        self.end_time = None

    def callback(self, stop):
        current_time = self._get_time_in_seconds()

        if self.end_time is None:
            self.end_time = current_time + self.delay

        elif current_time > self.end_time:
            stop()

    def reset(self) -> None:
        self.end_time = None

    @staticmethod
    def _get_time_in_seconds():
        return time.time()


class StopAtColor(StopIndicator):
    def __init__(self, color_sensor: ColorSensor, colours):
        self.color_sensor = color_sensor
        self._colours = colours

    def callback(self, stop):
        color_reading = self.color_sensor.get_color()

        if color_reading in self._colours:
            main.Main.beep()
            stop()

    def reset(self) -> None:
        pass


class StopAtCrossLine(StopAtColor):
    def __init__(self, color_sensor: ColorSensor):
        super().__init__(color_sensor, (ColorSensor.BLACK,))
        self.color_sensor = color_sensor


class StopAfterXTimes(StopIndicator):
    def __init__(self, number_of_times, should_stop: StopIndicator):
        self.number_of_times = number_of_times
        self.should_stop = should_stop
        self.counter = 0

    def callback(self, stop):
        def _increment_counter():
            self.counter += 1
            self.should_stop.reset()

            if self.counter == self.number_of_times:
                stop()

        self.should_stop.callback(_increment_counter)

    def reset(self) -> None:
        self.counter = 0
        self.should_stop.reset()


class StopAfterMultiple(StopIndicator):
    def __init__(self, list_of_indicators: List[StopIndicator]):
        self.stop_indicators = list_of_indicators
        self.counter = 0

    def callback(self, stop):
        def _increment_counter():
            self.counter += 1

            if self.counter == len(self.stop_indicators):
                stop()

        self.stop_indicators[self.counter].callback(_increment_counter)

    def reset(self) -> None:
        self.counter = 0
        for stop_indicator in self.stop_indicators:
            stop_indicator.reset()


class StopNever(StopIndicator):

    def callback(self, stop):
        pass

    def reset(self) -> None:
        pass


def get_stop_after_x_intersections(number_of_intersections_to_pass, color_sensor_to_use, include_initial_delay=True):
    if include_initial_delay:
        return StopAfterXTimes(number_of_intersections_to_pass + 1,
                               StopAfterMultiple([
                                   StopAfterTime(300),
                                   StopAtCrossLine(color_sensor_to_use)])
                               )

    else:
        return StopAfterMultiple([
            StopAfterXTimes(number_of_intersections_to_pass,
                            StopAfterMultiple([
                                StopAtCrossLine(color_sensor_to_use),
                                StopAfterTime(300)
                            ])),
            StopAtCrossLine(color_sensor_to_use)
        ])

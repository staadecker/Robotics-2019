from lib.movement_controller import MovementController
from lib.color_sensor import ColorSensor
from typing import List

import datetime
import abc


class StopIndicator(abc.ABC):

    @abc.abstractmethod
    def should_end(self) -> bool:
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        pass


class LineFollower:
    """Responsible for following a line using color sensors"""

    _WHITE_REFLECTION = 1
    _BLACK_REFLECTION = 0
    _FRACTION_OF_DELTA = 0.5

    _MIDDLE_REFLECTION_VALUE = (_WHITE_REFLECTION - _BLACK_REFLECTION) * _FRACTION_OF_DELTA + _BLACK_REFLECTION

    _P_COEF = 0.2
    _D_COEF = 0

    def __init__(self, movement_controller: MovementController, left_color_sensor: ColorSensor,
                 right_color_sensor: ColorSensor):
        self.movement_controller = movement_controller
        self.left_color_sensor = left_color_sensor
        self.right_color_sensor = right_color_sensor

    def follow_on_left(self, stop_indicator: StopIndicator, stop=True, callback=None):
        self._follow_line(stop_indicator, self.left_color_sensor, True, stop=stop, callback=callback)

    def follow_on_right(self, stop_indicator: StopIndicator, stop=True, callback=None):
        self._follow_line(stop_indicator, self.right_color_sensor, False, stop=stop, callback=callback)

    def _follow_line(self, stop_indicator, color_sensor, inverse_correction, stop=True, callback=None):
        """
        Method used to follow the line.

        :param stop_indicator : Object that can be used to know when to stop following the line
        :param color_sensor : The color sensor to use for following
        :param stop : Determines if the line follower should stop following when finished or just pass over the control
        :param callback : method to be called repeatedly when following the line
        """

        last_error = 0
        flip_multiplication = -1 if inverse_correction else 1

        while not stop_indicator.should_end():
            error = self._MIDDLE_REFLECTION_VALUE - color_sensor.get_reflected()

            self.movement_controller.steer(
                (LineFollower._P_COEF * error + LineFollower._D_COEF * (error - last_error)) * flip_multiplication
            )

            last_error = error

            if callback is not None:
                callback()

        if stop:
            self.movement_controller.stop()


class StopAfterTime(StopIndicator):
    def __init__(self, delay):
        """
        :param delay: Time in milliseconds to wait before stopping
        """
        self.delay = delay
        self.end_time = None

    def should_end(self) -> bool:
        if self.end_time is None:
            self.end_time = self._get_time_in_millis() + self.delay

        return self._get_time_in_millis() > self.end_time

    def reset(self) -> None:
        self.end_time = None

    @staticmethod
    def _get_time_in_millis():
        return datetime.datetime.now().timestamp() * 1000


class StopAtCrossLine(StopIndicator):
    def __init__(self, color_sensor: ColorSensor):
        self.color_sensor = color_sensor

    def should_end(self) -> bool:
        return self.color_sensor.get_color() == ColorSensor.BLACK

    def reset(self) -> None:
        pass


class StopAfterXTimes(StopIndicator):
    def __init__(self, number_of_times, should_stop: StopIndicator):
        self.number_of_times = number_of_times
        self.should_stop = should_stop
        self.counter = 0

    def should_end(self) -> bool:
        if self.should_stop.should_end():
            self.counter += 1

            if self.counter == self.number_of_times:
                return True
            else:
                self.should_stop.reset()

        return False

    def reset(self) -> None:
        self.counter = 0
        self.should_stop.reset()


class StopAfterMultiple(StopIndicator):
    def __init__(self, list_of_indicators: List[StopIndicator]):
        self.stop_indicators = list_of_indicators
        self.counter = 0

    def should_end(self) -> bool:
        if self.stop_indicators[self.counter].should_end():
            self.counter += 1

            if self.counter == len(self.stop_indicators):
                return True

        return False

    def reset(self) -> None:
        self.counter = 0
        for stop_indicator in self.stop_indicators:
            stop_indicator.reset()


class StopNever(StopIndicator):

    def should_end(self) -> bool:
        return False

    def reset(self) -> None:
        pass


def get_stop_after_x_intersections(number_of_intersections_to_pass, color_sensor_to_use):
    return StopAfterMultiple([
        StopAfterXTimes(number_of_intersections_to_pass,
                        StopAfterMultiple([
                            StopAtCrossLine(color_sensor_to_use),
                            StopAfterTime(1000)])
                        ),
        StopAtCrossLine(color_sensor_to_use)
    ])

from lib.motors import Mover
from lib.sensors import ColorSensor
from typing import List
import lib.ports

import datetime
import abc
import lib.robot


class StopIndicator(abc.ABC):

    @abc.abstractmethod
    def should_end(self) -> bool:
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        pass


class LineFollower:
    """Responsible for following a line using color sensors"""

    _WHITE_REFLECTION = 85
    _BLACK_REFLECTION = 10
    _FRACTION_OF_DELTA = 0.5

    _DEFAULT_KP = 0.25
    _DEFAULT_KD = 1.25
    _DEFAULT_KI = 0.000
    _DEFAULT_SPEED = 35
    _DEFAULT_SLOW_SPEED = 20

    _DEFAULT_SLOW_KP = 0.4
    _DEFAULT_SLOW_KD = 1.25
    _DEFAULT_SLOW_KI = 0.000

    _MIDDLE_REFLECTION_VALUE = (_WHITE_REFLECTION - _BLACK_REFLECTION) * _FRACTION_OF_DELTA + _BLACK_REFLECTION

    def __init__(self, mover: Mover, port=lib.ports.LINE_FOLLOWER_COLOR_SENSOR):
        self.movement_controller = mover
        self.color_sensor = ColorSensor(port)

    def follow_on_left(self, stop_indicator: StopIndicator, **kwargs):
        self._follow_line(stop_indicator, True, **kwargs)

    def follow_on_right(self, stop_indicator: StopIndicator, **kwargs):
        self._follow_line(stop_indicator, False, **kwargs)

    def _follow_line(self, stop_indicator, inverse_correction, stop=True, callback=None, slow=False,
                     kp=None, kd=None, ki=None):
        """
        Method used to follow the line.

        :param stop_indicator : Object that can be used to know when to stop following the line
        :param stop : Determines if the line follower should stop following when finished or just pass over the control
        :param callback : method to be called repeatedly when following the line
        """

        last_error = 0
        total_error = 0
        error_was_positive = True

        speed = LineFollower._DEFAULT_SLOW_SPEED if slow else LineFollower._DEFAULT_SPEED

        if kp is None:
            kp = LineFollower._DEFAULT_SLOW_KP if slow else LineFollower._DEFAULT_KP

        if kd is None:
            kd = LineFollower._DEFAULT_SLOW_KD if slow else LineFollower._DEFAULT_KD

        if ki is None:
            ki = LineFollower._DEFAULT_SLOW_KI if slow else LineFollower._DEFAULT_KI

        while not stop_indicator.should_end():
            error = self._MIDDLE_REFLECTION_VALUE - self.color_sensor.get_reflected()

            error_is_positive = (True if error > 0 else False)
            if error_was_positive != error_is_positive:
                total_error = 0
                error_was_positive = error_is_positive

            total_error += error

            direction = kp * error + kd * (
                    error - last_error) + ki * total_error

            if inverse_correction:
                direction *= -1

            # print(direction)

            if direction > 100:
                direction = 100
                print("Warning: Steering at +100")
            if direction < -100:
                direction = -100
                print("Warning: Steering at -100")

            self.movement_controller.steer(direction, speed=speed)

            last_error = error

            if callback is not None:
                callback()

        #self.movement_controller.travel(10)

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


class StopAtColor(StopIndicator):

    def __init__(self, color_sensor: ColorSensor, colours):
        self.color_sensor = color_sensor
        self._colours = colours
        self._times_where_got_correct_color = 0

    def should_end(self) -> bool:
        color_reading = self.color_sensor.get_color()

        if color_reading in self._colours:
            self._times_where_got_correct_color += 1

        if self._times_where_got_correct_color > 0:
            lib.robot.Robot.beep()
            return True

        return False

    def reset(self) -> None:
        self._times_where_got_correct_color = 0


class StopAtCrossLine(StopAtColor):
    def __init__(self, color_sensor: ColorSensor):
        super().__init__(color_sensor, (ColorSensor.BLACK, ColorSensor.BROWN))
        self.color_sensor = color_sensor


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

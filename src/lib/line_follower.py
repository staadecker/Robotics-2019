from lib.motors import Mover
import lib.sensors as sensors
import lib.ports

import time
import main


class LineFollower:
    """Responsible for following a line using color sensors"""

    _MIDDLE_VALUE = 0.5

    _DEFAULT_KP = 0.7
    _DEFAULT_KD = 1.25
    _DEFAULT_KI = 0.000
    _DEFAULT_SPEED = 60

    def __init__(self, mover: Mover):
        self.movement_controller = mover
        self.front_sensor = sensors.EV3ColorSensor(lib.ports.FRONT_SENSOR)
        self.back_sensor = sensors.EV3ColorSensor(lib.ports.BACK_SENSOR)

    def follow(self,
               callback,
               on_left=True,
               kp=_DEFAULT_KP,
               kd=_DEFAULT_KD,
               ki=_DEFAULT_KI,
               speed=_DEFAULT_SPEED,
               backwards=False):
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
            error = self._MIDDLE_VALUE - self.front_sensor.get_reflected()

            total_error += error

            direction = kp * error + kd * (
                    error - last_error) + ki * total_error

            if on_left != backwards:
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


class StopIndicator:
    def callback(self, stop):
        print("WARNING: not implemented, callback in stop indicator")

    def reset(self) -> None:
        print("WARNING: not implemented, reset in stop indicator")

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
    def __init__(self, color_sensor: sensors.ColorSensor, colours):
        self.color_sensor = color_sensor
        self._colours = colours

    def callback(self, stop):
        color_reading = self.color_sensor.get_color()

        if color_reading in self._colours:
            main.beep()
            stop()

    def reset(self) -> None:
        pass


class StopAtCrossLine(StopAtColor):
    def __init__(self, color_sensor: sensors.ColorSensor):
        super().__init__(color_sensor, (sensors.BLACK,))
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
    def __init__(self, list_of_indicators):
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
                                   StopAfterTime(0.3),
                                   StopAtCrossLine(color_sensor_to_use)])
                               )

    else:
        return StopAfterMultiple([
            StopAfterXTimes(number_of_intersections_to_pass,
                            StopAfterMultiple([
                                StopAtCrossLine(color_sensor_to_use),
                                StopAfterTime(0.3)
                            ])),
            StopAtCrossLine(color_sensor_to_use)
        ])

from lib.up_motors import Mover
import lib.up_sensors as sensors
import lib.up_ports as ports

import time
import os

# class Graph:
#     def __init__(self):
#         self.times = []
#         self.values = []
#         self.types = []

#     def add_data_point(self, times, values, types):
#         self.times.append(times)
#         self.values.append(values)
#         self.types.append(types)

#     def save_to_file(self):
#         with open('graph_output.csv', mode="w") as my_file:
#             for i in range(len(self.times)):
#                 my_file.write([self.times[i], self.values[i], self.types[i]])


class LineFollower:
    """Responsible for following a line using color sensors"""

    _MIDDLE_VALUE = 30

    _DEFAULT_KP = 0.3
    _DEFAULT_KD = 1
    _DEFAULT_KI = 0
    _DEFAULT_SPEED = 70

    def __init__(self, mover: Mover):
        self.mover = mover
        self.front_sensor = sensors.EV3ColorSensor(ports.FRONT_SENSOR)
        self.back_sensor = sensors.EV3ColorSensor(ports.BACK_SENSOR)

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

        # graph = Graph()

        def stop():
            nonlocal stop_called
            stop_called = True

        while not stop_called:
            if backwards:
                sensor_value = self.back_sensor.get_reflected()
            else:
                sensor_value = self.front_sensor.get_reflected()

            # graph.add_data_point(time.time(), sensor_value, "Sensor value")

            error = self._MIDDLE_VALUE - sensor_value
            

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

            self.mover.steer(direction, speed=(speed * (-0.8 if backwards else 1)))

            last_error = error

            callback(stop, sensor_value)

        self.mover.stop()

        # graph.save_to_file()


class StopIndicator:
    def callback(self, stop, value):
        print("WARNING: not implemented, callback in stop indicator")

    def reset(self) -> None:
        print("WARNING: not implemented, reset in stop indicator")

    def __call__(self, stop, value):
        self.callback(stop, value)


class StopAfterTime(StopIndicator):
    def __init__(self, delay):
        """
        :param delay: Time in seconds to wait before stopping
        """
        self.delay = delay
        self.end_time = None

    def callback(self, stop, value):
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

    def callback(self, stop, value):
        color_reading = self.color_sensor.get_color()

        if color_reading in self._colours:
            #os.system("/usr/bin/beep")
            print("Detected line")
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

    def callback(self, stop, value):
        def _increment_counter():
            self.counter += 1
            self.should_stop.reset()

            if self.counter == self.number_of_times:
                stop()

        self.should_stop.callback(_increment_counter, value)

    def reset(self) -> None:
        self.counter = 0
        self.should_stop.reset()


class StopAfterMultiple(StopIndicator):
    def __init__(self, list_of_indicators):
        self.stop_indicators = list_of_indicators
        self.counter = 0

    def callback(self, stop, value):
        def _increment_counter():
            self.counter += 1

            if self.counter == len(self.stop_indicators):
                stop()

        self.stop_indicators[self.counter].callback(_increment_counter, value)

    def reset(self) -> None:
        self.counter = 0
        for stop_indicator in self.stop_indicators:
            stop_indicator.reset()


class StopNever(StopIndicator):

    def callback(self, stop, value):
        pass

    def reset(self) -> None:
        pass

# class StopOnIntersectionsX(StopIndicator):
#     def __init__(self, number_of_intersections_to_pass, color_sensor_to_use):
#         self.number_of_intersections_to_pass = number_of_intersections_to_pass
#         self.color_sensor = color_sensor_to_use
#         self.number_of_intersections_passed = 0
#         self.can_start_scaning_at = None
    
#     def callback(self, stop):
#         if self.can_start_scaning_at is None:
#             self.can_start_scaning_at = time.time() + 0.3
#             return

#         if time.time() > self.can_start_scaning_at:
#             if self.color_sensor.get_color() == sensors.BLACK:
#                 self.number_of_intersections_passed +=1
                
#                 if self.number_of_intersections_passed == self.number_of_intersections_to_pass:
#                     stop()
#                     return

#                 self.can_start_scaning_at = time.time() + 0.3

                
        





def StopAtIntersectionX(number_of_intersections_to_pass, color_sensor_to_use, include_initial_delay=True):
    if include_initial_delay:
        return StopAfterXTimes(number_of_intersections_to_pass,
                               StopAfterMultiple([
                                   StopAfterTime(0.3),
                                   StopAtCrossLine(color_sensor_to_use)])
                               )

    else:
        return StopAfterMultiple([
            StopAfterXTimes(number_of_intersections_to_pass -1,
                            StopAfterMultiple([
                                StopAtCrossLine(color_sensor_to_use),
                                StopAfterTime(0.3)
                            ])),
            StopAtCrossLine(color_sensor_to_use)
        ])

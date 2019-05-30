import time
import lib.up_sensors as sensors


class LineFollower:
    """Responsible for following a line using color sensors"""

    _MIDDLE_VALUE = 30

    _DEFAULT_KP = 0.3
    _DEFAULT_KD = 1
    _DEFAULT_SPEED = 65

    def __init__(self, mover, front_sensor, back_sensor):
        self.mover = mover
        self.back_sensor = back_sensor
        self.front_sensor = front_sensor
        self.last_error = None

    def follow(self,
               on_left=True,
               kp=_DEFAULT_KP,
               kd=_DEFAULT_KD,
               speed=_DEFAULT_SPEED,
               backwards=False):
        """
        Method used to follow the line.
        """

        if backwards:
            sensor_value = self.back_sensor.get_reflected()
        else:
            sensor_value = self.front_sensor.get_reflected()

        error = self._MIDDLE_VALUE - sensor_value

        if self.last_error is None:
            direction = kp * error
        else:
            direction = kp * error + kd * (error - self.last_error)

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

    def follow_for_time(self, time_in_sec, stop=True, **kwargs):
        start_time = time.time()

        while time.time() < start_time + time_in_sec:
            self.follow(**kwargs)

        if stop:
            self.mover.stop()

    def follow_until_color(self, color_sensor: sensors.ColorSensor, colours, stop=True, **kwargs):
        while not color_sensor.get_color() in colours:
            self.follow(**kwargs)

        print("MARK")
        if stop:
            self.mover.stop()
            self.last_error = None

    def follow_until_line(self, color_sensor: sensors.ColorSensor, stop=True, **kwargs):
        self.follow_until_color(color_sensor, (sensors.BLACK,), stop=stop, **kwargs)

    def follow_until_intersection_x(self, number_of_intersections, color_sensor, include_initial_delay=False, stop=True,
                                    **kwargs):
        if include_initial_delay:
            self.follow_for_time(0.3, stop=False, **kwargs)

        for i in range(number_of_intersections):
            self.follow_until_line(color_sensor, stop=False, **kwargs)

            if i != number_of_intersections - 1:
                self.follow_for_time(0.3, stop=False, **kwargs)

        if stop:
            self.mover.stop()
            self.last_error = None
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
        self.direction = None

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
            self.direction = kp * error
        else:
            self.direction = kp * error + kd * (error - self.last_error)

        if on_left != backwards:
            self.direction *= -1

        if self.direction > 100:
            self.direction = 100
            print("Warning: Steering at +100")
        if self.direction < -100:
            self.direction = -100
            print("Warning: Steering at -100")

        self.mover.steer(self.direction, speed=(speed * (-0.8 if backwards else 1)))

        self.last_error = error

    def follow_for_time(self, time_in_sec, stop=True, **kwargs):
        start_time = time.time()

        while time.time() < start_time + time_in_sec:
            self.follow(**kwargs)

        if stop:
            self.mover.stop()
            self.reset()

    def follow_until_color(self, color_sensor: sensors.ColorSensor, colours, stop=True, **kwargs):
        while not color_sensor.get_color() in colours:
            self.follow(**kwargs)

        print("Mark")
        if stop:
            self.mover.stop()
            self.reset()

    def follow_until_line(self, color_sensor: sensors.ColorSensor, stop=True, **kwargs):
        self.follow_until_color(color_sensor, (sensors.BLACK,), stop=stop, **kwargs)

    def follow_until_intersection_x(self, number_of_intersections, color_sensor, include_initial_delay=False, stop=True, use_reflection=False,
                                    **kwargs):
        if include_initial_delay:
            self.follow_for_time(0.1, stop=False, **kwargs)

        for i in range(number_of_intersections):
            if use_reflection:
                self.follow_until_cutoff(color_sensor, 40, False, stop=False, **kwargs)
            else:
                self.follow_until_line(color_sensor, stop=False, **kwargs)

            if i != number_of_intersections - 1:
                if use_reflection:
                    self.follow_until_cutoff(color_sensor, 50, True, stop=False, **kwargs)
                else:
                    self.follow_for_time(0.1, stop=False, **kwargs)

        if stop:
            self.mover.stop()
            self.reset()

    def follow_until_cutoff(self, sensor: sensors.EV3ColorSensor, cutoff, greater_than, stop=True, **kwargs):
        if greater_than:
            while sensor.get_reflected() < cutoff:
                self.follow(**kwargs)
        else:
            while sensor.get_reflected() > cutoff:
                self.follow(**kwargs)

        if stop:
            self.mover.stop()
            self.reset()

    def follow_until_constant(self, stop=True, cutoff=6, cycles=10, use_correction=True, **kwargs):
        def get_value():
            if use_correction:
                return self.direction
            else:
                return self.last_error
        
        in_a_row = 0
        while True:
            print(get_value())
            self.follow(**kwargs)
            if get_value() is None:
                in_a_row = 0
                continue

            in_a_row += 1

            if abs(get_value()) > cutoff:
                in_a_row = 0

            if in_a_row == cycles:
                break

        if stop:
            self.mover.stop()
            self.reset()

    def follow_until_change(self, stop=True, cutoff=10, cycles=10,  use_correction=True, **kwargs):
        def get_value():
            if use_correction:
                return self.direction
            else:
                return self.last_error
        in_a_row = 0
        while True:
            print(get_value())
            self.follow(**kwargs)
            if get_value() is None:
                in_a_row = 0
                continue

            in_a_row += 1

            if abs(get_value()) < cutoff:
                in_a_row = 0

            if in_a_row == cycles:
                break

        if stop:
            self.mover.stop()
            self.reset()

    def reset(self):
        self.last_error = None

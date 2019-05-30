import time
import lib.up_sensors as sensors
import lib.up_robot as robot


class LineFollower:
    """Responsible for following a line using color sensors"""

    _MIDDLE_VALUE = 30

    _DEFAULT_KP = 0.3
    _DEFAULT_KD = 0.6
    _DEFAULT_SPEED = 70

    def __init__(self):
        self.last_error = 0

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
            sensor_value = robot.BACK_SENSOR.get_reflected()
        else:
            sensor_value = robot.FRONT_SENSOR.get_reflected()

        error = self._MIDDLE_VALUE - sensor_value

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

        robot.MOVER.steer(direction, speed=(speed * (-0.8 if backwards else 1)))

        self.last_error = error

        # graph.save_to_file()


LINE_FOLLOWER = LineFollower()


def follow_for_time(time_in_sec, stop=True, **kwargs):
    start_time = time.time()

    while time.time() < start_time + time_in_sec:
        LINE_FOLLOWER.follow(**kwargs)

    if stop:
        robot.MOVER.stop()


def follow_until_color(color_sensor: sensors.ColorSensor, colours, stop=True, **kwargs):
    while not color_sensor.get_color() in colours:
        LINE_FOLLOWER.follow(**kwargs)

    if stop:
        robot.MOVER.stop()


def follow_until_line(color_sensor: sensors.ColorSensor, stop=True, **kwargs):
    follow_until_color(color_sensor, (sensors.BLACK,), stop=stop, **kwargs)


def follow_until_intersection_x(number_of_intersections, color_sensor, include_initial_delay=True, stop=True,
                                **kwargs):
    if include_initial_delay:
        follow_for_time(0.3, stop=False, **kwargs)

    for i in range(number_of_intersections):
        follow_until_line(color_sensor, stop=False, **kwargs)

        if i != number_of_intersections - 1:
            follow_for_time(0.3, stop=False, **kwargs)

    if stop:
        robot.MOVER.stop()

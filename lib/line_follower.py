from movement_controller import MovementController
from color_sensor import ColorSensorWrapper

WHITE_REFLECTION = 1
BLACK_REFLECTION = 0
PERCENTAGE_OF_MIDDLE = 0.5
KP_FACTOR = 1


class LineFollower:
    """Responsible for following a line using color sensors"""

    def __init__(self, movement_controller: MovementController, left_color_sensor: ColorSensorWrapper,
                 right_color_sensor: ColorSensorWrapper):
        self.movement_controller = movement_controller
        self.left_color_sensor = left_color_sensor
        self.right_color_sensor = right_color_sensor
        self.middle_value = (WHITE_REFLECTION - BLACK_REFLECTION) * PERCENTAGE_OF_MIDDLE + BLACK_REFLECTION

    def follow_line(self, should_stop_following, use_left_sensor=True):
        """
        Method used to follow the line.
        Parameters:
            should_stop_following : Method returning true or false depending on whether the line follower should stop
            use_left_sensor : Determines whether it should follow the line with the left color sensor or the right one
        """

        while not should_stop_following():
            if use_left_sensor:
                correction = KP_FACTOR * (self.middle_value - self.left_color_sensor.get_reflected())
                self.movement_controller.steer(correction)
            else:
                correction = KP_FACTOR * (self.middle_value - self.right_color_sensor.get_reflected())
                self.movement_controller.steer(correction * -1)

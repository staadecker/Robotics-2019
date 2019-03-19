from movement_controller import MovementController


class LineFollower:
    """Responsible for following a line using color sensors"""

    def __init__(self, movement_controller, left_color_sensor, right_color_sensor):
        self.movement_controller = movement_controller
        self.left_color_sensor = left_color_sensor
        self.right_color_sensor = right_color_sensor

    def follow_line(self, should_stop_following, use_left_sensor=True):
        """
        Method used to follow the line.
        Parameters:
            should_stop_following : Method returning true or false depending on whether the line follower should stop
            use_left_sensor : Determines whether it should follow the line with the left color sensor or the right one
        """
        pass  # TODO

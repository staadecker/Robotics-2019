import abc


class BaseLineFollower(abc.ABC):
    """Responsible for following a line using color sensors"""

    @abc.abstractmethod
    def follow_line(self, should_stop_following, use_left_sensor=True):
        """
        Method used to follow the line.
        Parameters:
            should_stop_following : Method returning true or false depending on whether the line follower should stop
            use_left_sensor : Determines whether it should follow the line with the left color sensor or the right one
        """
        pass # TODO

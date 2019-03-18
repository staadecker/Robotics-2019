import abc
from ev3dev2.motor import MoveSteering, SpeedPercent
import constants


class BaseMovementController(abc.ABC):
    """Interface of the controller that moves the robot"""

    @abc.abstractmethod
    def rotate(self, degrees, speed=100, block=True):
        """Rotate the robot a certain number of degrees"""
        pass

    @abc.abstractmethod
    def travel(self, distance, speed=100, block=True):
        """Make the robot move forward or backward a certain number of cm"""
        pass

    @abc.abstractmethod
    def steer(self, direction, speed=100):
        """Make the robot move in a direction"""
        pass

    @abc.abstractmethod
    def stop(self):
        """Make robot stop"""
        pass


# TODO Test
class MovementController(BaseMovementController):
    _ROTATION_TO_DEGREE = 1
    _DISTANCE_TO_DEGREE = 1

    def __init__(self):
        self.moveSteering = MoveSteering(constants.LEFT_MOTOR_PORT, constants.RIGHT_MOTOR_PORT)

    def rotate(self, degrees, speed=100, block=True):
        self.moveSteering.on_for_degrees(100, SpeedPercent(speed), degrees * MovementController._ROTATION_TO_DEGREE,
                                         block=block)

    def travel(self, distance, speed=100, block=True):
        self.moveSteering.on_for_degrees(0, speed, distance * MovementController._DISTANCE_TO_DEGREE, block=block)

    def steer(self, direction, speed=100):
        self.moveSteering.on(direction, speed)

    def stop(self):
        self.moveSteering.off()

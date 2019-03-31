import ev3dev2.motor as base_motor
import constants
import math


# TODO Test
class MovementController:
    """Class to move the robot"""

    _WHEEL_RADIUS = 6.16
    _DISTANCE_BETWEEN_WHEELS = 8

    _ANGLE_TO_DEGREES = _DISTANCE_BETWEEN_WHEELS / _WHEEL_RADIUS / 2
    _DISTANCE_TO_DEGREES = 360 / (_WHEEL_RADIUS * math.pi)

    def __init__(self):
        self.moveSteering = base_motor.MoveSteering(constants.LEFT_MOTOR_PORT, constants.RIGHT_MOTOR_PORT)

    def rotate(self, degrees, speed=100, block=True):
        """Rotate the robot a certain number of degrees. Positive is counter-clockwise"""
        self.moveSteering.on_for_degrees(100, base_motor.SpeedPercent(speed),
                                         degrees * MovementController._ANGLE_TO_DEGREES,
                                         block=block)

    def travel(self, distance, speed=100, block=True):
        """Make the robot move forward or backward a certain number of cm"""
        self.moveSteering.on_for_degrees(0, speed, distance * MovementController._DISTANCE_TO_DEGREES, block=block)

    def steer(self, direction, speed=100):
        """Make the robot move in a direction"""
        self.moveSteering.on(direction, speed)

    def stop(self):
        """Make robot stop"""
        self.moveSteering.off()

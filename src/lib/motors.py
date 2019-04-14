import math

import ev3dev2.motor

import lib.constants
from lib import constants


class ArmController:
    """Class to control arm of robot"""

    _ACCELERATION = 100  # Time in milliseconds the motor would take to reach 100% max speed from not moving
    _DEFAULT_SPEED = 30
    _DEFAULT_SPEED_WITH_OBJECT = 10

    # Degrees predictions for arm
    _DEG_TO_FIBRE_OPTIC = 105  # TODO Correct
    _DEG_TO_DEVICE = 70

    def __init__(self):
        self._arm = ev3dev2.motor.LargeMotor(lib.constants.ARM_MOTOR_PORT)
        self._arm.stop_action = ev3dev2.motor.Motor.STOP_ACTION_HOLD
        self._arm.ramp_up_sp = self._ACCELERATION
        self._arm.ramp_down_sp = self._ACCELERATION

        self._arm_is_raised = False

    def raise_arm(self, slow=False):
        """Resets arm to raised position"""

        speed = self._DEFAULT_SPEED_WITH_OBJECT if slow else self._DEFAULT_SPEED

        if not self._arm_is_raised:
            self._arm.on(speed * -1)
            self._arm.wait_until_not_moving()

            self._arm.on_for_degrees(speed, 20)

            self._arm_is_raised = True

    def lower_to_device(self, slow=False, block=True):
        """Lowers arm the degrees to pick up device"""

        speed = self._DEFAULT_SPEED_WITH_OBJECT if slow else self._DEFAULT_SPEED

        if self._arm_is_raised:
            self._arm.on_for_degrees(speed, self._DEG_TO_DEVICE, block=block)

            self._arm_is_raised = False

    def lower_to_fibre_optic(self, slow=False, block=True):
        """Lowers arm the degrees to pick up fibre optic cable"""

        speed = self._DEFAULT_SPEED_WITH_OBJECT if slow else self._DEFAULT_SPEED

        if self._arm_is_raised:
            self._arm.on_for_degrees(speed, self._DEG_TO_FIBRE_OPTIC, block=block)

            self._arm_is_raised = False


class SwivelController:
    """Class to control the robot's swivel"""

    _ACCELERATION = 100  # Time in milliseconds the motor would take to reach 100% max speed from not moving
    _DEFAULT_SPEED = 40  # In percent

    def __init__(self):
        self._swivel = ev3dev2.motor.MediumMotor(lib.constants.SWIVEL_MOTOR_PORT)
        self._swivel.ramp_up_sp = self._ACCELERATION
        self._swivel.ramp_down_sp = self._ACCELERATION
        self._swivel.position = self._convert_deg_to_pos(90)
        self._swivel.stop_action = ev3dev2.motor.Motor.STOP_ACTION_HOLD

    def point_forward(self, speed=_DEFAULT_SPEED, block=True):
        self._swivel.on_to_position(speed, 0, block=block)

    def point_left(self, speed=_DEFAULT_SPEED, block=True):
        self._swivel.on_to_position(speed, self._convert_deg_to_pos(90), block=block)

    def point_right(self, speed=_DEFAULT_SPEED, block=True):
        self._swivel.on_to_position(speed, self._convert_deg_to_pos(-90), block=block)

    def point_backwards(self, speed=_DEFAULT_SPEED, block=True):
        self._swivel.on_to_position(speed, self._convert_deg_to_pos(180), block=block)

    def _convert_deg_to_pos(self, degrees):
        return degrees * self._swivel.count_per_rot / 360


class Mover:
    """Class to move the robot"""

    _WHEEL_RADIUS = 40.8
    CHASSIS_RADIUS = 57.5

    _DEFAULT_SPEED = 15
    _DEFAULT_ROTATE_SPEED = 15

    def __init__(self, reverse_motors=False):
        self._control = ev3dev2.motor.MoveTank(constants.LEFT_MOTOR_PORT, constants.RIGHT_MOTOR_PORT)

        for motor in self._control.motors.values():
            if reverse_motors:
                motor.polarity = ev3dev2.motor.Motor.POLARITY_INVERSED
            else:
                motor.polarity = ev3dev2.motor.Motor.POLARITY_NORMAL

    def travel(self, distance, speed=_DEFAULT_SPEED, block=True, backwards=False):
        """Make the robot move forward or backward a certain number of mm"""
        degrees_for_wheel = Mover._convert_rad_to_deg(Mover._convert_distance_to_rad(distance))
        if backwards:
            self._control.on_for_degrees(-speed, -speed, degrees_for_wheel, block=block)
        else:
            self._control.on_for_degrees(speed, speed, degrees_for_wheel, block=block)

    def rotate(self, degrees=None, arc_radius=0, clockwise=True, speed=_DEFAULT_ROTATE_SPEED, block=True,
               backwards=False) -> None:
        """
        :param arc_radius: the radius or tightness of the turn in mm. 0 means the robot is turning on itself.
        :param degrees: the degrees the robot should rotate
        :param clockwise: the direction of rotation
        :param speed: the speed the fastest wheel should travel
        :param block: whether to return immediately or to wait for end of movement
        :param backwards: whether the rotate movement should move the robot backwards
        """
        if degrees <= 0:
            raise ValueError("Can't rotate a negative number of degrees. Use clockwise=False to turn counter-clockwise")

        if degrees is None:
            if block:
                raise ValueError("Can't run forever with block=True")

            inside_speed = (arc_radius - Mover.CHASSIS_RADIUS) / (arc_radius + Mover.CHASSIS_RADIUS) * speed

            if clockwise:
                if backwards:
                    self._control.on(-inside_speed, -speed)
                else:
                    self._control.on(speed, inside_speed)
            else:
                if backwards:
                    self._control.on(-speed, -inside_speed)
                else:
                    self._control.on(inside_speed, speed)
        else:
            degrees_in_rad = Mover._convert_deg_to_rad(degrees)
            inside_distance = (arc_radius - Mover.CHASSIS_RADIUS) * degrees_in_rad
            outside_distance = (arc_radius + Mover.CHASSIS_RADIUS) * degrees_in_rad

            time = outside_distance / speed
            inside_speed = inside_distance / time
            outside_degrees = Mover._convert_rad_to_deg(Mover._convert_distance_to_rad(outside_distance))

            if clockwise:
                if backwards:
                    self._control.on_for_degrees(-inside_speed, -speed, outside_degrees, block=block)
                else:
                    self._control.on_for_degrees(speed, inside_speed, outside_degrees, block=block)
            else:
                if backwards:
                    self._control.on_for_degrees(-speed, -inside_speed, outside_degrees, block=block)
                else:
                    self._control.on_for_degrees(inside_speed, speed, outside_degrees, block=block)

    def steer(self, steering, speed=_DEFAULT_SPEED):
        """Make the robot move in a direction. -100 is to the left. +100 is to the right. 0 is straight"""

        # Modified code from ev3dev2.robot.MoveSteering

        if steering < -100 or steering > 100:
            raise ValueError("Steering, must be between -100 and 100 (inclusive)")

        inside_speed = speed - speed * abs(steering) / 50

        if steering >= 0:
            self._control.on(speed, inside_speed)
        else:
            self._control.on(inside_speed, speed)

    def stop(self):
        """Make robot stop"""
        self._control.off()

    @staticmethod
    def _convert_distance_to_rad(distance):
        return distance / Mover._WHEEL_RADIUS

    @staticmethod
    def _convert_deg_to_rad(deg):
        return deg * math.pi / 180

    @staticmethod
    def _convert_rad_to_deg(rad):
        return rad / math.pi * 180

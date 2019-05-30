import math

import ev3dev2.motor
import lib.up_ports as ports
import time

class Lift:
    """Class to control arm of robot"""

    _ACCELERATION = 1000  # Time in milliseconds the motor would take to reach 100% max speed from not moving
    _DEFAULT_SPEED = 80

    # Degrees predictions for arm
    _DEG_TO_FIBRE = 580
    _DEG_TO_NODE = 500

    _POS_UP = 0
    _POS_FIBRE = 1
    _POS_NODE = 2

    def __init__(self):
        self._position = self._POS_UP
        self._lift = ev3dev2.motor.MediumMotor(ports.LIFT_MOTOR)

        self._lift.ramp_up_sp = self._ACCELERATION

        self._lift.polarity = ev3dev2.motor.Motor.POLARITY_NORMAL

    def calibrate(self):
        self._lift.on(self._DEFAULT_SPEED)
        self._lift.wait_until_not_moving()

        self._lift.on_for_degrees(-self._DEFAULT_SPEED, 50, block=True)

        self._position = self._POS_UP

    def up(self, block=True):
        if self._position == self._POS_FIBRE:
            self._lift.on_for_degrees(self._DEFAULT_SPEED, self._DEG_TO_FIBRE, block=block)

            self._position = self._POS_UP
        elif self._position == self._POS_NODE:
            self._lift.on_for_degrees(self._DEFAULT_SPEED, self._DEG_TO_NODE, block=block)

            self._position = self._POS_UP
        else:
            print("WARNING: called Lift.up() when already up")

    def to_fibre(self, block=True):
        """Lowers arm the degrees to pick up the fibre"""

        if self._position == self._POS_UP:
            self._lift.on_for_degrees(-self._DEFAULT_SPEED, self._DEG_TO_FIBRE, block=block)

            self._position = self._POS_FIBRE
        else:
            print("WARNING: called Lift.to_fibre() when not in up position")

    def to_node(self, block=True):
        """Lowers arm the degrees to pick up the fibre"""

        if self._position == self._POS_UP:
            self._lift.on_for_degrees(-self._DEFAULT_SPEED, self._DEG_TO_NODE, block=block)

            self._position = self._POS_NODE
        else:
            print("WARNING: called Lift.to_fibre() when not in up position")


class Swivel:
    """Class to control the robot's swivel"""

    _ACCELERATION = 300  # Time in milliseconds the motor would take to reach 100% max speed from not moving
    _DEFAULT_SPEED = 80  # In percent
    _START_POSITION = 0

    def __init__(self):
        self._swivel = ev3dev2.motor.MediumMotor(ports.SWIVEL_MOTOR)
        self._swivel.ramp_up_sp = self._ACCELERATION
        self._swivel.ramp_down_sp = self._ACCELERATION
        self._swivel.position = self._START_POSITION
        self._swivel.stop_action = ev3dev2.motor.Motor.STOP_ACTION_HOLD

    def forward(self, block=False):
        self._swivel.on_to_position(self._DEFAULT_SPEED, 0, block=block)

    def left(self, block=False):
        self._swivel.on_to_position(self._DEFAULT_SPEED, 90, block=block)

    def right(self, block=False):
        self._swivel.on_to_position(self._DEFAULT_SPEED, -90, block=block)

    def back(self, block=False):
        self._swivel.on_to_position(self._DEFAULT_SPEED, 180, block=block)

    def reset(self):
        self._swivel.on_to_position(self._DEFAULT_SPEED, self._START_POSITION)


class Mover:
    """Class to move the robot"""

    _WHEEL_RADIUS = 28
    CHASSIS_RADIUS = 67

    _DEFAULT_SPEED = 40
    _DEFAULT_ROTATE_SPEED = 30
    _RAMP_UP = 300
    _RAMP_DOWN = 300

    def __init__(self, reverse_motors=False):
        self._mover = ev3dev2.motor.MoveTank(ports.LEFT_MOTOR, ports.RIGHT_MOTOR,
                                             motor_class=ev3dev2.motor.MediumMotor)

        self._mover.left_motor.ramp_up_sp = self._RAMP_UP
        self._mover.right_motor.ramp_up_sp = self._RAMP_UP
        self._mover.left_motor.ramp_down_sp = self._RAMP_DOWN
        self._mover.right_motor.ramp_down_sp = self._RAMP_DOWN

        for motor in self._mover.motors.values():
            if reverse_motors:
                motor.polarity = ev3dev2.motor.Motor.POLARITY_INVERSED
            else:
                motor.polarity = ev3dev2.motor.Motor.POLARITY_NORMAL

    def travel(self, distance=None, speed=_DEFAULT_SPEED, block=True, backwards=False):
        """Make the robot move forward or backward a certain number of mm"""
        if distance is None:
            if block:
                raise ValueError("Can't run forever with block=True")
            if backwards:
                self._mover.on(-speed, -speed)
            else:
                self._mover.on(speed, speed)
        else:
            degrees_for_wheel = Mover._convert_rad_to_deg(Mover._convert_distance_to_rad(distance))
            if backwards:
                self._mover.on_for_degrees(-speed, -speed, degrees_for_wheel, block=block)
            else:
                self._mover.on_for_degrees(speed, speed, degrees_for_wheel, block=block)
            
            if block:
                time.sleep(0.1)

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

        if degrees is None:
            if block:
                raise ValueError("Can't run forever with block=True")

            inside_speed = (arc_radius - Mover.CHASSIS_RADIUS) / (arc_radius + Mover.CHASSIS_RADIUS) * speed

            if clockwise:
                if backwards:
                    self._mover.on(-inside_speed, -speed)
                else:
                    self._mover.on(speed, inside_speed)
            else:
                if backwards:
                    self._mover.on(-speed, -inside_speed)
                else:
                    self._mover.on(inside_speed, speed)
        else:
            if degrees <= 0:
                raise ValueError(
                    "Can't rotate a negative number of degrees. Use clockwise=False to turn counter-clockwise")

            degrees_in_rad = Mover._convert_deg_to_rad(degrees)
            inside_distance = (arc_radius - Mover.CHASSIS_RADIUS) * degrees_in_rad
            outside_distance = (arc_radius + Mover.CHASSIS_RADIUS) * degrees_in_rad

            movement_time = outside_distance / speed
            inside_speed = inside_distance / movement_time
            outside_degrees = Mover._convert_rad_to_deg(Mover._convert_distance_to_rad(outside_distance))

            if clockwise:
                if backwards:
                    self._mover.on_for_degrees(-inside_speed, -speed, outside_degrees, block=block)
                else:
                    self._mover.on_for_degrees(speed, inside_speed, outside_degrees, block=block)
            else:
                if backwards:
                    self._mover.on_for_degrees(-speed, -inside_speed, outside_degrees, block=block)
                else:
                    self._mover.on_for_degrees(inside_speed, speed, outside_degrees, block=block)

            if block:
                time.sleep(0.1)

    def steer(self, steering, speed=_DEFAULT_SPEED):
        """Make the robot move in a direction. -100 is to the left. +100 is to the right. 0 is straight"""

        # Modified code from ev3dev2.robot.MoveSteering

        if steering < -100 or steering > 100:
            raise ValueError("Steering, must be between -100 and 100 (inclusive)")

        inside_speed = speed - speed * abs(steering) / 50

        if steering >= 0:
            self._mover.on(speed, inside_speed)
        else:
            self._mover.on(inside_speed, speed)

    def stop(self):
        """Make robot stop"""
        self._mover.off()
        time.sleep(0.1)
        

    @staticmethod
    def _convert_distance_to_rad(distance):
        return distance / Mover._WHEEL_RADIUS

    @staticmethod
    def _convert_deg_to_rad(deg):
        return deg * math.pi / 180

    @staticmethod
    def _convert_rad_to_deg(rad):
        return rad / math.pi * 180

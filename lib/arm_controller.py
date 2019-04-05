from ev3dev2.motor import SpeedPercent, LargeMotor
from constants import DEG_DEVICE, DEG_FIBRE_OPTIC, ARM_MOTOR_PORT


class ArmController:
    '''class to control arm of robot'''

    def __init__(self):
        self.arm = LargeMotor(ARM_MOTOR_PORT)
        self.arm_current_position = 0

    def get_arm_position(self):
        '''Gets current position of claw'''
        return self.arm_current_position

    def raise_arm(self, speed=-30, block=True):
        '''Resets arm to raised position'''
        if self.arm_current_position != 0:
            self.arm.on_for_seconds(SpeedPercent(speed), 2, block=block)

        self.arm_current_position = 0

    def run_arm_to_device(self, speed=30, block=True):
        '''Lowers arm the degrees to pick up device'''
        if self.arm_current_position == 0:
            self.arm.on_for_degrees(SpeedPercent(speed), DEG_DEVICE, block=block)

        self.arm_current_position = 1

    def run_arm_to_fibre_optic(self, speed=30, block=True):
        """ Lowers arm the degrees to pick up fibre optic cable"""
        if self.arm_current_position == 0:
            self.arm.on_for_degrees(SpeedPercent(speed), DEG_FIBRE_OPTIC, block=block)

        self.arm_current_position = 2


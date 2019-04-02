from ev3dev2.motor import SpeedPercent, LargeMotor
from constants import deg_device, deg_fibre_optic

class ClawController:

    '''class to control claw of robot'''

    def __init__(self,port,position):
        self.claw = LargeMotor(port)
        self.claw_current_position = position

    def get_position(self):
        '''Gets current position of claw'''
        return self.claw_current_position

    def raised_position(self):
        '''Resets claw to raised position'''
        if self.claw_current_position != 0:
            self.claw.on_for_seconds(SpeedPercent(-50),2)

        self.claw_current_position = 0

    def device_position(self):
        '''Lowers claw the degrees to pick up device'''
        if self.claw_current_position == 0:
            self.claw.on_for_degrees(SpeedPercent(25),deg_device)

        self.claw_current_position = 1

    def fibre_optic_position(self):
        """ Lowers claw the degrees to pick up fibre optic cable"""
        if self.claw_current_position == 0:
            self.claw.on_for_degrees(SpeedPercent(25), deg_fibre_optic)

        self.claw_current_position = 2


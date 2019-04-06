from ev3dev2.motor import SpeedPercent, LargeMotor
from lib.constants import ARM_MOTOR_PORT


class ArmController:
    """class to control arm of robot"""

    # Degrees predictions for arm
    _DEG_FIBRE_OPTIC = 135
    _DEG_DEVICE = 90
    _SECONDS_TO_RESET = 1

    def __init__(self):
        self._arm = LargeMotor(ARM_MOTOR_PORT)
        self._arm_is_raised = False

    def raise_arm(self, speed=30, block=True):
        """Resets arm to raised position"""
        if not self._arm_is_raised:
            self._arm.on_for_seconds(SpeedPercent(speed * -1), self._SECONDS_TO_RESET, block=block)
            if self._arm.is_stalled:  # TODO : Test
                self._arm.stop()

            self._arm_is_raised = True

    def run_arm_to_device(self, speed=30, block=True):
        """Lowers arm the degrees to pick up device"""
        if self._arm_is_raised:
            self._arm.on_for_degrees(SpeedPercent(speed), self._DEG_DEVICE, block=block)

            self._arm_is_raised = False

    def run_arm_to_fibre_optic(self, speed=30, block=True):
        """Lowers arm the degrees to pick up fibre optic cable"""

        if self._arm_is_raised:
            self._arm.on_for_degrees(SpeedPercent(speed), self._DEG_FIBRE_OPTIC, block=block)

            self._arm_is_raised = False

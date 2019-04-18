import lib.motors
import lib.sensors
import lib.constants
import ev3dev2.sound


class Robot:
    def __init__(self):
        self.mover = lib.motors.Mover()
        self.left_color_sensor = lib.sensors.ColorSensor(lib.constants.LEFT_COLOR_SENSOR)
        self.right_color_sensor = lib.sensors.ColorSensor(lib.constants.RIGHT_COLOR_SENSOR)
        self.swivel = lib.motors.SwivelController()
        self.arm = lib.motors.ArmController()

    def tear_down(self):
        self.mover.stop()
        self.swivel.point_backwards()
        self.arm.lower_to_fibre_optic()

    @classmethod
    def beep(cls):
        ev3dev2.sound.Sound().beep(play_type=ev3dev2.sound.Sound.PLAY_NO_WAIT_FOR_COMPLETE)

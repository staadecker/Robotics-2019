from lib.movement_controller import MovementController
from lib.color_sensor import ColorSensor
from lib.line_follower import LineFollower, StopAtCrossLine
from lib import constants
from ev3dev2.button import Button

DEBUGGING = True


class Robot:
    def __init__(self):
        self.movement_controller = MovementController()
        self.left_color_sensor = ColorSensor(constants.LEFT_LINE_COLOR_SENSOR)
        self.right_color_sensor = ColorSensor(constants.RIGHT_LINE_COLOR_SENSOR)


class Main:
    def __init__(self):
        self.robot = Robot()

        self.line_follower = LineFollower(self.robot.movement_controller, self.robot.left_color_sensor,
                                          self.robot.right_color_sensor)

    def run(self):
        self.robot.movement_controller.travel(10)
        self.line_follower.follow_on_right(StopAtCrossLine(self.robot.left_color_sensor),
                                           callback=self.read_info_blocks_callback)
        self.robot.movement_controller.rotate(90)
        pass

    def read_info_blocks_callback(self):
        pass  # TODO

    @staticmethod
    def wait_for_button_press():
        Button.wait_for_released('enter')


if __name__ == '__main__':
    main = Main()
    if not DEBUGGING:
        main.wait_for_button_press()
    main.run()

import ev3dev2.sensor.lego as lego_sensor


class ColorSensor:
    """Represents a color sensor"""

    BLACK = lego_sensor.ColorSensor.COLOR_BLACK
    WHITE = lego_sensor.ColorSensor.COLOR_WHITE
    GREEN = lego_sensor.ColorSensor.COLOR_GREEN
    BLUE = lego_sensor.ColorSensor.COLOR_BLUE
    RED = lego_sensor.ColorSensor.COLOR_RED
    YELLOW = lego_sensor.ColorSensor.COLOR_YELLOW
    NO_COLOR = lego_sensor.ColorSensor.COLOR_NOCOLOR
    BROWN = lego_sensor.ColorSensor.COLOR_BROWN

    def __init__(self, port):
        self.sensor = lego_sensor.ColorSensor(port)

    def get_color(self):
        """Returns the color under the sensor"""
        return self.sensor.color

    def get_reflected(self):
        """Returns the amount of light reflected (percentage)"""
        return self.sensor.reflected_light_intensity

import ev3dev2.sensor.lego as lego_sensor

BLACK = lego_sensor.ColorSensor.COLOR_BLACK
WHITE = lego_sensor.ColorSensor.COLOR_WHITE
GREEN = lego_sensor.ColorSensor.COLOR_GREEN
BLUE = lego_sensor.ColorSensor.COLOR_BLUE
RED = lego_sensor.ColorSensor.COLOR_RED
YELLOW = lego_sensor.ColorSensor.COLOR_YELLOW
NO_COLOR = lego_sensor.ColorSensor.COLOR_NOCOLOR
BROWN = lego_sensor.ColorSensor.COLOR_BROWN
UNKNOWN = -1


class ColorSensor:
    def get_color(self) -> int:
        print("ERROR: Not implemented")
        return UNKNOWN


class HiTechnicSensor(ColorSensor):
    """Represents a color sensor"""

    def __init__(self, port):
        self.sensor = lego_sensor.Sensor(address=port)
        self.sensor.mode = "COLOR"

    def get_color(self):
        """Returns the color under the sensor"""
        # self.sensor._ensure_mode("COLOR")
        return HiTechnicSensor.convert_code_to_color(self.sensor.value())

    @staticmethod
    def convert_code_to_color(code):
        if code == 0:
            return BLACK
        elif code == 17:
            return WHITE
        elif code == 2:
            return BLUE
        elif code == 4:
            return GREEN
        elif code == 6:
            return YELLOW
        elif code == 8:
            return RED
        else:
            print("ERROR: Got color code %s and don't know its color" % code)
            return UNKNOWN


class EV3ColorSensor(ColorSensor):
    """Represents an ev3 color sensor"""

    def __init__(self, port):
        self.sensor = lego_sensor.ColorSensor(port)

    def get_color(self):
        """Returns the color under the sensor"""
        return self.sensor.color

    def get_reflected(self):
        """Returns the amount of light reflected (percentage)"""
        return self.sensor.reflected_light_intensity

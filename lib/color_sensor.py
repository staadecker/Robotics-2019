from ev3dev2.sensor.lego import ColorSensor


class EV3ColorSensor:
    """A class for a color sensor"""

    def __init__(self, port):
        """
        Method that gets the color under the sensor

        Returns:
            A number representing the color
        """
        self.color_sensor = ColorSensor(port)
        self.color_sensor.mode = ColorSensor.MODE_COL_COLOR

    def get_color(self):
        return self.color_sensor.value(1)

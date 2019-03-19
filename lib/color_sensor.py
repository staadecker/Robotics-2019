from ev3dev2.sensor.lego import ColorSensor


class ColorSensorWrapper:
    """Represents a color sensor"""

    def __init__(self, port):
        self.sensor = ColorSensor(port)

        self.mode = self.sensor.mode # Used to save time so not to call the get method each time

    def get_color(self):
        """Returns the color under the sensor"""
        if self.mode != ColorSensor.MODE_COL_COLOR:
            self.sensor.mode = ColorSensor.MODE_COL_COLOR
            self.mode = ColorSensor.MODE_COL_COLOR

        return self.sensor.value(1)

    def get_reflected(self):
        """Returns the amount of light reflected (percentage)"""
        if self.mode != ColorSensor.MODE_COL_REFLECT:
            self.sensor.mode = ColorSensor.MODE_COL_REFLECT
            self.mode = ColorSensor.MODE_COL_REFLECT

        return self.sensor.value(1)

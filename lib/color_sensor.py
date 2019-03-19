import abc
from ev3dev2.sensor.lego import ColorSensor


class BaseColorSensor(abc.ABC):
    """Interface for a color sensor"""

    @abc.abstractmethod
    def get_color(self):
        """
        Method that gets the color under the sensor

        Returns:
            A number representing the color
        """
        pass


# TODO : Test
class EV3ColorSensor(BaseColorSensor):
    def __init__(self, port):
        self.color_sensor = ColorSensor(port)
        self.color_sensor.mode = ColorSensor.MODE_COL_COLOR

    def get_color(self):
        return self.color_sensor.value(1)

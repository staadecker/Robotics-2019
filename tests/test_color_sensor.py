import unittest
import util
import color_sensor
import constants
from ev3dev2.sensor.lego import ColorSensor


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestEV3ColorSensor(unittest.TestCase):
    def setUp(self):
        self.color_sensor = color_sensor.ColorSensorWrapper(constants.LEFT_LINE_COLOR_SENSOR)

    def test_color(self):
        input("Place the left line color sensor on a black line then press enter.")
        self.assertEqual(self.color_sensor.get_color(), ColorSensor.COLOR_BLACK)

    def test_reflection_mode(self):
        result = self.color_sensor.get_reflected()
        self.assertTrue(util.get_user_answer(f"Reflection percentage is: {result}. Does this make sense?"))


if __name__ == '__main__':
    unittest.main()

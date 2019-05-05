import unittest
from tests import util
from lib.sensors import ColorSensor
from lib import ports


@unittest.skipUnless(util.is_running_on_ev3(), "Requires EV3")
class TestEV3ColorSensor(unittest.TestCase):
    def setUp(self):
        self.color_sensor = ColorSensor(ports.LEFT_COLOR_SENSOR)

    def test_color(self):
        input("Place the left line color sensor on a black line then press enter.")
        self.assertEqual(self.color_sensor.get_color(), ColorSensor.BLACK)

        input("Place the left line color sensor on a white area then press enter.")
        self.assertEqual(self.color_sensor.get_color(), ColorSensor.WHITE)

    def test_reflection_mode(self):
        result = self.color_sensor.get_reflected()
        self.assertTrue(util.get_user_answer("Reflection percentage is: " + str(result) + ". Does this make sense?"))


if __name__ == '__main__':
    unittest.main()

import lib.up_motors as motors
import lib.up_sensors as sensors
import lib.up_ports as ports

MOVER = motors.Mover(reverse_motors=True)
LEFT_SENSOR = sensors.EV3ColorSensor(ports.LEFT_SENSOR)
RIGHT_SENSOR = sensors.HiTechnicSensor(ports.RIGHT_SENSOR)
FRONT_SENSOR = sensors.EV3ColorSensor(ports.FRONT_SENSOR)
BACK_SENSOR = sensors.EV3ColorSensor(ports.BACK_SENSOR)

SWIVEL = motors.Swivel()
LIFT = motors.Lift()



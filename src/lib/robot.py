import lib.up_line_follower as line_follower
import lib.up_motors as motors
import lib.up_sensors as sensors
import lib.up_ports as ports

MOVER = motors.Mover(reverse_motors=False)
LEFT_SENSOR = sensors.EV3ColorSensor(ports.LEFT_SENSOR)
RIGHT_SENSOR = sensors.HiTechnicSensor(ports.RIGHT_SENSOR)
FRONT_SENSOR = sensors.EV3ColorSensor(ports.FRONT_SENSOR)
BACK_SENSOR = sensors.EV3ColorSensor(ports.BACK_SENSOR)

SWIVEL = motors.Swivel()
LIFT = motors.Lift()

LINE_FOLLOWER = line_follower.LineFollower(MOVER, FRONT_SENSOR, BACK_SENSOR)

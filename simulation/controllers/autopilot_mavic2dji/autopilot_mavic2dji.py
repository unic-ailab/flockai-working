from flockai.webots_controllers.mavic2dji import AutopilotMavic2DJI
from flockai.models.devices.device_enums import EnableableDevice, NonEnableableDevice, MotorDevice, AircraftAxis, \
    Relative2DPosition

enableable_devices = [

    (EnableableDevice.RECEIVER, "receiver"),
    (EnableableDevice.CAMERA, "camera"),
    (EnableableDevice.KEYBOARD, None),
    (EnableableDevice.BATTERY_SENSOR, None),
    (EnableableDevice.INERTIAL_UNIT, "inertial unit"),
    (EnableableDevice.GPS, "gps"),
    (EnableableDevice.COMPASS, "compass"),
    (EnableableDevice.GYRO, "gyro")
]

non_enableable_devices = [
    # (NonEnableableDevice.EMITTER, "emitter"),
    # (NonEnableableDevice.LED, "front left led"),
    # (NonEnableableDevice.LED, "front right led"),
]

motor_devices = [
    (MotorDevice.CAMERA, "camera roll", AircraftAxis.ROLL),
    (MotorDevice.CAMERA, "camera pitch", AircraftAxis.PITCH),
    (MotorDevice.CAMERA, "camera yaw", AircraftAxis.YAW),
    (MotorDevice.PROPELLER, "front left propeller", Relative2DPosition(1, -1)),
    (MotorDevice.PROPELLER, "front right propeller", Relative2DPosition(1, 1)),
    (MotorDevice.PROPELLER, "rear left propeller", Relative2DPosition(-1, -1)),
    (MotorDevice.PROPELLER, "rear right propeller", Relative2DPosition(-1, 1)),
]

# Create drone instance and run its controller
controller = AutopilotMavic2DJI(enableable_devices, non_enableable_devices, motor_devices)
controller.run()

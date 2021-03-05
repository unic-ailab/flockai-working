import pickle

from flockai.PyCatascopia.Metrics import *
from flockai.models.probes.flockai_probe import FlockAIProbe, ProcessCpuUtilizationMetric, ProcessCpuTimeMetric, ProcessIOTimeMetric, \
    ProcessAliveTimeMetric, ProbeAliveTimeMetric, ProcessMemoryMetric
from flockai.webots_controllers.mavic2dji import KeyboardMavic2DJI
from flockai.models.devices.device_enums import EnableableDevice, NonEnableableDevice, MotorDevice, AircraftAxis, \
    Relative2DPosition, Devices



"""""""""""""""""""""
DECLARE DEVICES HERE
"""""""""""""""""""""
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
    (NonEnableableDevice.EMITTER, "emitter"),
    (NonEnableableDevice.LED, "front left led"),
    (NonEnableableDevice.LED, "front right led"),
]

"""""""""""""""""""""
DECLARE MOTORS HERE
"""""""""""""""""""""
motor_devices = [
    (MotorDevice.CAMERA, "camera roll", AircraftAxis.ROLL),
    (MotorDevice.CAMERA, "camera pitch", AircraftAxis.PITCH),
    (MotorDevice.CAMERA, "camera yaw", AircraftAxis.YAW),
    (MotorDevice.PROPELLER, "front left propeller", Relative2DPosition(1, -1)),
    (MotorDevice.PROPELLER, "front right propeller", Relative2DPosition(1, 1)),
    (MotorDevice.PROPELLER, "rear left propeller", Relative2DPosition(-1, -1)),
    (MotorDevice.PROPELLER, "rear right propeller", Relative2DPosition(-1, 1)),
]

devices = Devices(enableable_devices, non_enableable_devices, motor_devices)

"""""""""""""""""""""""""""
CREATE MONITORING PROBES
"""""""""""""""""""""""""""
# 1. Create a probe interface where the use defines what metrics he wants to use
# 2. Based on the probes that the user wants to use flockai should behave accordingly

metrics = [
    ProcessCpuUtilizationMetric(name='cpu_pct', units='%', desc='process-level cpu utilization', minVal=0, higherIsBetter=False),
    ProcessCpuTimeMetric('cpu_time', 's', 'process-level cpu time', minVal=0, higherIsBetter=False),
    ProcessIOTimeMetric('io_time', 's', 'process-level io time (linux-only)', minVal=0, higherIsBetter=False),
    ProcessAliveTimeMetric('alive_time', 's', 'time process is alive', minVal=0, higherIsBetter=False),
    ProbeAliveTimeMetric('probe_alive_time', 's', 'time probe is alive', minVal=0, higherIsBetter=False),
    ProcessMemoryMetric('mem_pct', '%', 'process-level memory utilization', minVal=0, higherIsBetter=False),
]
probe = FlockAIProbe(metrics, name='Example Probe', periodicity=5)

"""""""""""""""""""""""""""""""""""""""""""""""""""
LOAD A MACHINE LEARNING MODEL AND SET THE INPUTS
"""""""""""""""""""""""""""""""""""""""""""""""""""
# 1. Create a model interface where the user defines the model:
#   a. filename
#   b. library functions to load and predict
#   c. input vector sizes and which data
filename = 'LinReg_model.sav'
model = pickle.load(open(filename, 'rb'))

"""""""""""""""""""""""""""""
START AND RUN THE CONTROLLER
"""""""""""""""""""""""""""""
controller = KeyboardMavic2DJI(devices=devices, probe=probe, model=model)

controller.run()

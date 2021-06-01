import pickle
from PIL import Image
import numpy as np
from flockai.interfaces.flockai_ml import FlockAIClassifier
from flockai.models.probes.flockai_probe import FlockAIProbe, ProcessCpuUtilizationMetric, ProcessCpuTimeMetric, ProcessIOTimeMetric, \
    ProcessAliveTimeMetric, ProbeAliveTimeMetric, ProcessMemoryMetric
from flockai.models.sensors.humidity import HumiditySensor
from flockai.models.sensors.temperature import TemperatureSensor
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
    (NonEnableableDevice.DISTANCE_SENSOR, "ds0")
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

"""""""""""""""""""""""""""""
INITIALIZE THE CONTROLLER
"""""""""""""""""""""""""""""
controller = KeyboardMavic2DJI(devices=devices, probe=probe)


class LinearRegressionClassifier(FlockAIClassifier):
    """
    IMPLEMENT A FLOCKAI CLASSIFIER
    """
    def __init__(self):
        super().__init__()
        self.periodicity = 5
        self.onboard = True
        self._load_model()

    """ IMPLEMENT ABSTRACT METHODS"""
    def _load_model(self):
        filename = 'LinReg_model.sav'
        self.model = pickle.load(open(filename, 'rb'))
        self.temperature_sensor = TemperatureSensor('data/temperature_data.txt')
        self.humidity_sensor = HumiditySensor('data/humidity_data.txt')

    def _get_model_input(self):
        humidity_max, humidity_min, humidity_avg = self.humidity_sensor.get_values()
        temperature_max, temperature_min, temperature_avg = self.temperature_sensor.get_values()
        return [humidity_max, humidity_min, humidity_avg], [temperature_max, temperature_min, temperature_avg]

    def predict(self):
        if controller.getTime() % self.periodicity != 0.0:  # get access to controller functions
            return None

        humidity_data, temperature_data = self._get_model_input()
        input_vector = np.array([[temperature_data[0]], [temperature_data[1]], [temperature_data[2]],
                                 [humidity_data[0]], [humidity_data[1]], [humidity_data[2]]]).reshape(1, -1)

        return self.model.predict(input_vector)

    """ IMPLEMENT CUSTOM METHODS """
    # def foo(self):
    #     pass

"""""""""""""""""""""""""""""""""""""""""""""
SET THE ML MODEL ON THE CONTROLLER AND RUN IT
"""""""""""""""""""""""""""""""""""""""""""""
controller.model = LinearRegressionClassifier()
controller.run()

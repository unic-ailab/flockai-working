import abc
import pickle

from PIL import Image
import numpy as np
from dlib import cnn_face_detection_model_v1

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

"""""""""""""""""""""""""""""""""""""""""""""""""""
LOAD A MACHINE LEARNING MODEL AND SET THE INPUTS
"""""""""""""""""""""""""""""""""""""""""""""""""""
# 1. Create a model interface where the user defines the model:
#   a. filename
#   b. library functions to load and predict
#   c. input vector sizes and which data
# filename = 'LinReg_model.sav'
# filename = 'cnnFaceRecognition.bin'
# model = pickle.load(open(filename, 'rb'))


class FlockAIClassifier(abc.ABC):
    def __init__(self):
        self.model = None

    @abc.abstractmethod
    def load_model(self):
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def set_input(self):
        raise NotImplementedError


class FaceDetectionClassifier(FlockAIClassifier):
    def load_model(self):
        filename = 'cnnFaceRecognition.bin'
        self.model = pickle.load(open(filename, 'rb'))
        self.cnn_face_detector = cnn_face_detection_model_v1(self.model)

    def predict(self, image_filename):
        image = self._load_image_file(image_filename)
        print([self._trim_css_to_bounds(self._rect_to_css(face.rect), image.shape) for face in self.cnn_face_detector(image, 1)])

    def set_input(self):
        pass

    def _trim_css_to_bounds(self, css, image_shape):
        return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

    def _rect_to_css(self, rect):
        return rect.top(), rect.right(), rect.bottom(), rect.left()

    def _load_image_file(self, file, mode='RGB'):
        im = Image.open(file)
        if mode:
            im = im.convert(mode)
        return np.array(im)


model = FaceDetectionClassifier()
model.load_model()
"""""""""""""""""""""""""""""
START AND RUN THE CONTROLLER
"""""""""""""""""""""""""""""
controller = KeyboardMavic2DJI(devices=devices, probe=probe, model=model)

controller.run()

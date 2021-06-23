import pickle
from PIL import Image
import numpy as np
from dlib import cnn_face_detection_model_v1

from controller import Camera
from flockai.PyCatascopia.Metrics import *
from flockai.interfaces.flockai_ml import FlockAIClassifier
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
metrics = [
    ProcessCpuUtilizationMetric(name='cpu_pct', units='%', desc='process-level cpu utilization', minVal=0, higherIsBetter=False),
    ProcessCpuTimeMetric('cpu_time', 's', 'process-level cpu time', minVal=0, higherIsBetter=False),
    ProcessIOTimeMetric('io_time', 's', 'process-level io time (linux-only)', minVal=0, higherIsBetter=False),
    ProcessAliveTimeMetric('alive_time', 's', 'time process is alive', minVal=0, higherIsBetter=False),
    ProbeAliveTimeMetric('probe_alive_time', 's', 'time probe is alive', minVal=0, higherIsBetter=False),
    ProcessMemoryMetric('mem_pct', '%', 'process-level memory utilization', minVal=0, higherIsBetter=False),
]
probe = FlockAIProbe(metrics, name='Example Probe', periodicity=1)

"""""""""""""""""""""""""""""
INITIALIZE THE CONTROLLER
"""""""""""""""""""""""""""""
controller = KeyboardMavic2DJI(devices=devices, probe=probe)

"""""""""""""""""""""""""""""""""""
IMPLEMENT THE FLOCKAI CLASSIFIER
"""""""""""""""""""""""""""""""""""
class FaceDetectionClassifier(FlockAIClassifier):
    def __init__(self):
        super().__init__()
        # REQUIRED ATTRIBUTES
        self.periodicity = 5  # defines the periodicity of the prediction
        self.onboard = True  # defines if the classifier is run on the drone, if False, the drone transmits the input data via its emitter device
        self._load_model()

    """ IMPLEMENT ABSTRACT METHODS"""
    def _load_model(self):
        """
        Custom method that implements the way a model is loaded
        :return:
        """
        filename = 'cnnFaceRecognition.bin'
        self.model = pickle.load(open(filename, 'rb'))
        self.cnn_face_detector = cnn_face_detection_model_v1(self.model)

    def _get_model_input(self):
        """
        Custom method that access the camera on the controller and captures images
        :return:
        """
        filename = f'logs/Images/image_{str(int(time.time()))}.jpg'
        camera: Camera = controller.devices['camera']['device']  # get access to controller devices
        camera.saveImage(filename, 20)
        return filename

    def predict(self):
        """
        Main pipeline method used by FlockAI during the simulation to make predictions
        :return:
        """
        if controller.getTime() % self.periodicity != 0.0:  # get access to controller functions
            return None

        image_filename = self._get_model_input()
        # return image_filename
        image = self._load_image_file(image_filename)
        return [self._trim_css_to_bounds(self._rect_to_css(face.rect), image.shape) for face in self.cnn_face_detector(image, 1)]

    """ IMPLEMENT CUSTOM METHODS """
    def _get_foo_unused_input(self):
        """
        Unused method showcasing a different input method that the user needs
        :return:
        """
        camera: Camera = controller.devices['camera']['device']
        image = camera.getImage()
        width = camera.getWidth()
        height = camera.getHeight()

        image_vector = [[[camera.imageGetRed(image, width, x, y),
                         camera.imageGetGreen(image, width, x, y),
                         camera.imageGetBlue(image, width, x, y)] for y in range(height)] for x in range(width)]
        return image_vector

    def _trim_css_to_bounds(self, css, image_shape):
        return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

    def _rect_to_css(self, rect):
        return rect.top(), rect.right(), rect.bottom(), rect.left()

    def _load_image_file(self, file, mode='RGB'):
        im = Image.open(file)
        if mode:
            im = im.convert(mode)
        return np.array(im)


"""""""""""""""""""""""""""""""""""""""""""""
SET THE ML MODEL ON THE CONTROLLER AND RUN IT
"""""""""""""""""""""""""""""""""""""""""""""
controller.model = FaceDetectionClassifier()
controller.run()

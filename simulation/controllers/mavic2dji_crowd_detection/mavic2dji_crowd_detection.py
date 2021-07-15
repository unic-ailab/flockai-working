import numpy as np
import tensorflow as tf
import cv2
import PIL.Image
import pickle
import time
from os import listdir
from os.path import isfile, join
import datetime
from os import listdir
from os.path import isfile, join
import datetime

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


class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        end_time = time.time()

        print("Elapsed Time:", end_time-start_time)

        im_height, im_width, _ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0, i, 0] * im_height),
                             int(boxes[0, i, 1] * im_width),
                             int(boxes[0, i, 2] * im_height),
                             int(boxes[0, i, 3] * im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()


"""""""""""""""""""""""""""""""""""
IMPLEMENT THE FLOCKAI CLASSIFIER
"""""""""""""""""""""""""""""""""""


class CrowdDetectionClassifier(FlockAIClassifier):
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
        filename = 'frozen_inference_graph.pb'
        self.odapi = DetectorAPI(path_to_ckpt=filename)
        self.threshold = 0.5
        dataset_path = 'crowd_images'
        self.image_blobs = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]
        self.size = 1500, 1500

        self.entry = 0

    def _get_model_input(self):
        """
        Custom method that access the camera on the controller and captures images
        :return:
        """
        blob_file = self.image_blobs[self.entry]
        self.entry = (self.entry + 1) % len(self.image_blobs)

        img = cv2.imread('crowd_images/' + blob_file)
        img = cv2.resize(img, (480, 480))

        return img

    def predict(self):
        """
        Main pipeline method used by FlockAI during the simulation to make predictions
        :return:
        """
        if controller.getTime() % self.periodicity != 0.0:  # get access to controller functions
            return None

        img = self._get_model_input()

        boxes, scores, classes, num = self.odapi.processFrame(img)

        count = 0
        for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > self.threshold:
                box = boxes[i]
                cv2.rectangle(img, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
                cv2.putText(img, "person", (box[1] - 10, box[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                count = count + 1

        return [count]


"""""""""""""""""""""""""""""""""""""""""""""
SET THE ML MODEL ON THE CONTROLLER AND RUN IT
"""""""""""""""""""""""""""""""""""""""""""""
controller.model = CrowdDetectionClassifier()
controller.run()

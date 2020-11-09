import enum
import threading
import random
import string
import yaml
import os
from flockai.singleton import Singleton


class IntensityLevel(enum.IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class IntensiveThread(threading.Thread):

    numbers = {
        IntensityLevel.LOW: 1000,
        IntensityLevel.NORMAL: 1000000,
        IntensityLevel.HIGH: 1000000000
    }

    def __init__(self, test_id):
        super().__init__()
        self.intensity = IntensityLevel(test_id).name
        self.number = self.numbers[test_id]

    def run(self):
        """
        Runs an intensive task based on the intensity level
        :return:
        """
        #changed
        #print(f"Doing a {self.intensity} intensive task. ID: {self.native_id}")

        for i in range(self.number):
            continue

        # print("Done doing some intensive task")


class StringGenerator:
    @staticmethod
    def get_random_message(length: int) -> str:
        """
        Returns a random message based on the length requested
        :param length: The length of the random message
        :return:
        """
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


class Graphics:
    @staticmethod
    def clamp(value, low, high):
        """
        Clamping is the process of limiting a position to an area. Unlike wrapping,
        clamping merely moves the point to the nearest available value.
        :param value: The value to be clamped
        :param low: The lower bound
        :param high: The upper bound
        :return: number
        """
        return low if value < low else high if value > high else value


class SimulationConfig(metaclass=Singleton):

    def __init__(self):
        import simulation
        path = os.path.abspath(simulation.__file__)
        self.config_file = path
        self.data = None
        self.simulation_enabled = False
        self._read_config()
        self._update_config()

    def _read_config(self):
        stream = open(self.config_file, 'r')
        self.data = yaml.safe_load(stream)

        self.simulation_id = self.data['simulation_id']
        self.simulation_image_directory = f"{self.data['image_directory']}{str(self.simulation_id)}/"

    def _update_config(self):
        self.data['simulation_id'] = self.simulation_id + 1
        with open(self.config_file, 'w') as f:
            f.write(yaml.dump(self.data, default_flow_style=False))

    def create_simulation_image_directory(self) -> str:
        try:
            os.makedirs(self.simulation_image_directory)
        except OSError:
            print("Creation of directory failed")

    def get_simulation_id(self):
        return self.simulation_id

    def get_simulation_image_directory(self) -> str:
        return self.simulation_image_directory

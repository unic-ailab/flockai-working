import os
import yaml

import simulation
from flockai.patterns.singleton import Singleton


class SimulationConfig(metaclass=Singleton):

    def __init__(self):
        self.config_file = os.path.abspath(simulation.__file__)
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

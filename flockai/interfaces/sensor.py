import abc
from pathlib import Path


class ISensor(metaclass=abc.ABCMeta):
    def __init__(self, file):
        self._set_data_file(file)
        self.data_entry = 0

    def _get_data(self):
        entry = self.data[self.data_entry % len(self.data)]

        self.data_entry += 1
        return entry

    @abc.abstractmethod
    def get_values(self):
        raise NotImplementedError

    def _set_data_file(self, file):
        with open(file, 'r') as f:
            self.data = [line[:-1] for line in f.readlines()]



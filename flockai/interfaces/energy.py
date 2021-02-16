import abc


class IEnergy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def calculate(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, *args, **kwargs):
        raise NotImplementedError

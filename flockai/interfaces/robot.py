import abc
from controller import Robot


class IRobot(Robot, abc.ABC):
    """
    Inherit functionalities provided by the Webots Robot library and declare abstract methods
    """
    def __init__(self):
        super(IRobot, self).__init__()

    @abc.abstractmethod
    def _attach_and_enable_devices(self, en_devices, nen_devices):
        """
        Attach and enable the devices on a drone
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _attach_and_enable_motors(self, motor_devices):
        """
        Attach and enable the motors on a drone
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _set_variables(self):
        """
        Set variables needed for controlling the drone on air
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _set_constants(self):
        """
        Set constants needed for controlling the drone on air
        :return:
        """
        raise NotImplementedError

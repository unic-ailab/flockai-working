from flockai.interfaces.robot import IRobot
from flockai.models.devices.device_enums import EnableableDevice


class IBaseStation(IRobot):

    def __init__(self, devices):
        super().__init__()
        self.name = self.getName()
        self.basic_time_step = int(self.getBasicTimeStep())
        self.devices = self._attach_and_enable_devices(devices.enableable_devices, devices.non_enableable_devices)

    def _attach_and_enable_devices(self, en_devices, nen_devices):
        """
        Define all the required devices and enable them
        :return:
        """
        e_devices = {}
        if en_devices is not None:
            for device, name in en_devices:
                if EnableableDevice(device) == EnableableDevice.KEYBOARD:
                    e_devices['keyboard'] = {'type': device, 'device': self.keyboard}
                    e_devices['keyboard']['device'].enable(self.basic_time_step)
                elif EnableableDevice(device) == EnableableDevice.BATTERY_SENSOR:
                    self.batterySensorEnable(self.basic_time_step)
                elif name is not None:
                    e_devices[name] = {'type': device, 'device': self.getDevice(name)}
                    e_devices[name]['device'].enable(self.basic_time_step)

        ne_devices = {}
        if nen_devices is not None:
            for device, name in nen_devices:
                if name is not None:
                    ne_devices[name] = {'type': device, 'device': self.getDevice(name)}

        return {**e_devices, **ne_devices}

    def _attach_and_enable_motors(self, motor_devices):
        pass

    def _set_variables(self):
        pass

    def _set_constants(self):
        pass
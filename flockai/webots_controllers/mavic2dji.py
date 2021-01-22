from flockai.models.drones.autopilot_controlled_drone import AutopilotControlledDrone
from flockai.models.drones.keyboard_controller_drone import KeyboardControlledDrone
from flockai.utils.string_generator import StringGenerator
from flockai.models.devices.device_enums import EnableableDevice, NonEnableableDevice, MotorDevice
from flockai.utils.intensive_thread import IntensiveThread

class KeyboardMavic2DJI(KeyboardControlledDrone):
    """
    A Keyboard Controlled Mavic2DJI
    """

    def __init__(self, devices, probes=None):
        super().__init__(devices)
        self.probes = probes

    def _activate_probes(self):
        if self.probes:
            for probe in self.probes:
                probe.activate()

    def send_msg(self, msg, emitter_devices: list):
        """
        Sends a message from the attached emitter device
        :param emitter_devices: The emitter devices to send the message
        :param msg: The message to send
        :return: None
        """
        for emitter in emitter_devices:
            if emitter not in self.devices:
                print(f"The specified emitter device is not found: {emitter}")
                return
            f_emitter = self.devices[emitter]['device']
            f_emitter.send(msg.encode('utf-8'))

    def receive_msgs(self, receiver_devices: list):
        """
        Receive messages on the receiver device
        :param receiver_devices: The receiver device name as a string
        :return: None
        """
        for receiver in receiver_devices:
            if receiver not in self.devices:
                print(f"The specified receiver device is not found: {receiver}")
                return

            f_receiver = self.devices[receiver]['device']
            while f_receiver.getQueueLength() > 0:
                message_received = f_receiver.getData().decode('utf-8')
                f_receiver.nextPacket()
                yield message_received

    def blink_led_lights(self, led_devices: list):
        """
        Blink led lights every 2 seconds
        :param time: The simulation time. ie self.getTime()
        :return:
        """
        f_led_devices = [self.devices[led]['device'] for led in led_devices]
        led_on = (self.getTime() // 1) % 2 == 1

        for f_led in f_led_devices:
            f_led.set(led_on)
            led_on = not led_on

    def run(self):
        # Wait a second before starting
        while self.step(self.basic_time_step) != -1:
            if self.getTime() > 1:
                break

        led_devices = []
        emitter_devices = []
        receiver_devices = []
        for device_name in self.devices:
            if self.devices[device_name]['type'] == NonEnableableDevice.LED:
                led_devices.append(device_name)
            if self.devices[device_name]['type'] == NonEnableableDevice.EMITTER:
                emitter_devices.append(device_name)
            if self.devices[device_name]['type'] == EnableableDevice.RECEIVER:
                receiver_devices.append(device_name)

        self._activate_probes()

        while self.step(self.basic_time_step) != -1:
            # Blink lights
            self.blink_led_lights(led_devices)
            # Fly drone
            self.actuate()

            # Get battery data
            # print(self.batterySensorGetValue())

            # Do an intensive task
            t = IntensiveThread()
            t.run()

            # Send messages
            self.send_msg(StringGenerator.get_random_message(4), emitter_devices)

            # Receive messages
            received_messages = self.receive_msgs(receiver_devices)


class AutopilotMavic2DJI(AutopilotControlledDrone):
    def __init__(self, devices):
        super().__init__(devices)

    def run(self):
        # Wait a second before starting
        while self.step(self.basic_time_step) != -1:
            if self.getTime() > 1:
                break

        while self.step(self.basic_time_step) != -1:
            # For now just actuate
            self.actuate()

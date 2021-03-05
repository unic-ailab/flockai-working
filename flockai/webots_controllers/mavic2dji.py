from flockai.PyCatascopia.probelib.ProcessProbe import ProcessProbe
from flockai.models.drones.autopilot_controlled_drone import AutopilotControlledDrone
from flockai.models.drones.keyboard_controller_drone import KeyboardControlledDrone
from flockai.models.probes.flockai_probe import FlockAIProbe
from flockai.models.sensors.humidity import HumiditySensor
from flockai.models.sensors.temperature import TemperatureSensor
from flockai.utils.string_generator import StringGenerator
from flockai.models.devices.device_enums import EnableableDevice, NonEnableableDevice, MotorDevice
from flockai.utils.intensive_thread import IntensiveThread
import numpy as np


class KeyboardMavic2DJI(KeyboardControlledDrone):
    """
    A Keyboard Controlled Mavic2DJI
    """

    def __init__(self, devices, probe: FlockAIProbe=None, model=None):
        self.P_COMM = 8.4
        self.DJI_A3_FC = 8
        self.RASPBERRY_PI_4B_IDLE = 4
        self.RASPBERRY_PI_4B_ACTIVE = 8
        super().__init__(devices)
        self.probe = probe
        self._activate_probes()
        self.model = model

    def _activate_probes(self):
        if self.probe is not None:
            self.probe.activate()
            print(f'{self.probe.get_name()} probe activated')

    def send_msg(self, msg, emitter_devices: list):
        """
        Sends a message from the attached emitter device
        :param emitter_devices: The emitter devices to send the message
        :param msg: The message to send
        :return: None
        """

        total_time = 0
        probe_alive_time = self.probe.get_metric('ProbeAliveTimeMetric')

        for emitter in emitter_devices:
            if emitter not in self.devices:
                print(f"The specified emitter device is not found: {emitter}")
                return 0
            f_emitter = self.devices[emitter]['device']
            t1 = probe_alive_time.get_val()
            f_emitter.send(msg.encode('utf-8'))
            t2 = probe_alive_time.get_val()
            total_time += t2 - t1

        return total_time

    def receive_msgs(self, receiver_devices: list):
        """
        Receive messages on the receiver device
        :param receiver_devices: The receiver device name as a string
        :return: None
        """
        total_time = 0
        messages = []
        probe_alive_time = self.probe.get_metric('ProbeAliveTimeMetric')

        for receiver in receiver_devices:
            if receiver not in self.devices:
                print(f"The specified receiver device is not found: {receiver}")
                return [], 0

            f_receiver = self.devices[receiver]['device']
            while f_receiver.getQueueLength() > 0:
                t1 = probe_alive_time.get_val()
                message_received = f_receiver.getData().decode('utf-8')
                messages.append(message_received)
                f_receiver.nextPacket()
                t2 = probe_alive_time.get_val()
                total_time += t2 - t1

        return messages, total_time

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

        probe_alive_time = self.probe.get_metric('ProbeAliveTimeMetric')
        probe_cpu_time = self.probe.get_metric('ProcessCpuTimeMetric')
        probe_io_time = self.probe.get_metric('ProcessIOTimeMetric')

        total_energy = 0
        net_transaction_time = 0
        temperature_sensor = TemperatureSensor('data/temperature_data.txt')
        humidity_sensor = HumiditySensor('data/humidity_data.txt')

        while self.step(self.basic_time_step) != -1:
            # Blink lights
            self.blink_led_lights(led_devices)
            # Fly drone
            self.actuate()

            # Get battery data
            # print(self.batterySensorGetValue())

            # Do an intensive task
            # t = IntensiveThread()
            # t.run()

            # Send messages
            transmit_time = self.send_msg(StringGenerator.get_random_message(100), emitter_devices)
            # print("Transmit time:", transmit_time)

            # Receive messages
            received_messages, receive_time = self.receive_msgs(receiver_devices)
            # print("Receive time:", receive_time)

            flight_time = probe_alive_time.get_val()
            cpu_time = probe_cpu_time.get_val()
            t = probe_io_time.get_val()
            io_time = 0 if t is None else t
            idle_time = flight_time - (cpu_time + io_time)

            total_energy += flight_time * self.DJI_A3_FC
            # print("Total energy consumed:", total_energy)

            humidity_max, humidity_min, humidity_avg = humidity_sensor.get_values()
            temperature_max, temperature_min, temperature_avg = temperature_sensor.get_values()

            input_vector = np.array([[temperature_max], [temperature_min], [temperature_avg],
                                     [humidity_max], [humidity_min], [humidity_avg]]).reshape(1, -1)
            print(self.model.predict(input_vector))

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

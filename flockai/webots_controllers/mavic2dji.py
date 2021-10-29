from flockai.models.drones.autopilot_controlled_drone import AutopilotControlledDrone
from flockai.models.drones.keyboard_controller_drone import KeyboardControlledDrone
from flockai.models.probes.flockai_probe import FlockAIProbe
from flockai.models.devices.device_enums import EnableableDevice, NonEnableableDevice
import time
import json

class KeyboardMavic2DJI(KeyboardControlledDrone):
    """
    A Keyboard Controlled Mavic2DJI
    """

    def __init__(self, devices, probe: FlockAIProbe=None, model=None):
        super().__init__(devices)
        self.probe = probe
        self._activate_probes()
        self.model = model

    def _activate_probes(self):
        if self.probe is not None:
            self.probe.activate()
            print(f'{self.probe.get_name()} probe activated')

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

    def get_processing_energy(self, start_flight_time):
        probe_alive_time = self.probe.get_metric('ProbeAliveTimeMetric')
        probe_cpu_time = self.probe.get_metric('ProcessCpuTimeMetric')
        probe_io_time = self.probe.get_metric('ProcessIOTimeMetric')

        cpu_time = probe_cpu_time.get_val()
        flight_time = time.time() - start_flight_time
        t = probe_io_time.get_val()
        io_time = 0 if t is None else t

        return self.energy_model.processing_energy.calculate(cpu_time_active=cpu_time, flight_time=flight_time, io_time=io_time)

    def get_communication_energy(self, start_flight_time, comm_transmit_time, comm_receive_time):
        probe_alive_time = self.probe.get_metric('ProbeAliveTimeMetric')
        flight_time = time.time() - start_flight_time
        return self.energy_model.communication_energy.calculate(transmit_time=comm_transmit_time, receive_time=comm_receive_time, idle_time=flight_time-(comm_transmit_time + comm_receive_time))

    def get_motor_energy(self, start_flight_time):
        probe_alive_time = self.probe.get_metric('ProbeAliveTimeMetric')
        flight_time = time.time() - start_flight_time
        return self.energy_model.motor_energy.calculate(hovering_time=flight_time)

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

        comm_transmit_time = 0
        comm_receive_time = 0
        cumm_inference_time = 0

        start_flight_time = time.time()
        while self.step(self.basic_time_step) != -1:

            if self.getTime() > 600:
                break

            self.blink_led_lights(led_devices)
            self.actuate()

            # Drone sends data specified by the user to the base station if ML is not running on board
            # TODO:

            # comm_transmit_time += t2 - t1
            # t1 = time.time()
            # received_messages = self.receive_msgs(receiver_devices=receiver_devices)
            # t2 = time.time()
            # comm_receive_time += t2 - t1

            # Execute prediction pipeline step
            inference_time = 0
            if self.model is not None:
                t1 = time.time()
                prediction = self.model.predict()
                t2 = time.time()
                inference_time = t2 - t1
                cumm_inference_time += inference_time

                # t1 = time.time()
                # self.send_msg(msg=str(prediction), emitter_devices=emitter_devices)
                # t2 = time.time()
                # comm_transmit_time += t2 - t1

                if prediction is not None:
                    print(prediction)

            # Get energy values on each cycle
            energy = {**self.get_processing_energy(start_flight_time=start_flight_time),
                      **self.get_communication_energy(start_flight_time=start_flight_time, comm_transmit_time=comm_transmit_time, comm_receive_time=comm_receive_time),
                      **self.get_motor_energy(start_flight_time=start_flight_time), 'simulation_time_s': self.getTime(),
                      'cpu_time_s': self.probe.get_metric('ProcessCpuTimeMetric').get_val(),
                      'inference_time_s': inference_time,
                      'cumm_inference_time_s': cumm_inference_time}

            energy['total_energy'] = energy['e_proc'] + energy['e_comm'] + energy['e_motor']

            # Update battery values
            self.battery.remaining_energy_percentage = 1.0 - (energy['total_energy'] / self.battery.energy_capacity)

            if self.getTime() % 5.0 != 0.0:
                continue

            # Update log data every 5 minutes with energy values
            print(energy, f'\n{self.battery.remaining_energy_percentage * 100}% battery remaining')
            with open('logs/Crowd_Detection_on_drone_no_flight_probe.json', 'a+') as logfile:
                json.dump(energy, logfile)
                logfile.write('\n')


class AutopilotMavic2DJI(AutopilotControlledDrone):
    def __init__(self, devices, probe: FlockAIProbe=None, model=None):
        super().__init__(devices)

    def send_msg(self, msg, emitter_devices: list):
        """
        Sends a message from the attached emitter device
        :param emitter_devices: The emitter devices to send the message
        :param msg: The message to send
        :return: None
        """
        total_time = 0

        for emitter in emitter_devices:
            if emitter not in self.devices:
                print(f"The specified emitter device is not found: {emitter}")
                return 0
            f_emitter = self.devices[emitter]['device']

        return total_time

    def run(self):
        # Wait a second before starting
        while self.step(self.basic_time_step) != -1:
            if self.getTime() > 1:
                break

        emitter_devices = []
        for device_name in self.devices:
            if self.devices[device_name]['type'] == NonEnableableDevice.EMITTER:
                emitter_devices.append(device_name)

        while self.step(self.basic_time_step) != -1:
            # For now just actuate
            self.actuate()

# Copyright 1996-2020 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This controller gives to its node the following behavior:
Listen the keyboard. According to the pressed key, send a
message through an emitter or handle the position of Robot1.
"""

from controller import Robot
from flockai.interfaces.robot import IRobot
from flockai.models.base.base_station import IBaseStation
from flockai.models.devices.device_enums import NonEnableableDevice, EnableableDevice, Devices
import json


class BaseStation(IBaseStation):
    def __init__(self, devices):
        super(BaseStation, self).__init__(devices)

    def blink_led_lights(self, led_devices: list):
        """
        Blink led lights every 2 seconds
        :return:
        """
        f_led_devices = [self.devices[led]['device'] for led in led_devices]
        led_on = (self.getTime() // 1) % 2 == 1

        for f_led in f_led_devices:
            # print('Blinking')
            f_led.set(led_on)
            led_on = not led_on

    def receive_msgs(self, receiver_devices: list):
        """
        Receive messages on the receiver device
        :param receiver_devices: The receiver device name as a string
        :return: None
        """
        messages = []

        for receiver in receiver_devices:
            if receiver not in self.devices:
                print(f"The specified receiver device is not found: {receiver}")
                return []

            f_receiver = self.devices[receiver]['device']
            while f_receiver.getQueueLength() > 0:
                message_received = f_receiver.getData().decode('utf-8')
                message = json.loads(message_received)
                if len(message) > 0:
                    messages.append(message)
                f_receiver.nextPacket()
        return messages

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

        while self.step(self.basic_time_step) != -1:
            # Blink lights
            self.blink_led_lights(led_devices)

            # Send messages
            # transmit_time = self.send_msg(StringGenerator.get_random_message(100), emitter_devices)
            # print("Transmit time:", transmit_time)

            # Receive messages
            received_messages = self.receive_msgs(receiver_devices)
            if len(received_messages) > 0:
                print('Received a message')
                # print("Received message:", received_messages)


enableable_devices = [
    (EnableableDevice.RECEIVER, "receiver"),
]

non_enableable_devices = [
    (NonEnableableDevice.LED, "led left"),
    (NonEnableableDevice.LED, "led middle"),
    (NonEnableableDevice.LED, "led right"),
]
devices = Devices(enableable_devices=enableable_devices, non_enableable_devices=non_enableable_devices, motor_devices=None)

controller = BaseStation(devices=devices)
controller.run()

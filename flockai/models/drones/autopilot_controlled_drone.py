import abc

from controller import Radar
from flockai.interfaces.drone import IDrone


class AutopilotControlledDrone(IDrone, abc.ABC):
    def __init__(self, devices):
        super().__init__(devices)
        self.multiplier = 1
        self.target_id_count = 0

    def get_input(self):
        """
        The drone rotates until it identifies a target.
        When a target is identified, the drone moves forward
        :return: A tuple with pitch, roll, yaw disturbance to actuate the drone
        """
        radar: Radar = self.devices['radar']['device']
        total_targets = radar.getNumberOfTargets()
        targets = radar.getTargets()

        if total_targets > 0:
            self.target_id_count += 1
            for i in range(total_targets):
                print(f'--target {i}: distance = {targets[i].distance} azimuth = {targets[i].azimuth}')
                if targets[i].distance < 2.5:
                    print('emitting')
                    emitter = self.devices['emitter']['device']
                    message = 'DESTINATION_ARRIVED'
                    emitter.send(message.encode('utf-8'))

            if self.target_id_count == 1:
                self.multiplier *= -1

            roll_disturbance, pitch_disturbance, yaw_disturbance = 0, 2, 0
        else:
            self.target_id_count = 0
            roll_disturbance, pitch_disturbance, yaw_disturbance = 0, 0, self.multiplier * 0.4

        return roll_disturbance, pitch_disturbance, yaw_disturbance

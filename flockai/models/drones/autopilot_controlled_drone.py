import abc
import json

from controller import Radar, RadarTarget
from flockai.interfaces.drone import IDrone


class AutopilotControlledDrone(IDrone, abc.ABC):
    def __init__(self, devices):
        super().__init__(devices)
        self.target = [5, 5]
        self.prev_distance = self.get_distance_from_target()
        self.simulation_step = 0
        self.multiplier = 1
        self.target_identified = False
        self.target_id_count = 0

    def set_flight_plan(self, plan):
        pass

    def update_flight_plan(self, plan):
        pass

    def abort_flight_plan(self):
        pass

    def get_flight_plan(self):
        pass

    def move(self, direction=1):
        """
        Return forward or backward disturbance for moving
        :param direction: 1 for forward, -1 for backward, 0 for stable
        :return:
        """
        pitch_disturbance = 2 * direction
        return pitch_disturbance

    def rotate(self, direction=1):
        """
        Return left or right disturbance for rotation
        :param direction: 1 for right, -1 for left, 0 for stable
        :return:
        """
        yaw_disturbance = 1.3 * direction

    def should_move_forward(self, target):
        pass

    def get_coordinates(self):
        gps = self.devices['gps']['device']
        return gps.getValues()

    def get_distance_from_target(self):
        coordinates = self.get_coordinates()
        distances = [abs(coordinates[0] - self.target[0]), abs(coordinates[2] - self.target[1])]
        return distances

    def target_has_reached(self):
        distance = [d // 1 for d in self.get_distance_from_target()]
        return not any(distance)

    def on_track(self):
        new_distance = self.get_distance_from_target()
        ok = all([self.prev_distance[0] > new_distance[0], self.prev_distance[1] > new_distance[1]])
        self.prev_distance = new_distance
        return ok

    def get_input(self):
        """
        Input is based on if we are getting closer to the target
        In case we are on the target no input is given
        :return:
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
            return 0, 2, 0
        else:
            self.target_id_count = 0
            return 0, 0, self.multiplier * 0.4
            # return roll_disturbance, pitch_disturbance, yaw_disturbance

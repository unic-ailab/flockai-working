import abc

from flockai.interfaces.drone import IDrone


class AutopilotControlledDrone(IDrone, abc.ABC):
    def __init__(self, devices):
        super().__init__(devices)

    def set_flight_plan(self, plan):
        pass

    def update_flight_plan(self, plan):
        pass

    def abort_flight_plan(self):
        pass

    def get_flight_plan(self):
        pass

    def get_input(self):
        # Transform the keyboard input to disturbances on the stabilization algorithm.
        roll_disturbance = 0
        pitch_disturbance = 2
        yaw_disturbance = 0

        return roll_disturbance, pitch_disturbance, yaw_disturbance

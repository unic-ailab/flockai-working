import abc

from flockai.interfaces.drone import IDrone


class AutopilotControlledDrone(IDrone, abc.ABC):
    def set_flight_plan(self, plan):
        pass

    def update_flight_plan(self, plan):
        pass

    def abort_flight_plan(self):
        pass

    def get_flight_plan(self):
        pass

    def get_input(self):
        pass

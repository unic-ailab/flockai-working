import abc
from flockai.interfaces.drone import IDrone
from controller import Keyboard


class KeyboardControlledDrone(IDrone, abc.ABC):
    """
    Defines a drone which can be controlled with keyboard controls
    """

    def __init__(self, devices):
        super().__init__(devices)

    @classmethod
    def display_controls(cls):
        """
        Displays keyboard controls message to stdout
        :return:
        """
        print("You can control the drone with your computer keyboard:")
        print("- 'up': move forward.")
        print("- 'down': move backward.")
        print("- 'right': turn right.")
        print("- 'left': turn left.")
        print("- 'shift + up': increase the target altitude.")
        print("- 'shift + down': decrease the target altitude.")
        print("- 'shift + right': strafe right.")
        print("- 'shift + left': strafe left.")

    def get_input(self) -> tuple:
        """
        Defines the keyboard input to actuate the drone
        :return: A tuple with pitch, roll, yaw disturbance to actuate the drone
        """
        # Transform the keyboard input to disturbances on the stabilization algorithm.
        roll_disturbance = 0
        pitch_disturbance = 0
        yaw_disturbance = 0

        def get_key_input():
            return self.devices['keyboard']['device'].getKey()

        key_input = get_key_input()
        while key_input > 0:
            if key_input == Keyboard.UP:
                pitch_disturbance = 2.0
            elif key_input == Keyboard.DOWN:
                pitch_disturbance = -2.0
            elif key_input == Keyboard.RIGHT:
                yaw_disturbance = 1.3
            elif key_input == Keyboard.LEFT:
                yaw_disturbance = -1.3
            elif key_input == Keyboard.SHIFT + Keyboard.UP:
                self.target_altitude += 0.05
            elif key_input == Keyboard.SHIFT + Keyboard.DOWN:
                self.target_altitude -= 0.05
            elif key_input == Keyboard.SHIFT + Keyboard.RIGHT:
                roll_disturbance = -1.0
            elif key_input == Keyboard.SHIFT + Keyboard.LEFT:
                roll_disturbance = 1.0
            key_input = get_key_input()

        return roll_disturbance, pitch_disturbance, yaw_disturbance

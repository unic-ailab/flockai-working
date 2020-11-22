import abc
from flockai.interfaces.robot import IRobot
import math
from flockai.utils.graphics import Graphics


class IDrone(IRobot, abc.ABC):
    """
    Define all actions needed for flying a drone and declare the get_input() abstract method
    """
    def __init__(self):
        super().__init__()
        self._set_constants()
        self._set_variables()

    def _set_variables(self):
        """
        Set variables needed for controlling the drone on air
        :return:
        """
        self.target_altitude = 1.0      # The target altitude. Can be modified

    def _set_constants(self):
        """
        Set constants needed for controlling the drone on air
        :return: None
        """
        self.K_VERTICAL_THRUST = 68.5   # this thrust lifts the drone
        self.K_VERTICAL_OFFSET = 0.6    # Vertical offset where the robot actually targets to stabilize itself
        self.K_VERTICAL_P = 3.0         # P constant of the vertical PID
        self.K_ROLL_P = 50.0            # P constant of the roll PID
        self.K_PITCH_P = 30.0           # P constant of the pitch PID
        self.K_YAW_P = 20.0             # P constant of the yaw PID

    def actuate(self):
        """
        Fly the drone by stabilizing it based on camera motor sensors and input
        :return: None
        """
        roll, pitch, yaw = self.imu.getRollPitchYaw()
        roll += math.pi / 2

        altitude = self.gps.getValues()[1]
        roll_acceleration, pitch_acceleration, yaw_acceleration = self.gyro.getValues()

        # Set camera motors based on current gyro data
        self.camera_roll_motor.setPosition(-0.115 * roll_acceleration)
        self.camera_pitch_motor.setPosition(-0.1 * pitch_acceleration)

        # Get input
        roll_disturbance, pitch_disturbance, yaw_disturbance = self.get_input()

        roll_input = self.K_ROLL_P * Graphics.clamp(roll, -1.0, 1.0) + roll_acceleration + roll_disturbance
        pitch_input = self.K_PITCH_P * Graphics.clamp(pitch, -1.0, 1.0) - pitch_acceleration + pitch_disturbance
        yaw_input = yaw_disturbance
        clamped_difference_altitude = Graphics.clamp(self.target_altitude - altitude + self.K_VERTICAL_OFFSET, -1.0,
                                                     1.0)
        vertical_input = self.K_VERTICAL_P * pow(clamped_difference_altitude, 3.0)

        # Actuate based on inputs
        front_left_motor_input = self.K_VERTICAL_THRUST + vertical_input - roll_input - pitch_input + yaw_input
        front_right_motor_input = self.K_VERTICAL_THRUST + vertical_input + roll_input - pitch_input - yaw_input
        rear_left_motor_input = self.K_VERTICAL_THRUST + vertical_input - roll_input + pitch_input - yaw_input
        rear_right_motor_input = self.K_VERTICAL_THRUST + vertical_input + roll_input + pitch_input + yaw_input

        # print(front_left_motor_input, front_right_motor_input, rear_left_motor_input, rear_right_motor_input)
        self.front_left_motor.setVelocity(front_left_motor_input)
        self.front_right_motor.setVelocity(-front_right_motor_input)
        self.rear_left_motor.setVelocity(-rear_left_motor_input)
        self.rear_right_motor.setVelocity(rear_right_motor_input)

    @abc.abstractmethod
    def get_input(self) -> tuple:
        """
        Get the input for actuating the drone
        :return: A tuple with pitch, roll, yaw disturbance to actuate the drone
        """
        raise NotImplementedError




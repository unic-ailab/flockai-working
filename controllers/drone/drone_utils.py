from typing import List
import math
from controller import Keyboard, Robot, Emitter, Receiver, Camera, InertialUnit, GPS, Compass, Gyro, LED, Motor
from utility import Graphics

def M_PI():
    return 3.14159

class DroneUtils(Robot):
    def __init__(self):
        super(DroneUtils, self).__init__()
        self._initialize_drone()

    def _initialize_drone(self):
        self.timestep = 1000  # Timestep
        self.name = self.getName()  # Name
        self._set_attached_devices()  # Set attached devices
        devices = self._get_attached_devices()
        self._enable_devices(devices)  # Enable devices

        self._set_attached_motors()  # Set attached motors
        self._set_initial_motor_fields()  # Set any initial value to motors

        self._display_keyboard_controls()  # Display controls
        self._set_empirical_constants()  # Set constants
        self._set_variables()  # Set variables

    def _set_attached_devices(self) -> None:
        """
        Set new devices here. Note: Don't forget to add it to the _get_attached_devices list also
        :return:
        """
        self.emitter: Emitter = self.getEmitter("emitter")
        self.receiver: Receiver = self.getReceiver("receiver")
        self.camera: Camera = self.getCamera("camera")
        self.front_left_led: LED = self.getLED("front left led")
        self.front_right_led: LED = self.getLED("front right led")
        self.imu: InertialUnit = self.getInertialUnit("inertial unit")
        self.gps: GPS = self.getGPS("gps")
        self.compass: Compass = self.getCompass("compass")
        self.gyro: Gyro = self.getGyro("gyro")
        self.keyboard: Keyboard
        self.batterySensorEnable(self.timestep)

    def _get_attached_devices(self):
        """
        Return the list with the devices that the robot has. New devices should be registered here as well
        :return:
        """
        return [
            self.emitter,
            self.receiver,
            self.camera,
            self.front_left_led,
            self.front_right_led,
            self.imu,
            self.gps,
            self.compass,
            self.gyro,
            self.keyboard
        ]

    def _enable_devices(self, devices, timestep=None) -> None:
        """
        Enables the devices
        :param devices: List of devices that the robot has
        :param timestep: Optional if a custom timestep will be tested
        :return:
        """

        for device in devices:
            try:
                device.enable(self.timestep if timestep is None else timestep)
            except AttributeError:
                pass

    def _set_attached_motors(self):
        """
        Define the motors that are used on the robot
        :return:
        """
        # Camera angle motors
        self.camera_roll_motor = self.getMotor("camera roll")
        self.camera_pitch_motor = self.getMotor("camera pitch")
        self.camera_yaw_motor = self.getMotor("camera yaw")

        # Propellers
        self.front_left_motor = self.getMotor("front left propeller")
        self.front_right_motor = self.getMotor("front right propeller")
        self.rear_left_motor = self.getMotor("rear left propeller")
        self.rear_right_motor = self.getMotor("rear right propeller")

    def _set_initial_motor_fields(self):
        """
        Set any initial field values for drone motors
        :return:
        """
        # Set position & velocity for propellers
        self.motors: List[Motor] = [
            self.front_left_motor,
            self.front_right_motor,
            self.rear_left_motor,
            self.rear_right_motor
        ]

        for motor in self.motors:
            motor.setPosition(float('inf'))
            motor.setVelocity(1.0)

    def _set_empirical_constants(self):
        """
        Set constants used across the simulation, based on empirical analysis
        :return: None
        """
        self.K_VERTICAL_THRUST = 68.5  # this thrust lifts the drone
        self.K_VERTICAL_OFFSET = 0.6  # Vertical offset where the robot actually targets to stabilize itself
        self.K_VERTICAL_P = 3.0  # P constant of the vertical PID
        self.K_ROLL_P = 50.0  # P constant of the roll PID
        self.K_PITCH_P = 30.0  # P constant of the pitch PID

    def _set_variables(self):
        """
        Set variables used across the simulation
        :return: None
        """
        self.target_altitude = 1.0  # The target altitude. Can be modified

    @staticmethod
    def _display_keyboard_controls():
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

    def blink_led_lights(self, time):
        """
        Blink led lights every 2 seconds
        :param time: The simulation time. ie self.getTime()
        :return:
        """
        led_on = (time // 1) % 2 == 1
        self.front_left_led.set(led_on)
        self.front_right_led.set(led_on)

    def stabilize_drone(self):
        """
        Stabilizes the drone based on camera motor sensors and user movement input
        TODO: BUGGY FUNCTION. there is probably an error in decimals
        :return: None
        """
        roll, pitch, yaw = self.imu.getRollPitchYaw()
        #changed
        roll += M_PI() / 2
        
        altitude = self.gps.getValues()[1]
        roll_acceleration, pitch_acceleration, yaw_acceleration = self.gyro.getValues()

        # Set camera motors based on current gyro data
        self.camera_roll_motor.setPosition(-0.115 * roll_acceleration)
        self.camera_pitch_motor.setPosition(-0.1 * pitch_acceleration)

        # Transform the keyboard input to disturbances on the stabilization algorithm.
        roll_disturbance = 0
        pitch_disturbance = 0
        yaw_disturbance = 0

        key_input = self.keyboard.getKey()
        while key_input > 0:
            if key_input == Keyboard.UP:
                pitch_disturbance = 2.0
            elif key_input == Keyboard.DOWN:
                pitch_disturbance = -2.0
            elif key_input == Keyboard.RIGHT:
                #changed
                yaw_disturbance = 1.3
            elif key_input == Keyboard.LEFT:
                #changed
                yaw_disturbance = -1.3
            elif key_input == Keyboard.SHIFT + Keyboard.UP:
                self.target_altitude += 0.05
            elif key_input == Keyboard.SHIFT + Keyboard.DOWN:
                self.target_altitude -= 0.05
            elif key_input == Keyboard.SHIFT + Keyboard.RIGHT:
                roll_disturbance = -1.0
            elif key_input == Keyboard.SHIFT + Keyboard.LEFT:
                roll_disturbance = 1.0
            key_input = self.keyboard.getKey()

        #changed
        roll_input = self.K_ROLL_P * Graphics.clamp(roll, -1.0, 1.0) + roll_acceleration + roll_disturbance
        pitch_input = self.K_PITCH_P * Graphics.clamp(pitch, -1.0, 1.0) - pitch_acceleration + pitch_disturbance
        yaw_input = yaw_disturbance
        clamped_difference_altitude = Graphics.clamp(self.target_altitude - altitude + self.K_VERTICAL_OFFSET, -1.0,1.0)
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

    def send_message(self, message: str) -> None:
        """
        Sends a message from the attached emitter device
        :param message: The message to send
        :return: None
        """
        if self.emitter is None:
            print("There is not emitter device attached")

        print(f'{self.name}: I am sending {message}')
        self.emitter.send(message.encode('utf-8'))

    def receive_messages(self) -> None:
        """
        Receive messages on the receiver device
        :param receiver: The attached receiver device instance
        :param name: Optional for debugging purposes, the name of the robot
        :return: None
        """
        if self.receiver is None:
            print("There is no receiver device attached")
            return

        while self.receiver.getQueueLength() > 0:
            message_received = self.receiver.getData().decode('utf-8')
            print(f'{self.name}: I have received this message {message_received}')
            self.receiver.nextPacket()


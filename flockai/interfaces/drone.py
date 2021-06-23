import abc
import json

from flockai.interfaces.robot import IRobot
import math

from flockai.models.battery.battery import Battery
from flockai.models.devices.device_enums import EnableableDevice, MotorDevice, AircraftAxis, Relative2DPosition
from flockai.models.energy.energy import Energy
from flockai.utils.graphics import Graphics


class IDrone(IRobot, abc.ABC):
    """
    Define all actions needed for flying a drone and declare the get_input() abstract method
    """

    def __init__(self, devices):
        super().__init__()
        # DEFINE ENERGY CONSTANTS FIRST

        self.name = self.getName()
        self.energy_model = Energy()
        self.battery = Battery()

        self.basic_time_step = int(self.getBasicTimeStep())
        self.devices = self._attach_and_enable_devices(devices.enableable_devices, devices.non_enableable_devices)
        self.motors = self._attach_and_enable_motors(devices.motor_devices)
        self._cross_check_devices()
        self._cross_check_motors()
        self._set_constants()
        self._set_variables()

    def _attach_and_enable_devices(self, en_devices, nen_devices):
        """
        Define all the required devices and enable them
        :return:
        """
        e_devices = {}
        for device, name, *sampling_period in en_devices:
            time_step = self.basic_time_step if len(sampling_period) == 0 else sampling_period[0]

            if EnableableDevice(device) == EnableableDevice.KEYBOARD:
                e_devices['keyboard'] = {'type': device, 'device': self.keyboard}
                e_devices['keyboard']['device'].enable(time_step)
            elif EnableableDevice(device) == EnableableDevice.BATTERY_SENSOR:
                self.batterySensorEnable(self.basic_time_step)
            elif name is not None:
                e_devices[name] = {'type': device, 'device': self.getDevice(name)}
                e_devices[name]['device'].enable(time_step)

        ne_devices = {}
        for device, name in nen_devices:
            if name is not None:
                ne_devices[name] = {'type': device, 'device': self.getDevice(name)}

        return {**e_devices, **ne_devices}

    def _attach_and_enable_motors(self, motor_devices):
        """
        Define all the required motors and enable them
        :return:
        """
        m_devices = {}
        for device, name, *args in motor_devices:
            if MotorDevice(device) == MotorDevice.CAMERA:
                m_devices[name] = {'type': device, 'motor': self.getDevice(name), 'axis': args[0]}
            elif MotorDevice(device) == MotorDevice.PROPELLER:
                m_devices[name] = {'type': device, 'motor': self.getDevice(name),
                                   'relative_position': args[0]}
                m_devices[name]['motor'].setPosition(float('inf'))
                m_devices[name]['motor'].setVelocity(1.0)

        return m_devices

    def _cross_check_devices(self):
        """
        Cross checks devices, making sure all of the required ones have been registered by the user in order for the drone to fly
        :return:
        """
        required_devices = {
            EnableableDevice.INERTIAL_UNIT: True,
            EnableableDevice.GPS: True,
            EnableableDevice.GYRO: True,
        }
        for device in self.devices.keys():
            f_device = self.devices[device]['device']
            f_type = self.devices[device]['type']
            if f_type in required_devices:
                if EnableableDevice(f_type) == EnableableDevice.INERTIAL_UNIT:
                    self.imu = f_device
                if EnableableDevice(f_type) == EnableableDevice.GPS:
                    self.gps = f_device
                if EnableableDevice(f_type) == EnableableDevice.GYRO:
                    self.gyro = f_device
                required_devices[f_type] = False

        for key, value in required_devices.items():
            if value:
                raise NotImplementedError(f"The drone needs {EnableableDevice(key).name} device to operate")

    def _cross_check_motors(self):
        """
        Cross checks motors, making sure all of the required ones have been registered by the user in order for the drone to fly
        :return:
        """
        front_left = repr(Relative2DPosition(1, -1))
        front_right = repr(Relative2DPosition(1, 1))
        rear_left = repr(Relative2DPosition(-1, -1))
        rear_right = repr(Relative2DPosition(-1, 1))

        required_motors = {
            MotorDevice.CAMERA: {
                AircraftAxis.ROLL: True,
                AircraftAxis.PITCH: True,
                AircraftAxis.YAW: True
            },
            MotorDevice.PROPELLER: {
                front_left: True,
                front_right: True,
                rear_left: True,
                rear_right: True,
            }
        }

        for motor in self.motors.keys():
            f_motor = self.motors[motor]['motor']
            f_type = self.motors[motor]['type']
            if f_type in required_motors:
                arg = None
                if MotorDevice(f_type) == MotorDevice.CAMERA:
                    f_axis = AircraftAxis(self.motors[motor]['axis'])
                    if AircraftAxis(f_axis) == AircraftAxis.ROLL:
                        self.camera_roll_motor = f_motor
                    if AircraftAxis(f_axis) == AircraftAxis.PITCH:
                        self.camera_pitch_motor = f_motor
                    if AircraftAxis(f_axis) == AircraftAxis.YAW:
                        self.camera_yaw_motor = f_motor
                    arg = f_axis
                elif MotorDevice(f_type) == MotorDevice.PROPELLER:
                    f_relative_position = repr(self.motors[motor]['relative_position'])
                    if f_relative_position == repr(Relative2DPosition(1, -1)):
                        self.front_left_motor = f_motor
                    if f_relative_position == repr(Relative2DPosition(1, 1)):
                        self.front_right_motor = f_motor
                    if f_relative_position == repr(Relative2DPosition(-1, -1)):
                        self.rear_left_motor = f_motor
                    if f_relative_position == repr(Relative2DPosition(-1, 1)):
                        self.rear_right_motor = f_motor
                    arg = f_relative_position
                required_motors[f_type][arg] = False

        for motor_key in required_motors.keys():
            for key, value in required_motors[motor_key].items():
                if value:
                    motor_device = MotorDevice(motor_key).name
                    if MotorDevice(motor_key) == MotorDevice.CAMERA:
                        motor_axis = AircraftAxis(key).name
                        if value:
                            raise NotImplementedError(f"The drone needs {motor_device} {motor_axis} motor to operate")
                    if MotorDevice(motor_key) == MotorDevice.PROPELLER:
                        if value:
                            raise NotImplementedError(f"The drone needs {key} {motor_device} to operate")

    def _set_variables(self):
        """
        Set variables needed for controlling the drone on air
        :return:
        """
        self.target_altitude = 1.0  # The target altitude. Can be modified

    def _set_constants(self):
        """
        Set constants needed for controlling the drone on air
        :return: None
        """
        self.K_VERTICAL_THRUST = 68.5  # this thrust lifts the drone
        self.K_VERTICAL_OFFSET = 0.6  # Vertical offset where the robot actually targets to stabilize itself
        self.K_VERTICAL_P = 3.0  # P constant of the vertical PID
        self.K_ROLL_P = 50.0  # P constant of the roll PID
        self.K_PITCH_P = 30.0  # P constant of the pitch PID
        self.K_YAW_P = 20.0  # P constant of the yaw PID

        # Set E_PROC constants
        self.energy_model.processing_energy.p_fc = self.energy_model.DJI_A3_FC
        self.energy_model.processing_energy.p_cpu_active = self.energy_model.RASPBERRY_PI_4B_ACTIVE
        self.energy_model.processing_energy.p_cpu_idle = self.energy_model.RASPBERRY_PI_4B_IDLE
        self.energy_model.processing_energy.p_cpu_io = self.energy_model.RASPBERRY_PI_4B_IDLE

        # Set E_COMM constants
        self.energy_model.communication_energy.p_transmit = self.energy_model.P_COMM  # 8.4
        self.energy_model.communication_energy.p_receive = self.energy_model.P_COMM   # 8.4
        self.energy_model.communication_energy.p_idle = self.energy_model.P_COMM / 2  # 4.2

        # Set E_MOTOR constants
        self.energy_model.motor_energy.p_hover = self.energy_model.DJI_P_HOVER

        # Set BATTERY constants
        self.battery.charge_capacity = self.battery.DJI_CHARGE_CAPACITY
        self.battery.voltage = self.battery.DJI_VOLTAGE
        self.battery.energy_capacity = self.battery.DJI_ENERGY_CAPACITY
        self.battery.max_flight_time = self.battery.DJI_MAX_FLIGHT_TIME
        self.battery.max_hover_time = self.battery.DJI_MAX_HOVERING_TIME
        self.battery.safe_landing_percentage = self.battery.DJI_SAFE_LANDING_PERCENTAGE

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
        if self.battery.remaining_energy_percentage <= self.battery.safe_landing_percentage:
            roll_disturbance, pitch_disturbance, yaw_disturbance = 0, 0, 0
            self.target_altitude -= 0.05
            print('Safe landing')
        else:
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

        self.front_left_motor.setVelocity(front_left_motor_input)
        self.front_right_motor.setVelocity(-front_right_motor_input)
        self.rear_left_motor.setVelocity(-rear_left_motor_input)
        self.rear_right_motor.setVelocity(rear_right_motor_input)

    def send_msg(self, msg, emitter_devices: list):
        """
        Sends a message from the attached emitter device
        :param emitter_devices: The emitter devices to send the message
        :param msg: The message to send
        :return: Time required to send the message
        """
        for emitter in emitter_devices:
            if emitter not in self.devices:
                print(f"The specified emitter device is not found: {emitter}")
                return 0
            f_emitter = self.devices[emitter]['device']
            message = json.dumps(msg)
            f_emitter.send(message.encode('utf-8'))

    def receive_msgs(self, receiver_devices: list):
        """
        Receive messages on the receiver device
        :param receiver_devices: The receiver device name as a string
        :return: The list of messages and the time required to receive them
        """
        messages = []

        for receiver in receiver_devices:
            if receiver not in self.devices:
                print(f"The specified receiver device is not found: {receiver}")
                return [], 0
            f_receiver = self.devices[receiver]['device']
            while f_receiver.getQueueLength() > 0:
                message_received = f_receiver.getData().decode('utf-8')
                messages.append(message_received)
                f_receiver.nextPacket()

        return messages

    @abc.abstractmethod
    def get_input(self) -> tuple:
        """
        Get the input for actuating the drone
        :return: A tuple with pitch, roll, yaw disturbance to actuate the drone
        """
        raise NotImplementedError

from typing import List

from flockai.models.drones.keyboard_controller_drone import KeyboardControlledDrone
from flockai.utils.string_generator import StringGenerator
from controller import InertialUnit, Camera, LED, Emitter, Receiver, GPS, Compass, Gyro, Motor


class KeyboardMavic2DJI(KeyboardControlledDrone):
    """
    A Keyboard Controlled Mavic2DJI
    """
    def __init__(self):
        super().__init__()
        self._initialize()

    def _initialize(self):
        """
        Initialization step
        :return:
        """
        self.name = self.getName()
        self.basic_time_step = int(self.getBasicTimeStep())
        self._attach_and_enable_devices()
        self._attach_and_enable_motors()
        self.keyboard.enable(self.basic_time_step)
        self.batterySensorEnable(self.basic_time_step)

    def _attach_and_enable_devices(self):
        """
        Define all the required devices and enable them
        :return:
        """
        self.emitter: Emitter = self.getEmitter("emitter")

        self.receiver: Receiver = self.getReceiver("receiver")
        self.receiver.enable(self.basic_time_step)

        self.camera: Camera = self.getCamera("camera")
        self.camera.enable(self.basic_time_step)

        self.front_left_led: LED = self.getLED("front left led")
        self.front_right_led: LED = self.getLED("front right led")

        self.imu: InertialUnit = self.getInertialUnit("inertial unit")
        self.imu.enable(self.basic_time_step)

        self.gps: GPS = self.getGPS("gps")
        self.gps.enable(self.basic_time_step)

        self.compass: Compass = self.getCompass("compass")
        self.compass.enable(self.basic_time_step)

        self.gyro: Gyro = self.getGyro("gyro")
        self.gyro.enable(self.basic_time_step)

    def _attach_and_enable_motors(self):
        """
        Define all the required motors and enable them
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

        # Set position & velocity for propellers
        propellers: List[Motor] = [
            self.front_left_motor,
            self.front_right_motor,
            self.rear_left_motor,
            self.rear_right_motor
        ]

        for propeller in propellers:
            propeller.setPosition(float('inf'))
            propeller.setVelocity(1.0)

    def send_msg(self, msg):
        """
        Sends a message from the attached emitter device
        :param msg: The message to send
        :return: None
        """
        if self.emitter is None:
            print("There is not emitter device attached")

        # print(f'{self.name}: I am sending {message}')
        self.emitter.send(msg.encode('utf-8'))

    def receive_msgs(self):
        """
        Receive messages on the receiver device
        :return: None
        """
        if self.receiver is None:
            print("There is no receiver device attached")
            return

        while self.receiver.getQueueLength() > 0:
            message_received = self.receiver.getData().decode('utf-8')
            # print(f'{self.name}: I have received this message {message_received}')
            self.receiver.nextPacket()

    def blink_led_lights(self, time):
        """
        Blink led lights every 2 seconds
        :param time: The simulation time. ie self.getTime()
        :return:
        """
        led_on = (time // 1) % 2 == 1
        self.front_left_led.set(led_on)
        self.front_right_led.set(not led_on)

    def run(self):
        # Wait a second before starting
        while self.step(self.basic_time_step) != -1:
            if self.getTime() > 1:
                break

        while self.step(self.basic_time_step) != -1:
            time = self.getTime()

            # Blink lights
            self.blink_led_lights(time)
            # Fly drone
            self.actuate()

            # Get battery data
            # print(self.batterySensorGetValue())

            # Retrieve image data
            # self.save_image_every_sec(time, 2)

            # Send messages
            self.send_msg(StringGenerator.get_random_message(4))
            # Receive messages
            self.receive_msgs()



    # def save_image_every_sec(self, time, sec):
    #     """
    #     Saves images every X seconds
    #     :param time: The simulation time
    #     :param sec: The timestep in seconds
    #     :return:
    #     """
    #     config = SimulationConfig()
    #     if config.simulation_enabled:
    #         save_image = (time // 1) % sec == 1
    #         if save_image:
    #             self.camera.saveImage(f"{config.get_simulation_image_directory()}test_{time}.png", 50)  # quality in range [1, 100]
    #     else:
    #         print("Note: Data collection is not enabled")

    # @classmethod
    # def enable_data_collection(cls):
    #     config = SimulationConfig()
    #     config.simulation_enabled = True
    #     print("Running Simulation: ", config.get_simulation_id())
    #     config.create_simulation_image_directory()
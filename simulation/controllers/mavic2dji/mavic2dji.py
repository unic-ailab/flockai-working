from flockai.drone_utils import DroneUtils
from flockai.utility import IntensiveThread, IntensityLevel, StringGenerator


class Mavic2DJI(DroneUtils):
    def __init__(self):
        super(Mavic2DJI, self).__init__()
        # self.enable_data_collection()

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
            self.stabilize_drone()

            # Get battery data
            # print(self.batterySensorGetValue())

            # Retrieve image data
            # self.save_image_every_sec(time, 2)

            # Do some intensive task
            t = IntensiveThread(IntensityLevel.LOW)
            # t.start()
            # Send messages
            self.send_message(StringGenerator.get_random_message(4))
            # Receive messages
            self.receive_messages()
            #changed
            #if t.is_alive():
            #    print(f"Task {t.native_id} did not finish :(")
            #else:
            #    print(f"Task {t.native_id} finished")


# Create drone instance and run its controller
controller = Mavic2DJI()
controller.run()

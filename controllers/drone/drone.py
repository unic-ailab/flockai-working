from drone_utils import DroneUtils
from utility import IntensiveThread, IntensityLevel, StringGenerator, SimulationConfig


class Drone(DroneUtils):
    def __init__(self):
        super(Drone, self).__init__()
        self.config = SimulationConfig()
        # If image data collection is needed
        print("Running Simulation: ", self.config.get_simulation_id())
        self.config.create_simulation_image_directory()

    def run(self):

        # Wait a second before starting
        while self.step(self.timestep) != -1:
            if self.getTime() > 1:
                break

        while self.step(self.timestep) != -1:
            time = self.getTime()
            # Blink lights
            self.blink_led_lights(time)
            # Fly drone
            self.stabilize_drone()
            # Get battery data
            print(self.batterySensorGetValue())
            # Retrieve image data
            self.camera.saveImage(f"{self.config.get_simulation_image_directory()}test_{time}.png", 50)  # quality in range [1, 100]
            # Do some intensive task
            t = IntensiveThread(IntensityLevel.LOW)
            t.start()
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
controller = Drone()
controller.run()

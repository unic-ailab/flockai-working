import enum
import threading


class IntensityLevel(enum.IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class IntensiveThread(threading.Thread):

    numbers = {
        IntensityLevel.LOW: 1000,
        IntensityLevel.NORMAL: 1000000,
        IntensityLevel.HIGH: 1000000000
    }

    def __init__(self, test_id):
        super().__init__()
        self.intensity = IntensityLevel(test_id).name
        self.number = self.numbers[test_id]

    def run(self):
        """
        Runs an intensive task based on the intensity level
        :return:
        """
        #print(f"Doing a {self.intensity} intensive task. ID: {self.native_id}")

        for i in range(self.number):
            continue

        # print("Done doing some intensive task")

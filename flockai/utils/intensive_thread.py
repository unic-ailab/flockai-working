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

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Runs an intensive task based on the intensity level
        :return:
        """
        with open("intensive_output.txt", 'w') as f:
            for i in range(10000):
                f.write(str("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"))

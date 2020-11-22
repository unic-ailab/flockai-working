import random
import string


class StringGenerator:
    @staticmethod
    def get_random_message(length: int) -> str:
        """
        Returns a random message based on the length requested
        :param length: The length of the random message
        :return:
        """
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

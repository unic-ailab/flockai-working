
from flockai.interfaces.sensor import ISensor


class TemperatureSensor(ISensor):

    def __init__(self, file):
        super().__init__(file)
        self.temperatureHigh = float('-inf')
        self.temperatureLow = float('inf')
        self.cum_sum = 0
        self.entries = 0

    def get_values(self):
        data = self._get_data()
        temperature = float(data)
        self.entries += 1
        self.cum_sum += temperature
        temperature_avg = self.cum_sum / self.entries
        self.temperatureHigh = max(temperature, self.temperatureHigh)
        self.temperatureLow = min(temperature, self.temperatureLow)

        return self.temperatureHigh, self.temperatureLow, temperature_avg



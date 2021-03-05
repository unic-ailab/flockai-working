from flockai.interfaces.sensor import ISensor


class HumiditySensor(ISensor):
    def __init__(self, file):
        super().__init__(file)
        self.humidityHigh = 0
        self.humidityLow = 100
        self.cum_sum = 0
        self.entries = 0

    def get_values(self):
        data = self._get_data()
        humidity = float(data)
        self.entries += 1
        self.cum_sum += humidity
        humidity_avg = self.cum_sum / self.entries
        self.humidityHigh = max(humidity, self.humidityHigh)
        self.humidityLow = min(humidity, self.humidityLow)

        return self.humidityHigh, self.humidityLow, humidity_avg

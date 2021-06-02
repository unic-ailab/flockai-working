
class Battery:
    DJI_CAPACITY = 3850  # mAh
    DJI_VOLTAGE = 15.4  # V
    DJI_ENERGY = 59.29  # Wh
    DJI_MAX_FLIGHT_TIME = 31 * 60  # seconds
    DJI_MAX_HOVERING_TIME = 29 * 60  # seconds
    DJI_SAFE_LANDING_PERCENTAGE = 0.1  # percentage

    def __init__(self):
        self.capacity = 0
        self.voltage = 0
        self.energy = 0
        self.max_flight_time = 0
        self.max_hover_time = 0
        self.safe_landing_percentage = 0


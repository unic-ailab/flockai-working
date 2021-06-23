
class Battery:
    DJI_CHARGE_CAPACITY = 3850  # mAh
    DJI_VOLTAGE = 15.4  # V
    DJI_ENERGY_CAPACITY = 59.29 * 3600  # W
    DJI_MAX_FLIGHT_TIME = 31 * 60  # seconds
    DJI_MAX_HOVERING_TIME = 29 * 60  # seconds
    DJI_SAFE_LANDING_PERCENTAGE = 0.1  # percentage

    def __init__(self):
        self.charge_capacity = 0
        self.voltage = 0
        self.energy_capacity = 0
        self.max_flight_time = 0
        self.max_hover_time = 0
        self.safe_landing_percentage = 0
        self.remaining_energy_percentage = 1.0


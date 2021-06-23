from flockai.interfaces.energy import IEnergy


class MotorEnergy(IEnergy):
    """
    Energy used to operate motors. Ie. Electrical Motors, Propellers...
    """
    def __init__(self):
        self.e_takeoff = 0  # energy attributed to the drone lifted in the air till it enters a hovering state
        self.e_hover = 0  # energy attributed to keeping the drone in the air and is dependent to the air density and weight of the drone
        self.e_move = 0  # the kinetic energy required to set a drone in motion from a hovering state

        # Need to be defined
        self.p_hover = 0

    def calculate(self, hovering_time):
        self.e_hover = self.p_hover * hovering_time
        return {"e_hover": self.e_hover,
                "e_motor": self.e_hover + self.e_move + self.e_takeoff}

    def set(self, *args, **kwargs):
        pass


class CommunicationEnergy(IEnergy):
    """
    Energy used to operate communication devices
    """

    def __init__(self):
        self.e_transmit = 0  # energy attributed to transmit data
        self.t_transmit = 0  # time attributed to transmit data
        self.e_receive = 0   # energy attributed to receive data
        self.t_receive = 0   # energy attributed to receive data
        self.e_idle = 0      # energy attributed when idling
        self.t_idle = 0      # idle time

        # Need to define these
        self.p_transmit = 0
        self.p_receive = 0
        self.p_idle = 0

    def calculate(self, transmit_time, receive_time, idle_time):
        self.e_transmit = self.p_transmit * transmit_time
        self.e_receive = self.p_receive * receive_time
        self.e_idle = self.p_idle * idle_time

        return {"e_transmit": self.e_transmit,
                "e_receive": self.e_receive,
                "e_idle": self.e_idle,
                "e_comm": self.e_transmit + self.e_receive + self.e_idle}

    def set(self, *args, **kwargs):
        pass


class ProcessingEnergy(IEnergy):
    """
    Energy used for processing
    """
    def __init__(self):
        self.e_cpu_active = 0      # processor power in compute state
        self.t_cpu_active = 0      # cpu time
        self.e_cpu_io = 0       # processor power in I/O state
        self.t_cpu_io = 0       # I/O time
        self.e_cpu_peripheral = 0  # processor power driving peripheral sensing devices
        self.t_cpu_peripheral = 0  # peripheral usage time
        self.e_cpu_idle = 0     # processor power when idling
        self.t_cpu_idle = 0     # idle time
        self.e_fc = 0           # flight controller energy

        # Need to be defined
        self.p_fc = 0
        self.p_cpu_active = 0
        self.p_cpu_idle = 0
        self.p_cpu_io = 0
        self.p_cpu_peripheral = 0

    def calculate(self, cpu_time_active, flight_time, io_time):
        self.e_cpu_active = self.p_cpu_active * cpu_time_active
        self.e_cpu_idle = self.p_cpu_idle * (flight_time - cpu_time_active)
        self.e_fc = self.p_fc * (flight_time / 10)
        self.e_cpu_io = self.p_cpu_io * io_time

        return {"e_cpu_active": self.e_cpu_active,
                "e_cpu_idle": self.e_cpu_idle,
                "e_fc": self.e_fc,
                "e_cpu_io": self.e_cpu_io,
                "e_proc": self.e_cpu_active + self.e_cpu_idle + self.e_fc + self.e_cpu_io}

    def set(self, *args, **kwargs):
        pass


class Energy:
    # Comm
    P_COMM = 8.4
    P_IDLE = 4.2

    # Proc
    DJI_A3_FC = 8
    RASPBERRY_PI_4B_IDLE = 4
    RASPBERRY_PI_4B_ACTIVE = 8

    # Motor
    DJI_P_HOVER = 95.02

    def __init__(self):
        self.motor_energy = MotorEnergy()
        self.communication_energy = CommunicationEnergy()
        self.processing_energy = ProcessingEnergy()


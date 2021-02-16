from flockai.interfaces.energy import IEnergy


class MotorEnergy(IEnergy):
    """
    Energy used to operate motors. Ie. Electrical Motors, Propellers...
    """
    def __init__(self):
        self.take_off_energy = 0  # energy attributed to the drone lifted in the air till it enters a hovering state
        self.hover_energy = 0  # energy attributed to keeping the drone in the air and is dependent to the air density and weight of the drone
        self.move_energy = 0  # the kinetic energy required to set a drone in motion from a hovering state

    def calculate(self):
        return self.take_off_energy + \
               self.hover_energy + \
               self.move_energy

    def set(self, *args, **kwargs):
        pass


class CommunicationEnergy(IEnergy):
    """
    Energy used to operate communication devices
    """

    def __init__(self):
        self.p_transmit = 0  # energy attributed to transmit data
        self.t_transmit = 0  # time attributed to transmit data
        self.p_receive = 0   # energy attributed to receive data
        self.t_receive = 0   # energy attributed to receive data
        self.p_idle = 0      # energy attributed when idling
        self.t_idle = 0      # idle time

    def calculate(self):
        return self.p_transmit * self.t_transmit + \
               self.p_receive * self.t_receive + \
               self.p_idle * self.t_idle

    def set(self, p_transmit=0, p_receive=0, p_idle=0):
        self.p_transmit = p_transmit
        self.p_receive = p_receive
        self.p_idle = p_idle


class ProcessingEnergy(IEnergy):
    """
    Energy used for processing
    """
    def __init__(self):
        self.p_active = 0      # processor power in compute state
        self.t_active = 0      # cpu time
        self.p_io = 0       # processor power in I/O state
        self.t_io = 0       # I/O time
        self.p_peripheral = 0  # processor power driving peripheral sensing devices
        self.t_peripheral = 0  # peripheral usage time
        self.p_idle = 0     # processor power when idling
        self.t_idle = 0     # idle time

    def calculate(self):
        return self.p_active * self.t_active + \
               self.p_io * self.t_io + \
               self.p_peripheral * self.t_peripheral + \
               self.p_idle * self.t_idle

    def set(self, p_active=0, p_io=0, p_peripheral=0, p_idle=0):
        self.p_active = p_active
        self.p_io = p_io
        self.p_peripheral = p_peripheral
        self.p_idle = p_idle


class Energy:
    def __init__(self):
        self.motor_energy = MotorEnergy()
        self.communication_energy = CommunicationEnergy()
        self.processing_energy = ProcessingEnergy()


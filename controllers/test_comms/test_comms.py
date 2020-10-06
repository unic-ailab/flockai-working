from controller import Robot, Emitter, Receiver
import random
import string


"""
Some custom code
"""
def get_random_message(length: int) -> str:
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


"""
Code running on the Drone
Note: This drone has an emitter and receiver device attached to it
"""
class Drone(Robot):
    # Made it 1 sec so I can analyze the logs
    timeStep = 1000 
    
    def __init__(self):
        super(Drone, self).__init__()
        
        # Set name
        self.name = self.getName()
        # Start emitter device
        self.emitter: Emitter = self.getEmitter('emitter')
        # Start receiver device
        self.receiver: Receiver = self.getReceiver('receiver')
        self.receiver.enable(self.timeStep)
        
    def run(self):
        """
        Bidirectional communication
        """
        while True:
               
            # Send messages
            random_message = get_random_message(4)
            self.send_message(random_message)    
            # Receive messages
            self.receive_messages()
            # Important step to avoid crashing the simulation on exit event
            if self.step(self.timeStep) == -1:
                break
    
    def send_message(self, message):    
        print(f'{self.name}: I am sending {message}')
        self.emitter.send(message.encode('utf-8'))
        
    def receive_messages(self):
        while self.receiver.getQueueLength() > 0:
            message_received = self.receiver.getData().decode('utf-8')
            print(f'{self.name}: I have received this message {message_received}')
            self.receiver.nextPacket()

# Create drone instance and run its controller
controller = Drone()
controller.run() 

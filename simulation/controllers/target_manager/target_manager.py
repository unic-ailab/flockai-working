import json

from controller import Supervisor, Receiver
import sys

supervisor = Supervisor()
target_objects = ["TARGET1", "TARGET2", "TARGET3"]
current_target_id = 0


def load_target(target_id):
    target_object = supervisor.getFromDef(target_objects[target_id])
    if target_object is None:
        sys.stderr.write(f"No DEF {target_objects[target_id]} node found in the current world file\n")
        sys.exit(1)
    return target_object


def set_visibility_status(t, status: float):
    visibility_field = t.getField("radarCrossSection")
    visibility_field.setSFFloat(status)


def change_target():
    global current_target_id

    # make old target invisible
    old_target = load_target(current_target_id)
    set_visibility_status(old_target, 0)

    # change to new target
    current_target_id = (current_target_id + 1) % len(target_objects)
    new_target = load_target(current_target_id)

    # set new target as visible
    set_visibility_status(new_target, 1)


# Enable receiver
receiver: Receiver = supervisor.getDevice('receiver')
receiver.enable(32)

# Initialize first target
target = load_target(current_target_id)
set_visibility_status(target, 1)

# Set target changing safeguard
last_change = -1
while supervisor.step(32) != -1:
    while receiver.getQueueLength() > 0:
        message = receiver.getData().decode('utf-8')
        print('received a message', message)
        if message == 'DESTINATION_ARRIVED':
            if supervisor.getTime() - last_change > 2:
                print('changing target')
                change_target()
                last_change = supervisor.getTime()
            else:
                print('ignore message')
        receiver.nextPacket()


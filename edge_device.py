import time
from random import randint

from models.WtkEdgeDevice import WtkEdgeDevice

cpid = 'avtds'
env = 'avnetpoc'
uniqueid = "EdgeExmple2"

device1 = WtkEdgeDevice(cpid, uniqueid, env)
device1.connect()

uniqueid = "EdgeExmple3"
device2 = WtkEdgeDevice(cpid, uniqueid, env)
device2.connect()
device2.power = 1

devices = [device1, device2]

# exit()
while True:
    print("\nCycle:")
    for m_device in devices:
        delta = randint(-10, -2)
        if m_device.power:
            delta = randint(2, 12)
        if 0 < (m_device.level + delta) < 100:
            m_device.level += delta

        data_sent = m_device.send_device_states()
        print("sending data")  # , data_sent)

    time.sleep(55)

'''
    Basic sample loading credentials from file and sending data to endpoint
'''
import time
from models.demo_edge_device import DemoEdgeDevice

CREDENTIALS_PATH = "credentials.json"

def main():
    '''Main function'''
    device = DemoEdgeDevice(CREDENTIALS_PATH)
    device.connect()

    while not device.needs_exit:
        device.update_local_state()
        print("sending data")
        device.send_device_states()

        time.sleep(10)


    print("APP EXIT")

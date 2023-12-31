'''
    Basic sample loading credentials from file and sending data to endpoint
'''
import time
from models.demo_edge_device import DemoEdgeDevice

# Relative Path is in respect from main.py
CREDENTIALS_PATH = "./primary/credentials.json"

def main():
    '''Main function'''
    device = DemoEdgeDevice(CREDENTIALS_PATH)
    device.connect()

    while True:
        if device.needs_exit and not device.in_ota:
            break

        device.update_local_state()
        print("sending data")
        device.send_device_states()

        time.sleep(10)


    print("APP EXIT")

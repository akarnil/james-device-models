'''
    Basic sample loading credentials from file and sending data to endpoint
'''
import time
from models.demo_edge_device import demo_edge_device
from credential_parser import parse_json_for_config

CREDENTIALS_PATH = "credentials.json"

def main():
    '''Main function'''
    credentials = parse_json_for_config(CREDENTIALS_PATH)
    device = demo_edge_device(credentials)
    device.connect()

    while not device.needs_exit:
        device.update()
        print("sending data")
        device.send_device_states()

        time.sleep(10)


    print("APP EXIT")

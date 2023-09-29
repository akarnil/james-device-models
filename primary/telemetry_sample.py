from datetime import datetime
import time
import random

from models.demo_edge_device import demo_edge_device

import json

import os
import sys


unique_id = "linuxPythonDemo"
sdk_id = "Yjg5MmMzNThlMzc1NGNjMzg4NDEzMmUyNzFlMjYxNTE=UDI6MDM6NzAuMTQ="
company_id = 'avtds'
environment = 'avnetpoc'
sdk_options = {
    "devicePrimaryKey":"MWRjP0I1fWQmPEU7XWl5VmhWcnlWTj9VSTxJ"
}


def main():
    device = demo_edge_device(company_id, unique_id, environment, sdk_id, sdk_options)
    device.connect()

    # # uncomment if you want an ota call without using the endpoint, will fail during the process but it allows most of it to execute
    #
    # msg_raw = '{"v": "2.1", "ct": 1, "cmd": "ota", "ack": "eddd3dc2-510b-4452-900a-fd066c5e3b00", "sw": "3", "hw": "1", "urls": [{"url": "https://pociotconnectblobstorage.blob.core.windows.net/firmware/FE285043-EEFA-4201-9B84-50F7822774AD.gz?sv=2018-03-28&sr=b&sig=F6xYdk0zT4SMQetEqRO1gXCAPndGwQ4XS0r7PCU32H0%3D&se=2023-09-28T11%3A34%3A42Z&sp=r", "fileName": "FE285043-EEFA-4201-9B84-50F7822774AD.gz"}]}'
    # msg = json.loads(msg_raw)
    # print(json.dumps(msg))
    # device.ota_cb(msg)

    # try:
    #     while device.needs_exit == False:
    #         data = device.generate_d2c_data(generate_dummy_data())
    #         device.send_d2c(data)
    #         print("sending data")  # , data_sent)
    #         time.sleep(30)

    # except KeyboardInterrupt:
    #     print ("Keyboard Interrupt Exception")
    #     os.abort()
    # except Exception as ex:
    #     print(ex.message)
    #     sys.exit(0)   

    while not device.needs_exit:
        device.update()
        print("sending data")  # , data_sent)
        device.send_device_states()
        
        time.sleep(30)


    print("APP EXIT")
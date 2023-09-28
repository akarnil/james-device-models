from datetime import datetime
import time
import random

from models.demo_edge_device import demo_edge_device

import json


unique_id = "linuxPythonDemo"
sdk_id = "Yjg5MmMzNThlMzc1NGNjMzg4NDEzMmUyNzFlMjYxNTE=UDI6MDM6NzAuMTQ="
company_id = 'avtds'
environment = 'avnetpoc'
sdk_options = {
    "devicePrimaryKey":"MWRjP0I1fWQmPEU7XWl5VmhWcnlWTj9VSTxJ"
}

def generate_dummy_data():
    data = {
    "temperature":random.randint(30, 50),
    "long1":random.randint(6000, 9000),
    "integer1": random.randint(100, 200),
    "decimal1":random.uniform(10.5, 75.5),
    "date1":datetime.utcnow().strftime("%Y-%m-%d"),
    "time1":"11:55:22",
    "bit1":1,
    "string1":"red",
    "datetime1":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }
    return data


device = demo_edge_device(company_id, unique_id, environment, sdk_id, sdk_options)
device.connect()

msg_raw = '{"v": "2.1", "ct": 1, "cmd": "ota", "ack": "eddd3dc2-510b-4452-900a-fd066c5e3b00", "sw": "3", "hw": "1", "urls": [{"url": "https://pociotconnectblobstorage.blob.core.windows.net/firmware/FE285043-EEFA-4201-9B84-50F7822774AD.gz?sv=2018-03-28&sr=b&sig=F6xYdk0zT4SMQetEqRO1gXCAPndGwQ4XS0r7PCU32H0%3D&se=2023-09-28T11%3A34%3A42Z&sp=r", "fileName": "FE285043-EEFA-4201-9B84-50F7822774AD.gz"}]}'
msg = json.loads(msg_raw)
print(json.dumps(msg))
device.ota_cb(msg)

while device.needs_exit == False:
    data = device.generate_d2c_data(generate_dummy_data())
    device.send_d2c(data)
    print("sending data")  # , data_sent)
    
    time.sleep(10)

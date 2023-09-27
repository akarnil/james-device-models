from datetime import datetime
import time
import random

from models.otaDemoDevice import otaDemoDevice


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


device = otaDemoDevice(company_id, unique_id, environment, sdk_id, sdk_options)
device.connect()

while device.needs_exit == False:
    data = device.generate_d2c_data(generate_dummy_data())
    device.send_d2c(data)
    print("sending data")  # , data_sent)
    
    time.sleep(10)

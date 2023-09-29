import requests

try:
    from models.device_model import ConnectedDevice
except:
    from device_model import ConnectedDevice

import sys
sys.path.append("iotconnect")
from iotconnect import IoTConnectSDK as SdkClient

import json


def whoami():
    import sys
    return sys._getframe(1).f_code.co_name

from models.api import api21 as api
from models.ota_handler import OtaHandler

import random
from datetime import datetime


class demo_edge_device(ConnectedDevice):
    api_ver = 2.1
    template = "wkjb220907"

    #sensor data
    time1 = "11:55:22"
    bit1 = 1
    string1 = "red"
    temperature = None
    long1 = None
    integer1 = None
    decimal1 = None
    date1 = None
    datetime1 = None

    def __init__(self, company_id, unique_id, environment, sdk_id, sdk_options=None):
        super().__init__(company_id, unique_id, environment, sdk_id, sdk_options)

    def connect(self):
        super().connect()
#        self.SdkClient.regiter_directmethod_callback("emergency", self.emergency_cb)

    def update(self):
        self.temperature = random.randint(30, 50)
        self.long1 = random.randint(6000, 9000)
        self.integer1 = random.randint(100, 200)
        self.decimal1 = random.uniform(10.5, 75.5)
        self.date1 = datetime.utcnow().strftime("%Y-%m-%d")
        self.datetime1 = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def get_state(self):
        # returns the current state of device
        data_obj = {
            "temperature": self.temperature,
            "long1": self.long1,
            "integer1": self.integer1,
            "decimal1": self.decimal1,
            "date1": self.date1,
            "time1": self.time1,
            "bit1": self.bit1,
            "string1": self.string1,
            "datetime1": self.datetime1
        }
        return data_obj


    def emergency_cb(self, msg, request_id):
        print("direct method CB on template {}".format(self.template))
        print(msg)
        print(request_id)
        self.direct_message_ack(request_id, {"fire": False})

    def get_state(self):
        data_array = {
            "level": self.level,
            "power": self.power
        }
        return data_array
    
    def get_command_type(self,msg):
        return self.api_enums.get_command_enum(msg)
    
    
    def ota_cb(self,msg):
        OtaHandler(self,msg)

    def send_ack(self, data, status, message, child_id = None):
        key = api.Keys.ack.value
        self.SdkClient.sendAckCmd(data[key],status.value,message, child_id)

    # def send_ack_if_needed(self,msg):
        
    #     if "ack" i n 
    #         if msg['ack'] == "True":
    #     print_msg("ack message", msg)
    #     d2c_msg = {
    #         "ackId": msg["ackId"],
    #         "st": status,
    #         "msg": "",
    #         "childId": ""
    #     }
    #     self.SdkClient.SendACK(d2c_msg, 5)  # 5 : command acknowledgement

    def device_cb(self,msg):
        print("device callback received")

        
        if (command_type := self.api_enums.get_command_enum(msg)) != None:      
            child_id_to_send = self.api_enums.get_value_from_key(msg, api.Keys.id)
            
            if command_type == self.api_enums.Commands.DCOMM:
                # do something cool here
                self.send_ack(msg,self.api_enums.AckStat.SUCCESS, "SUCCESS", child_id_to_send) # need to check if ack has been requested then send it
                

            if command_type == self.api_enums.Commands.is_connect:
                print("connection status is " + msg["command"])

            else:
                print(whoami() + " got sent command_type     " + command_type.name)
            return

        print("callback received not valid")
        print("rule command",msg)

    def device_command(self, msg):
        command = msg['command'].split(' ')
        if command[0] == "setPower":
            self.power = int(command[1])  # == '1')
            print("self.power = {}".format(self.power))
            status = 6  # 6 = command success
            return status

    def firmware_command(self, msg):
        print("firmware\nhw: {}, sw: {}, {} urls".format(msg["ver"]["hw"], msg["ver"]["sw"], len(msg["urls"])))
        status = 1
        for url in msg["urls"]:
            result = requests.get(url["url"])
            print(result.text)
        return status

    def twin_update_cb(self, msg):
        super().twin_update_cb(msg)
        self.twin = msg["desired"]["twin"]
        print("self.twin = {}".format(self.twin))

    def for_iotconnect_upload(self):
        export_dict = super().for_iotconnect_upload()
        export_dict["properties"] = [
            {
                "key": "level",
                "value": self.level
            },
            {
                "key": "power",
                "value": self.power
            }
        ]
        return export_dict


if __name__ == "__main__":
    pass
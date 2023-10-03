import requests

from models.device_model import ConnectedDevice

import sys
sys.path.append("iotconnect")
from iotconnect import IoTConnectSDK as SdkClient

import json

from enum import Enum
from models.enums import Enums as e

def whoami():
    import sys
    return sys._getframe(1).f_code.co_name

from models.ota_handler import OtaHandler

import random
from datetime import datetime
from typing import Union # to use Union[Enum, None] type hint



class demo_edge_device(ConnectedDevice):
    attributes = []
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

    class DeviceCommands(Enum):
        ECHO:str = "echo "
        LED:str = "led "

    def __init__(self, company_id, unique_id, environment, sdk_id, sdk_options=None):
        super().__init__(company_id, unique_id, environment, sdk_id, sdk_options)

    def __init__(self, credentials):
        super().__init__(credentials["company_id"], credentials["unique_id"], credentials["environment"], credentials["sdk_id"], credentials["sdk_options"])
        self.api_ver = credentials["message_version"]
        self.attributes = credentials["attributes"]

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

        
    def ota_cb(self,msg):
        OtaHandler(self,msg)


    def device_cb(self,msg):
        print("device callback received")

        # check command type got from message
        if (command_type := e.get_command_type(msg)) is not None:
            if command_type == e.Values.Commands.DCOMM:
                # do something cool here
                self.device_command(msg)

            if command_type == e.Values.Commands.is_connect:
                print("connection status is " + msg["command"])

            else:
                print(whoami() + " got sent command_type     " + command_type.name)
            return

        print("callback received not valid")
        print("rule command",msg)

    def get_device_command(self, full_command:str) -> Union[Enum, None]:
        command_enum = None
        if full_command is not None:
            for dc in self.DeviceCommands:
                dc = dc.value
                if (sliced := full_command[:len(dc)]) == dc:
                    command_enum = self.DeviceCommands(sliced)
                    break
        return command_enum

    def device_command(self, msg):
        full_command = e.get_value_using_key(msg, e.Keys.device_command)
        command_enum = self.get_device_command(full_command)

        if command_enum == self.DeviceCommands.ECHO:
            to_print = full_command[len(self.DeviceCommands.ECHO.value):]
            print(to_print)
            self.send_ack(msg,e.Values.AckStat.SUCCESS, "Command Executed Successfully")


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
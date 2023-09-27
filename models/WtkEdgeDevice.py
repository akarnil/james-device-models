import requests

from models.device_model import *


class WtkEdgeDevice(ConnectedDevice):
    template = "wkjb220907"
    # Min, Max, Sum, Average, Latest Value
    # attributes
    level = 0
    power = 0

    # twin properties
    sw_version = "5.5"
    upTime = 0
    twin = ""

    def __init__(self, cp_id, unique_id, environment, sdk_options=None):
        super().__init__(cp_id, unique_id, environment, sdk_options)

    def connect(self):
        super().connect()
        self.SdkClient.regiter_directmethod_callback("emergency", self.emergency_cb)

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

    def device_cb(self, msg, status=None):
        print("device callback")
        if msg["cmdType"] == self.CMD_TYPE_DEVICE:
            status = self.device_command(msg)
        elif msg["cmdType"] == self.CMD_TYPE_FIRMWARE:
            status = self.firmware_command(msg)
        super().device_cb(msg, status)

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

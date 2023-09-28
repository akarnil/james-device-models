import requests

from models.device_model import ConnectedDevice

import sys
sys.path.append("iotconnect")
from iotconnect import IoTConnectSDK as SdkClient


def whoami():
    import sys
    return sys._getframe(1).f_code.co_name



class otaDemoDevice(ConnectedDevice):
    api_ver = 2.1
    needs_exit:bool = False

    template = "wkjb220907"
    # Min, Max, Sum, Average, Latest Value
    # attributes
    level = 0
    power = 0

    # twin properties
    sw_version = "5.5"
    upTime = 0
    twin = ""

    def __init__(self, company_id, unique_id, environment, sdk_id, sdk_options=None):
        super().__init__(company_id, unique_id, environment, sdk_id, sdk_options)

    def connect(self):
        super().connect()
#        self.SdkClient.regiter_directmethod_callback("emergency", self.emergency_cb)


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
        pass
        # print("device callback received")
        # command_type_got = None
        # if "ct" in msg:
        #     if msg["ct"] in CommandType._value2member_map_:
        #         command_type_got = CommandType(msg["ct"])

        # if command_type_got != None:        
        #     child_id_to_send = None
        #     if "id" in msg:
        #         child_id_to_send = msg["id"]

        #     if command_type_got == CommandType.DCOMM:
        #         self.SdkClient.sendAckCmd(msg["ack"], ackCmdStatus.SUCCESS, "Sending SUCCESSFUL", child_id_to_send)

        #     if command_type_got == CommandType.is_connect:
        #         print("connection status is " + msg["command"])

        #     else:
        #         print(whoami() + " got sent command_type     " + command_type_got.name)
        #     return

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

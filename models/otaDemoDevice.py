import requests

from models.device_model import ConnectedDevice

import sys
sys.path.append("iotconnect")
from iotconnect import IoTConnectSDK as SdkClient


def whoami():
    import sys
    return sys._getframe(1).f_code.co_name

from enum import Enum

# 2.1 enums
class ackCmdStatus(Enum):
    FAIL = 4,
    EXECUTED = 5,
    SUCCESS = 7,
    EXECUTED_ACK = 6 # what is the difference between this and EXECUTED??

class MessageType(Enum):
    RPT = 0
    FLT = 1
    RPTEDGE = 2
    RMEdge = 3
    LOG = 4
    ACK = 5
    OTA = 6
    FIRMWARE = 11

class ErrorCode(Enum):
    OK = 0
    DEV_NOT_REG = 1
    AUTO_REG = 2
    DEV_NOT_FOUND = 3
    DEV_INACTIVE = 4
    OBJ_MOVED = 5
    CPID_NOT_FOUND = 6

class CommandType(Enum):
    DCOMM = 0
    FIRMWARE = 1
    MODULE = 2
    U_ATTRIBUTE = 101
    U_SETTING = 102
    U_RULE = 103
    U_DEVICE = 104
    DATA_FRQ = 105
    U_barred = 106
    D_Disabled = 107
    D_Released = 108
    STOP = 109
    Start_Hr_beat = 110
    Stop_Hr_beat = 111
    is_connect = 116
    SYNC = "sync"
    RESETPWD = "resetpwd"
    UCART = "updatecrt"

class Option(Enum):
    attribute = "att"
    setting = "set"
    protocol = "p"
    device = "d"
    sdkConfig = "sc"
    rule = "r"

class DataType(Enum):
    INT = 1
    LONG = 2
    FLOAT = 3
    STRING = 4
    Time = 5
    Date = 6
    DateTime = 7
    BIT = 8
    Boolean = 9
    LatLong = 10
    OBJECT = 11

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

    def device_cb(self,msg):
        print("device callback received")
        command_type_got = None
        if "ct" in msg:
            if msg["ct"] in CommandType._value2member_map_:
                command_type_got = CommandType(msg["ct"])

        if command_type_got != None:        
            child_id_to_send = None
            if "id" in msg:
                child_id_to_send = msg["id"]

            if command_type_got == CommandType.DCOMM:
                self.SdkClient.sendAckCmd(msg["ack"], ackCmdStatus.SUCCESS, "Sending SUCCESSFUL", child_id_to_send)
            else:
                print(whoami() + " got sent command_type     " + command_type_got.name)
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

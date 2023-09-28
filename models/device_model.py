import json
from datetime import datetime

# only to use a local copy of the SDK remove for release
import sys
sys.path.append("iotconnect")
# remove for release
from iotconnect import IoTConnectSDK

class api21:
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

    class CommandTypes(Enum):
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

    class msg_fields(str, Enum):
        ack = 'ack'
        command_type = 'ct'

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

    @classmethod
    def get_command_type(self, msg):
        ret = None
        ct = self.msg_fields.command_type
        if ct in msg:
            if msg[ct] in self.CommandTypes._value2member_map_:
                ret = self.CommandTypes(msg[ct])
        return ret



def print_msg(title, msg):
    print("{}: \n{}".format(title, json.dumps(msg, indent=2)))


class GenericDevice:
    template = None
    children = None
    """
    minimal device, no connectivity, has to be child device
    """
    def __init__(self, unique_id, tag=None):
        self.unique_id = unique_id
        self.name = unique_id
        self.tag = tag

    def for_iotconnect_upload(self):
        export_dict = {
            "name": self.name,
            "uniqueId": self.unique_id,
            "tag": self.tag,
            "properties": []
        }
        return export_dict

    def get_d2c_data(self):
        data_obj = [{
            "uniqueId": self.unique_id,
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "data": self.get_state()
        }]
        return data_obj
    
        
    def generate_d2c_data(self, data):
        data_obj = [{
            "uniqueId": self.unique_id,
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "data": data
        }]
        return data_obj

    def get_state(self):
        return {}


class ConnectedDevice(GenericDevice):

    CMD_TYPE_DEVICE = '0x01'
    CMD_TYPE_FIRMWARE = '0x02'
    CMD_TYPE_CONNECTION = '0x16'

    api_ver = 2.1
    api_enums = api21

    def __init__(self, company_id, unique_id, environment, sdk_id, sdk_options=None):
        super().__init__(unique_id)
        self.company_id = company_id
        self.environment = environment
        self.sdk_id = sdk_id
        self.SdkClient = None
        self.SdkOptions = sdk_options

    def connect(self):
        print("message version {}".format(self.api_ver))
        if self.api_ver == 2.1:
            # def __init__(self, uniqueId, sId, sdkOptions=None, initCallback=None)
            self.SdkClient = IoTConnectSDK(
                self.unique_id,
                self.sdk_id,
                self.SdkOptions,
                self.init_cb
            )
        else:
            # def __init__(self, cpId, uniqueId, listner, listner_twin, sdkOptions=None, env="PROD")
            self.SdkClient = IoTConnectSDK(
                self.company_id,
                self.unique_id,
                self.device_cb,
                self.twin_update_cb,
                self.SdkOptions,
                self.environment
            )


    def init_cb(self, msg):
        if self.api_enums.get_command_type(msg) == self.api_enums.CommandTypes.is_connect:
            print("connection status is " + msg["command"])

    def device_cb(self, msg, status=None):
        
        if status is None:
            print("device callback")
            print(json.dumps(msg, indent=2))
            command_type = msg['ct']

            if command_type == self.CMD_TYPE_DEVICE:
                print("device command cmdType")

            elif command_type == self.CMD_TYPE_FIRMWARE:
                print("firmware cmdType")

            elif command_type == self.CMD_TYPE_CONNECTION:
                # Device connection status e.g. data["command"] = true(connected) or false(disconnected)
                print("connection status cmdType")

            elif command_type == 116:
                print("connection status is " + msg["command"])

            else:
                print("unimplemented cmdType: {}".format(command_type))

            print_msg("message", msg)

        if msg['ack'] == "True":
            print_msg("ack message", msg)
            d2c_msg = {
                "ackId": msg["ackId"],
                "st": status,
                "msg": "",
                "childId": ""
            }
            self.SdkClient.SendACK(d2c_msg, 5)  # 5 : command acknowledgement



    def send_device_states(self):
        data_array = [self.get_d2c_data()]
        if self.children is not None:
            for child in self.children:
                data_array.append(child.get_d2c_data())
        self.send_d2c(data_array)
        return data_array

    def send_d2c(self, data):
        if self.SdkClient is not None:
            self.SdkClient.SendData(data)
        else:
            print("no client")

    def direct_message_ack(self, rId, data, status=200):
        return self.SdkClient.DirectMethodACK(data, status, rId)

    def get_twins(self):
        return self.SdkClient.GetAllTwins()

    def direct_method_cb(self, msg, rId):
        print("direct method CB on template {}".format(self.template))
        print(msg)
        print(rId)
        # DirectMethodACK(msg,status,requestId
        self.SdkClient.DirectMethodACK(msg, )

    def twin_update(self, key, value):
        print("twin update on {} template {}, {} = {}".format(self.unique_id, self.template, key, value))
        self.SdkClient.UpdateTwin(key, value)

    def twin_update_cb(self, msg):
        print_msg("twin update CB on {} template {}".format(self.unique_id, self.template), msg)

class Gateway(ConnectedDevice):
    children = []

    def show_children(self):
        if self.children.count:
            print("children")
            for child in self.children:
                print(child.unique_id)
        else:
            print("no children")

    def for_iotconnect_upload(self):
        export_dict = {
            "gateway": {
                "items": []
            }
        }
        for child in self.children:
            export_dict["gateway"]["items"].append(child.for_iotconnect_upload())
        return export_dict

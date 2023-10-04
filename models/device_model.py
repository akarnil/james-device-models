import json
from datetime import datetime

# only to use a local copy of the SDK remove for release
import sys
sys.path.append("iotconnect")
sys.path.append("/home/akarnil/Documents/Work/james-device-models/")

# remove for release
from iotconnect import IoTConnectSDK

from models.enums import Enums as e

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

    def get_state(self) -> dict:
        raise NotImplementedError()


class ConnectedDevice(GenericDevice):

    CMD_TYPE_DEVICE = '0x01'
    CMD_TYPE_FIRMWARE = '0x02'
    CMD_TYPE_CONNECTION = '0x16'

    # for now set to default to api21
    api_ver = 2.1

    needs_exit:bool = False

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
            self.SdkClient = IoTConnectSDK(
                uniqueId=self.unique_id,
                sId=self.sdk_id,
                # cpid=self.company_id,
                cpid=None, # remove this once they fix the SDK
                env=self.environment,
                sdkOptions=self.SdkOptions,
                initCallback=self.init_cb)
            self.bind_callbacks()
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

    def ota_cb(self,msg):
        raise NotImplementedError()

    def module_cb(self,msg):
        raise NotImplementedError()

    def twin_change_cb(self,msg):
        raise NotImplementedError()

    def attribute_change_cb(self,msg):
        raise NotImplementedError()

    def device_change_cb(self,msg):
        raise NotImplementedError()

    def rule_change_cb(self,msg):
        raise NotImplementedError()

    def init_cb(self, msg):
        if e.get_command_type(msg) is e.Values.Commands.is_connect:
            print("connection status is " + msg["command"])
        

    def device_cb(self, msg, status=None):
        pass
        # if status is None:
        #     print("device callback")
        #     print(json.dumps(msg, indent=2))
        #     command_type = msg['ct']

        #     if command_type == self.CMD_TYPE_DEVICE:
        #         print("device command cmdType")

        #     elif command_type == self.CMD_TYPE_FIRMWARE:
        #         print("firmware cmdType")

        #     elif command_type == self.CMD_TYPE_CONNECTION:
        #         # Device connection status e.g. data["command"] = true(connected) or false(disconnected)
        #         print("connection status cmdType")

        #     elif command_type == 116:
        #         print("connection status is " + msg["command"])

        #     else:
        #         print("unimplemented cmdType: {}".format(command_type))

        #     print_msg("message", msg)

        # if msg['ack'] == "True":
        #     print_msg("ack message", msg)
        #     d2c_msg = {
        #         "ackId": msg["ackId"],
        #         "st": status,
        #         "msg": "",
        #         "childId": ""
        #     }
        #     self.SdkClient.SendACK(d2c_msg, 5)  # 5 : command acknowledgement


    def bind_callbacks(self):
        self.SdkClient.onOTACommand(self.ota_cb)
        self.SdkClient.onModuleCommand(self.module_cb)
        self.SdkClient.onTwinChangeCommand(self.twin_change_cb)
        self.SdkClient.onAttrChangeCommand(self.attribute_change_cb)
        self.SdkClient.onDeviceChangeCommand(self.device_change_cb)
        self.SdkClient.onRuleChangeCommand(self.rule_change_cb)
        self.SdkClient.onDeviceCommand(self.device_cb)


    # there might overlaps with some of the call backs above and below, will need to check
    
    def send_device_states(self):
        data_array = [self.get_d2c_data()]
        if self.children is not None:
            for child in self.children:
                data_array.append(child.get_d2c_data())

        for data in data_array:
            self.send_d2c(data)
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

    # Either OTA or Standard, exits early if not requested
    def send_ack(self, msg, status: e.Values.AckStat, message):
        # check if ack exists in message 
        if not e.key_in_msg(msg, e.Keys.ack):
            print(" Ack not requested, returning")
            return
        
        id_to_send = e.get_value_using_key(msg, e.Keys.id)
        key_str = e.Keys.ack.value
        status_int = status.value

        if status.__class__ == e.Values.AckStat:
            self.SdkClient.sendAckCmd(msg[key_str], status_int ,message, id_to_send)
            return
        
        if status.__class__ == e.Values.OtaStat:
            self.SdkClient.sendOTAAckCmd(msg[key_str],status_int,message, id_to_send)
            return

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

import json
from datetime import datetime

# only to use a local copy of the SDK remove for release
import sys
sys.path.append("iotconnect")
# remove for release
from iotconnect import IoTConnectSDK



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

    def __init__(self, company_id, unique_id, environment, sdk_id, sdk_options=None):
        super().__init__(unique_id)
        self.company_id = company_id
        self.Env = environment
        self.S_id = sdk_id
        self.SdkClient = None
        self.SdkOptions = sdk_options

    def connect(self):
        self.SdkClient = IoTConnectSDK(
            self.unique_id,
            self.S_id,
            self.SdkOptions,
            self.twin_update_cb
        )

    def device_cb(self, msg, status=None):
        if status is None:
            print("device callback")
            if msg["cmdType"] == self.CMD_TYPE_DEVICE:
                print("device command cmdType")
            elif msg["cmdType"] == self.CMD_TYPE_FIRMWARE:
                print("firmware cmdType")

            elif msg["cmdType"] == self.CMD_TYPE_CONNECTION:
                # Device connection status e.g. data["command"] = true(connected) or false(disconnected)
                print("connection status cmdType")

            else:
                print("unimplemented cmdType: {}".format(msg["cmdType"]))

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

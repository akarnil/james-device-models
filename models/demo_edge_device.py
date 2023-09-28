import requests

try:
    from models.device_model import ConnectedDevice
except:
    from device_model import ConnectedDevice

import sys
sys.path.append("iotconnect")
from iotconnect import IoTConnectSDK as SdkClient

import json
import os
import tarfile
import shutil
from urllib.request import urlretrieve 

def whoami():
    import sys
    return sys._getframe(1).f_code.co_name

from models.api import api21 as api

from app_paths import app_paths

class demo_edge_device(ConnectedDevice):
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
    
    def get_command_type(self,msg):
        return self.api_enums.get_command_type(msg)
    
    def send_ota_ack(self, data, status, message):
        key = self.api_enums.msg_keys.ack
        self.SdkClient.sendOTAAckCmd(data[key],status,message)
    
    def ota_cb(self,msg):

        command_type_got = self.get_command_type(msg)
        if command_type_got != api.CommandTypes.FIRMWARE:
            print("fail wrong command type")
            return
        
        payload_valid: bool = False
        data: dict = msg
        
        if ("urls" in data) and len(data["urls"]) == 1:                
            if ("url" in data["urls"][0]) and ("fileName" in data["urls"][0]):
                if (data["urls"][0]["fileName"].endswith(".gz")):
                    payload_valid = True   

        if payload_valid is True:
            urls = data["urls"][0]    
            # download tarball from url to download_dir
            url: str = urls["url"]
            download_filename: str = urls["fileName"]
            final_folder_dest:str = app_paths["main_dir"] + app_paths["tarball_download_dir"]
            if os.path.exists(final_folder_dest) == False:
                os.mkdir(final_folder_dest)
            try:
                self.send_ota_ack(data, api.otaAcks.DL_IN_PROGRESS, "downloading payload")
                urlretrieve(url, final_folder_dest + download_filename)
            except:
                self.send_ota_ack(data, api.otaAcks.DL_FAILED, "payload dl failed")
                raise
            self.send_ota_ack(data, api.otaAcks.DL_DONE, "payload downloaded")
            
            self.needs_exit = False
            self.ota_backup_primary()
            try:
                self.ota_extract_to_a_and_move_old_a_to_b(download_filename)
                self.needs_exit = True
                self.ota_delete_primary_backup()
                self.send_ota_ack(data, api.otaAcks.SUCCESS, "OTA SUCCESS")
                return
            
            except:
                self.ota_restore_primary()
                self.send_ota_ack(data, api.otaAcks.FAILED, "OTA FAILED to install")
                self.needs_exit = False
                raise
            # if self.needs_exit:
            #     self.ota_delete_primary_backup()
            #     self.send_ota_ack(data, api.otaAcks.SUCCESS, "OTA SUCCESS")
            #     return
            
        self.send_ota_ack(data, api.otaAcks.FAILED, "OTA FAILED,invalid payload")

    def ota_extract_to_a_and_move_old_a_to_b(self,tarball_name:str):
        # extract tarball to new directory
        file = tarfile.open(app_paths["main_dir"] + app_paths["tarball_download_dir"] + tarball_name)
        file.extractall(app_paths["main_dir"] + app_paths["tarball_extract_dir"])
        file.close()

        # rm secondary dir
        path = app_paths["main_dir"] + app_paths["secondary_app_dir"]
        shutil.rmtree(path, ignore_errors=True)

        # move primary to secondary
        os.rename(app_paths["main_dir"] + app_paths["primary_app_dir"], app_paths["main_dir"] + app_paths["secondary_app_dir"])

        # copy extracted dir to primary dir
        src = app_paths["main_dir"] + app_paths["tarball_extract_dir"]
        dst = app_paths["main_dir"] + app_paths["primary_app_dir"]
        shutil.copytree(src, dst)

        # delete temp folders
        shutil.rmtree(app_paths["main_dir"] + app_paths["tarball_download_dir"], ignore_errors=True)
        shutil.rmtree(app_paths["main_dir"] + app_paths["tarball_extract_dir"], ignore_errors=True)

    def ota_backup_primary(self):
        src = app_paths["main_dir"] + app_paths["primary_app_dir"]
        dst = app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"]
        shutil.copytree(src, dst)

    def ota_restore_primary(self):
        shutil.rmtree(app_paths["main_dir"] + app_paths["primary_app_dir"], ignore_errors=True)
        os.rename(app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"], app_paths["main_dir"] + app_paths["primary_app_dir"])

    def ota_delete_primary_backup(self):
        shutil.rmtree(app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"], ignore_errors=True)


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

        
        command_type_got = self.api_enums.get_command_type(msg)
        if command_type_got != None:        
            child_id_to_send = None
            if "id" in msg:
                child_id_to_send = msg["id"]

            if command_type_got == self.api_enums.CommandTypes.DCOMM:
                # do something cool here
                self.SdkClient.sendAckCmd(msg["ack"], self.api_enums.ackCmdStatus.SUCCESS, "Sending SUCCESSFUL", child_id_to_send)

            if command_type_got == self.api_enums.CommandTypes.is_connect:
                print("connection status is " + msg["command"])

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


if __name__ == "__main__":
    pass
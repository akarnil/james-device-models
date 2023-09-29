from models.api import api21 as api
from app_paths import app_paths
from iotconnect import IoTConnectSDK
import json
import os
import tarfile
import shutil
from urllib.request import urlretrieve 

class OtaHandler:

    SdkClient: IoTConnectSDK = None

    def __init__(self, SdkClient: IoTConnectSDK, msg):
        self.SdkClient = SdkClient
        self.ota_perform_update(msg)

    def send_ota_ack(self, data, status:api.OtaStat, message):
        key = api.Keys.ack
        self.SdkClient.sendOTAAckCmd(data[key],status.value,message)
    
    def ota_perform_update(self,msg):

        if api.get_enum_from_key(msg,api.Keys.command_type) != api.Commands.FIRMWARE:
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
                self.send_ota_ack(data, api.OtaStat.DL_IN_PROGRESS, "downloading payload")
                urlretrieve(url, final_folder_dest + download_filename)
            except:
                self.send_ota_ack(data, api.OtaStat.DL_FAILED, "payload dl failed")
                raise
            self.send_ota_ack(data, api.OtaStat.DL_DONE, "payload downloaded")
            
            self.needs_exit = False
            self.ota_backup_primary()
            try:
                self.ota_extract_to_a_and_move_old_a_to_b(download_filename)
                self.needs_exit = True
            except:
                self.ota_restore_primary()
                self.send_ota_ack(data, api.OtaStat.FAILED, "OTA FAILED to install")
                self.needs_exit = False
                raise

            if self.needs_exit:
                self.ota_delete_primary_backup()
                self.send_ota_ack(data, api.OtaStat.SUCCESS, "OTA SUCCESS")
                return
            
        self.send_ota_ack(data, api.OtaStat.FAILED, "OTA FAILED,invalid payload")

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

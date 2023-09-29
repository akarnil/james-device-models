from models.api import api21 as api
from app_paths import app_paths
import json
import os
import tarfile
import shutil
from urllib.request import urlretrieve
from models.device_model import ConnectedDevice


class OtaHandler:
    d: ConnectedDevice = None
    e: api = None

    def __init__(self, connected_device: ConnectedDevice, msg):
        self.d = connected_device
        self.e = self.d.api_enums
        self.ota_perform_update(msg)

    def send_ota_ack(self, data, status:api.OtaStat, message):
        key = self.e.Keys.ack
        self.d.SdkClient.sendOTAAckCmd(data[key],status.value,message)
        
    
    def ota_perform_update(self,msg):
        if self.e.get_enum_using_key(msg, self.e.Keys.command_type) != self.e.Commands.FIRMWARE:
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
                self.send_ota_ack(data, self.e.OtaStat.DL_IN_PROGRESS, "downloading payload")
                urlretrieve(url, final_folder_dest + download_filename)
            except:
                self.send_ota_ack(data, self.e.OtaStat.DL_FAILED, "payload dl failed")
                raise
            self.send_ota_ack(data, self.e.OtaStat.DL_DONE, "payload downloaded")
            
            self.d.needs_exit  = False
            self.ota_backup_primary()
            try:
                self.ota_extract_to_a_and_move_old_a_to_b(download_filename)
                self.d.needs_exit  = True
            except:
                self.ota_restore_primary()
                self.send_ota_ack(data, self.e.OtaStat.FAILED, "OTA FAILED to install")
                self.d.needs_exit  = False
                raise

            if self.d.needs_exit:
                self.ota_delete_primary_backup()
                self.send_ota_ack(data, self.e.OtaStat.SUCCESS, "OTA SUCCESS")
                return
            
        self.send_ota_ack(data, self.e.OtaStat.FAILED, "OTA FAILED,invalid payload")

    @staticmethod
    def ota_extract_to_a_and_move_old_a_to_b(tarball_name:str):
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

    @staticmethod
    def ota_backup_primary():
        src = app_paths["main_dir"] + app_paths["primary_app_dir"]
        dst = app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"]
        shutil.copytree(src, dst)

    @staticmethod
    def ota_restore_primary():
        shutil.rmtree(app_paths["main_dir"] + app_paths["primary_app_dir"], ignore_errors=True)
        os.rename(app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"], app_paths["main_dir"] + app_paths["primary_app_dir"])

    @staticmethod
    def ota_delete_primary_backup():
        shutil.rmtree(app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"], ignore_errors=True)

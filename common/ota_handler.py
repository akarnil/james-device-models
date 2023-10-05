'''
    Module handling OTA update functionality
'''
import os
import tarfile
import shutil
from urllib.request import urlretrieve
from models.device_model import ConnectedDevice

from common.enums import Enums as e
from common.app_paths import AppPaths as AP


# OTA payload must be a single file of extension .tar.gz
# the updated application .py file  must be called the same
# as a previous version otherwise it will not load, refer to AP.app_name

# OTA payload will replace entire contents of primary folder with contents of payload


class OtaHandler:
    '''Class for handling OTA'''
    d: ConnectedDevice = None

    def __init__(self, connected_device: ConnectedDevice, msg):
        self.d = connected_device
        self.d.in_ota = True
        self.ota_perform_update(msg)

    def __del__(self):
        self.d.in_ota = False

    def ota_perform_update(self,msg):

        """Perform OTA logic"""
        if e.get_command_type(msg) != e.Values.Commands.FIRMWARE:
            print("fail wrong command type")
            return

        payload_valid: bool = False
        data: dict = msg

        if ("urls" in data) and len(data["urls"]) == 1:
            if ("url" in data["urls"][0]) and ("fileName" in data["urls"][0]):
                if data["urls"][0]["fileName"].endswith(".gz"):
                    payload_valid = True

        if payload_valid is True:
            urls = data["urls"][0]
            # download tarball from url to download_dir
            url: str = urls["url"]
            download_filename: str = urls["fileName"]
            final_folder_dest:str = AP.main_app_dir + AP.tarball_download_dir
            if not os.path.exists(final_folder_dest):
                os.mkdir(final_folder_dest)
            try:
                self.d.send_ack(data, e.Values.OtaStat.DL_IN_PROGRESS, "downloading payload")
                urlretrieve(url, final_folder_dest + download_filename)
            except:
                self.d.send_ack(data, e.Values.OtaStat.DL_FAILED, "payload dl failed")
                raise
            self.d.send_ack(data, e.Values.OtaStat.DL_DONE, "payload downloaded")

            self.d.needs_exit  = False
            self.ota_backup_primary()
            try:
                self.ota_extract_to_a_and_move_old_a_to_b(download_filename)
                self.d.needs_exit  = True
            except:
                self.ota_restore_primary()
                self.d.send_ack(data, e.Values.OtaStat.FAILED, "OTA FAILED to install")
                self.d.needs_exit  = False
                raise

            if self.d.needs_exit:
                self.ota_delete_primary_backup()
                self.d.send_ack(data, e.Values.OtaStat.SUCCESS, "OTA SUCCESS")
                return

        self.d.send_ack(data, e.Values.OtaStat.FAILED, "OTA FAILED,invalid payload")

    @staticmethod
    def ota_extract_to_a_and_move_old_a_to_b(tarball_name:str):
        """Extract OTA tarball and assign to primary, move old primary to secondary"""
        # extract tarball to new directory
        file = tarfile.open(AP.main_app_dir + AP.tarball_download_dir + tarball_name)
        file.extractall(AP.main_app_dir + AP.tarball_extract_dir)
        file.close()

        # rm secondary dir
        path = AP.main_app_dir + AP.secondary_app_dir
        shutil.rmtree(path, ignore_errors=True)

        # move primary to secondary
        os.rename(AP.main_app_dir + AP.primary_app_dir, AP.main_app_dir + AP.secondary_app_dir)

        # copy extracted dir to primary dir
        src = AP.main_app_dir + AP.tarball_extract_dir
        dst = AP.main_app_dir + AP.primary_app_dir
        shutil.copytree(src, dst)

        # delete temp folders
        shutil.rmtree(AP.main_app_dir + AP.tarball_download_dir, ignore_errors=True)
        shutil.rmtree(AP.main_app_dir + AP.tarball_extract_dir, ignore_errors=True)

    @staticmethod
    def ota_backup_primary():
        """Copy primary app folder for backup"""
        src = AP.main_app_dir + AP.primary_app_dir
        dst = AP.main_app_dir + AP.primary_app_backup_folder_name

        if os.path.exists(dst):
            shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)

    @staticmethod
    def ota_restore_primary():
        """Delete faulty primary app folder and replace with backup"""
        shutil.rmtree(AP.main_app_dir + AP.primary_app_dir, ignore_errors=True)
        os.rename(AP.main_app_dir + AP.primary_app_backup_folder_name, AP.main_app_dir + AP.primary_app_dir)

    @staticmethod
    def ota_delete_primary_backup():
        """Delete primary app backup folder"""
        shutil.rmtree(AP.main_app_dir + AP.primary_app_backup_folder_name, ignore_errors=True)

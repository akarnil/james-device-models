"""
    Configurables for application running using main.py, and using ota_handler.py
    Change application names, directories inside the app_paths dictionary
"""
import os

class AppPaths:
    """
        Import this class where application paths are needed
        The main application needs to set main_app_dir however
        for example

        from common.app_paths import AppPaths as AP
        AP.main_app_dir = os.path.dirname(__file__)
    """
    app_name = "telemetry_sample.py"
    primary_app_dir = "/primary/"
    secondary_app_dir = "/secondary/"
    tarball_download_dir = "/.temp_ota/"
    tarball_extract_dir = "/.temp_extracted/"
    main_app_dir = None
    primary_backup_extension = ".backup"
    module_name = app_name.replace(".py","")
    primary_app_backup_folder_name = primary_app_dir.rstrip("/") + primary_backup_extension

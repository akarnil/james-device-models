"""
    Configurables for application running using main.py, and using ota_handler.py
    Change application names, directories inside the app_paths dictionary
"""
import os

app_paths: dict = {
    "app_name": "telemetry_sample.py",
    "primary_app_dir": "/primary/",
    "secondary_app_dir": "/secondary/",
    "tarball_download_dir": "/.temp_ota/",
    "tarball_extract_dir": "/.temp_extracted/",
    "main_dir": os.path.dirname(__file__),
    "primary_backup_extension": ".backup",
}
app_paths["module_name"] = app_paths["app_name"].replace(".py","")
app_paths["primary_app_backup_folder_name"] = app_paths["primary_app_dir"].rstrip("/") + app_paths["primary_backup_extension"]

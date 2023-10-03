"""Module for application launcher providing A/B seamless update functionality"""
#!/usr/bin/python3
import os
import sys
from importlib import import_module, reload

from app_paths import app_paths

# this the runner of the demo, used to show A/B updates
# the actual code lives inside a folder called `primary_app_dir`
# should it fail, an attempt will be made to run the previous code in `secondary_app_dir`

# this sample can perform OTA updates, requirements of the OTA payload
# OTA payload must be a single file of file extension .tar.gz
# the updated application .py file  must be called the same
#  as a previous version otherwise it will not load, refer to app_name

def run_app(to_run_path: str):
    """Runs .py application via path, removes from path when exception occurs"""
    try:
        print("Running app on "+ to_run_path)
        module_path: str = to_run_path.replace(app_paths["app_name"],"")
        sys.path.append(module_path)
        module = import_module(app_paths["module_name"])
        reload(module)
        module.main()
    except Exception as ex:
        sys.path.remove(module_path)
        print("App failed")
        print(str(ex))
        raise


if __name__ == "__main__":
    SECONDARY_EXISTS: bool = False
    secondary_path: str = app_paths["main_dir"] + app_paths["secondary_app_dir"] + app_paths["app_name"]
    if os.path.exists(secondary_path):
        SECONDARY_EXISTS = True

    PRIMARY_EXISTS: bool = False
    primary_path: str = app_paths["main_dir"] + app_paths["primary_app_dir"] + app_paths["app_name"]
    if os.path.exists(primary_path):
        PRIMARY_EXISTS = True

    if PRIMARY_EXISTS and SECONDARY_EXISTS:
        print("Primary and Secondary exist, running")
        try:
            run_app(primary_path)
        except Exception:
            print("Primary app has failed trying backup")
            run_app(secondary_path)

    elif PRIMARY_EXISTS:
        print("Only Primary exists, running")
        run_app(primary_path)

    elif SECONDARY_EXISTS:
        print("Only Secondary exists, running")
        run_app(secondary_path)

    else:
        print("No valid application exists to run")

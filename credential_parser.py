import json
from enum import Enum

from models.device_model import ConnectedDevice

path_to_json = "credentials.json"


class sdk_options_children:

    class certificate:
        name:str = "certificate"
        class children:
            key_path:str = "SSLKeyPath"
            cert_path: str = "SSLCertPath"
            root_cert_path: str = "SSLCaPath"
    
    class offline_storage:
        name:str = "offlineStorage"
        class children:
            disabled:str = "disabled"
            available_space: str = "availSpaceInMb"
            file_count: str = "fileCount"

    symmetric_primary_key: str = "devicePrimaryKey"


class k:
    unique_id:str = "duid"
    company_id:str = "cpid"
    environment:str = "env"
    auth:str = "auth"
    sdk_id:str = "sdk_id"
    device:str = "device"

class auth:
    type: str = "type"
    params: str = "params"

    class x509:
        name:str = "x509"
        class children:
            client_key:str = "client_key"
            client_cert:str = "client_cert"
            root_cert:str = "root_cert"

    class symmetric:
        name:str = "symmetric"
        class children:
            primary_key:str = "primary_key"
        

class device:
    class offline_storage:
        name:str = "offline_storage"
        class children:
            available_space:str = "available_space_MB"
            file_count:str = "file_count"

def get(json, key):
    if not isinstance(key,str):
        key = key.__name__
    if key in json:
        return json[key]
    return None

# sample stuff
#
# SdkOptions={
# 	"certificate" : { 
# #		"SSLKeyPath"  : "",    #aws=pk_devicename.pem   ||   #az=device.key
# #		"SSLCertPath" : "",    #aws=cert_devicename.crt ||   #az=device.pem
# 		"SSLCaPath"   : "./aws_cert/root-CA.pem"     #aws=root-CA.pem         ||   #az=rootCA.pem 
        
# 	},
#     "offlineStorage":{
#         "disabled": False,
# 	    "availSpaceInMb": 0.01,
# 	    "fileCount": 5,
#         #"keepalive":60
#     }
#     #"skipValidation":False,
# 	# As per your Environment(Azure or Azure EU or AWS) uncomment single URL and comment("#") rest of URLs.
#     #"discoveryUrl":"https://eudiscovery.iotconnect.io", #Azure EU environment 
#     #"discoveryUrl":"https://discovery.iotconnect.io", #Azure All Environment 
#     #"discoveryUrl":"http://52.204.155.38:219", #AWS pre-QA Environment
#     #"IsDebug": False
# }


def parse_json_for_config(path_to_json) -> dict:
    j = get_json_from_file(path_to_json)

    credentials["company_id"] = get(j, k.company_id)
    credentials["unique_id"] = get(j, k.unique_id)
    credentials["environment"] = get(j, k.environment)
    credentials["sdk_id"] = get(j, k.sdk_id)

    sdk_options: dict[str] = {}
    sdk_options.update(parse_auth(j))

    sdk_options.update(parse_device(j))

    credentials["sdk_options"] = sdk_options
    return credentials

def get_and_assign(from_json, to_obj , from_key, to_key):
    if (temp := get(from_json, from_key)) is not None:
            to_obj[to_key] = temp

def parse_device(j: json):
    temp: dict[str] = {}
    device_o = get(j, k.device)

    child: dict[str] = {}
    if (offline_storage_o := get(device_o, device.offline_storage.name)) is not None:
        child[sdk_options_children.offline_storage.children.disabled] = False
        get_and_assign(offline_storage_o,child, device.offline_storage.children.available_space, sdk_options_children.offline_storage.children.available_space)
        get_and_assign(offline_storage_o,child, device.offline_storage.children.file_count, sdk_options_children.offline_storage.children.file_count)
    else:
        child[sdk_options_children.offline_storage.children.disabled] = True
    temp[sdk_options_children.offline_storage.name] = child



    return temp



def parse_auth(j: json):
    temp: dict[str] = {}

    auth_o = get(j, k.auth)
    auth_type = get(auth_o, auth.type)
    params_o = get(auth_o, auth.params) # need to fetch child object for get() to work with nested enums

    if auth_type == auth.symmetric.name:
    # from jon
    #
    #     "auth": {
    #     "type": "symmetric",
    #     "params": {
    #         "primary_key": "a"
    #     }
    # },

    # to sdj
    #
    # 	"devicePrimaryKey" : "a"

        get_and_assign(params_o,temp, auth.symmetric.children.primary_key, sdk_options_children.symmetric_primary_key)
        
    elif auth_type == auth.x509.name:
    # from json
    
    #     "auth": {
    #     "type": "x509",
    #     "params": {
    #         "client_key": "a",
    #         "client_cert": "b",
    #         "root_cert": "c"
    #     }
    # },

    # to sdk
    #
    # 	"certificate" : { 
    # 		"SSLKeyPath"  : "a",
    # 		"SSLCertPath" : "b",
    # 		"SSLCaPath"   : "c"    
    # 	},

        child: dict[str] = {}
        get_and_assign(params_o,child, auth.x509.children.client_key, sdk_options_children.certificate.children.key_path)
        get_and_assign(params_o,child, auth.x509.children.client_cert, sdk_options_children.certificate.children.cert_path)
        get_and_assign(params_o,child, auth.x509.children.root_cert, sdk_options_children.certificate.children.root_cert_path)
        temp[sdk_options_children.certificate.name] = child
        

    return temp



credentials: dict = {
    "company_id": None,
    "unique_id": None,
    "environment": None,
    "sdk_id": None,
    "sdk_options": dict[str]
}

def get_json_from_file(path):
    j: json = None
    with open(path, "r") as f:
        f_contents = f.read()
        j = json.loads(f_contents)
    return j

if __name__ == "__main__":
    parse_json_for_config(path_to_json)

    



# sample stuff
#       
# """
# * sdkOptions is optional. Mandatory for "certificate" X.509 device authentication type
# * "certificate" : It indicated to define the path of the certificate file. Mandatory for X.509/SSL device CA signed or self-signed authentication type only.
# * 	- SSLKeyPath: your device key
# * 	- SSLCertPath: your device certificate
# * 	- SSLCaPath : Root CA certificate
# * 	- Windows + Linux OS: Use "/" forward slash (Example: Windows: "E:/folder1/folder2/certificate", Linux: "/home/folder1/folder2/certificate")
# * "offlineStorage" : Define the configuration related to the offline data storage 
# * 	- disabled : false = offline data storing, true = not storing offline data 
# * 	- availSpaceInMb : Define the file size of offline data which should be in (MB)
# * 	- fileCount : Number of files need to create for offline data
# * "devicePrimaryKey" : It is optional parameter. Mandatory for the Symmetric Key Authentication support only. It gets from the IoTConnect UI portal "Device -> Select device -> info(Tab) -> Connection Info -> Device Connection".
#     - - "devicePrimaryKey": "<<your Key>>"
# * Note: sdkOptions is optional but mandatory for SSL/x509 device authentication type only. Define proper setting or leave it NULL. If you not provide the offline storage it will set the default settings as per defined above. It may harm your device by storing the large data. Once memory get full may chance to stop the execution.
# """



import json
from enum import Enum

from models.device_model import ConnectedDevice

path_to_json = "credentials.json"

# Enum overrides
def enum__str__(self):
        return str(self.value)
Enum.__str__ = enum__str__

def enum__getattr__(self, item):
    if item != '_value_':
        return getattr(self.value, item)
    raise AttributeError
Enum.__getattr__ = enum__getattr__

def tV(enum: Enum) -> str:
    return enum.value


class sdk_options_children(Enum):

    class certificate(Enum):
        name:str = "certificate"
        class children(Enum):
            key_path:str = "SSLKeyPath"
            cert_path: str = "SSLCertPath"
            root_cert_path: str = "SSLCaPath"
    
    class offline_storage(Enum):
        name:str = "offlineStorage"
        class children(Enum):
            disabled:str = "disabled"
            space_megabytes: str = "availSpaceInMb"
            file_count: str = "fileCount"

    symmetric_primary_key: str = "devicePrimaryKey"


class k(Enum):
    unique_id:str = "duid"
    company_id:str = "cpid"
    environment:str = "env"
    auth:str = "auth"
    sdk_id:str = "sdk_id"

class auth(Enum):
    type: str = "type"
    params: str = "params"

    class x509(Enum):
        name: str = "x509"
        class children(Enum):
            client_key:str = "client_key"
            client_cert:str = "client_cert"

    class symmetric(Enum):
        name: str = "symmetric"
        class children(Enum):
            primary_key:str = "primary_key"
        

def get(json, key: Enum):
    if key.value in json:
        return json[key.value]
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

    credentials["sdk_options"] = sdk_options


    return credentials


def parse_auth(j: json):
    temp: dict[str] = {}

    auth_o = get(j, k.auth)
    auth_type = get(auth_o, auth.type)
    params_o = get(auth_o, auth.params) # need to fetch child object for get() to work with nested enums

    if auth_type == auth.symmetric.name:
        primary_key = get(params_o, auth.symmetric.children.primary_key)

        temp[sdk_options_children.symmetric_primary_key.value] = primary_key
        
    elif auth_type == auth.x509.name:
        client_key = get(params_o, auth.x509.children.client_key)
        client_cert = get(params_o, auth.x509.children.client_cert)
        

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



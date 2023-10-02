import json
from enum import Enum
path_to_json = "/home/akarnil/Documents/Work/james-device-models/credentials.json"

# unique_id = "afkPythonDemo"
# sdk_id = "Yjg5MmMzNThlMzc1NGNjMzg4NDEzMmUyNzFlMjYxNTE=UDI6MDM6NzAuMTQ="
# company_id = 'avtds'
# environment = 'avnetpoc'
# sdk_options = {
#     "devicePrimaryKey":"aHSkrFGVo3ezFoQLfUx7zQ=="
# }

# this function and the assignment below allows python to have nested enums, this is nice to model the auth types
def enum__getattr__(self, item):
    if item != '_value_':
        return getattr(self.value, item)
    raise AttributeError
Enum.__getattr__ = enum__getattr__

def tV(enum: Enum) -> str:
    return enum.value


class k(Enum):
    device_id:str = "duid"
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

def parse_auth(j: json):
    auth_o = get(j, k.auth)
    auth_type = get(auth_o, auth.type)
    params_o = get(auth_o, auth.params) # need to fetch child object for get() to work with nested enums

    if auth_type == auth.symmetric.name:
        primary_key = get(params_o, auth.symmetric.children.primary_key)
        pass

    if auth_type == auth.x509.name:
        client_key = get(params_o, auth.x509.children.client_key)
        client_cert = get(params_o, auth.x509.children.client_cert)
        pass
    

if __name__ == "__main__":

    # the minimum
    device_id: str = None
    company_id: str = None
    environment: str = None
    auth_type: str = None
    sdk_id: str = None

    j: json = None
    with open(path_to_json, "r") as f:
        f_contents = f.read()
        j = json.loads(f_contents)

    device_id = get(j, k.device_id)
    company_id = get(j, k.company_id)
    environment = get(j, k.environment)
    sdk_id = get(j, k.sdk_id)

    parse_auth(j)
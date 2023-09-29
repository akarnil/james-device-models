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


class k(str,Enum):
    device_id = "duid"
    company_id = "cpid"
    environment = "env"
    auth_type = "auth_type"
    auth_fields = "auth_fields"
    sdk_id = "sdk_id"



class auth_types(Enum):
    x509 = "x509"
    symmetric = "symmetric"

class at_symmetric(str,Enum):
    primary_key = "primary_key"

class at_x509(str,Enum):
    client_key = "client_key"
    client_cert = "client_cert"

at2m = {
    auth_types.x509.value : at_x509,
    auth_types.symmetric.value : at_symmetric,
}


def get(json, key):
    if key in json:
        return json[key]
    return None

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
    auth_type = get(j, k.auth_type)
    sdk_id = get(j, k.sdk_id)

    auth_fields: json = get(j, k.auth_fields)

    if auth_type == auth_types.symmetric.name:
        primary_key = get(auth_fields, at2m[auth_type].primary_key)
        pass

    if auth_type == auth_types.x509.name:
        client_key = get(auth_fields, at2m[auth_type].client_key)
        client_cert = get(auth_fields, at2m[auth_type].client_cert)
        pass
    
    print(device_id)
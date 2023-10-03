"""Load a device json file from path and translate to format required for the SDK"""
import json


class SdkOptions:
    """Human readable Enum for to mapping SDK's sdkOptions format"""
    class Certificate:
        name:str = "certificate"
        class Children:
            key_path:str = "SSLKeyPath"
            cert_path: str = "SSLCertPath"
            root_cert_path: str = "SSLCaPath"
    
    class OfflineStorage:
        name:str = "offlineStorage"
        class Children:
            disabled:str = "disabled"
            available_space: str = "availSpaceInMb"
            file_count: str = "fileCount"

    symmetric_primary_key: str = "devicePrimaryKey"


class Keys:
    """Human readable Enum for to mapping credential's json format"""
    unique_id:str = "duid"
    company_id:str = "cpid"
    environment:str = "env"
    auth:str = "auth"
    sdk_id:str = "sdk_id"
    device:str = "device"
    message_version:str = "message_version"

class Auth:
    """Human readable Enum for to mapping credential's auth object json format, including subclasses"""
    type: str = "type"
    params: str = "params"

    class X509:
        name:str = "x509"
        class Children:
            client_key:str = "client_key"
            client_cert:str = "client_cert"
            root_cert:str = "root_cert"

    class Symmetric:
        name:str = "symmetric"
        class Children:
            primary_key:str = "primary_key"
        

class Device:
    """Human readable Enum for to mapping credential's device object json format, including subclasses"""
    class OfflineStorage:
        name:str = "offline_storage"
        class Children:
            available_space:str = "available_space_MB"
            file_count:str = "file_count"

    class Attributes:
        """Human readable Enum for to mapping credential's attributes objects json format, including subclasses"""
        name:str = "attributes"
        class Children:
            name:str = "name"
            private_data:str = "private_data"
            data_type:str = "data_type"
            default_value:str = "default_value"

def get(j: json, key):
    """Get value from key, return None if it doesn't exist"""
    if not isinstance(key,str):
        key = key.__name__
    if key in j:
        return j[key]
    return None

def parse_json_for_config(path_to_json) -> dict:
    """Create and return credentials dictionary with values from json"""
    j = get_json_from_file(path_to_json)

    c: dict = {}
    c["message_version"] = get(j, Keys.message_version)
    c["company_id"] = get(j, Keys.company_id)
    c["unique_id"] = get(j, Keys.unique_id)
    c["environment"] = get(j, Keys.environment)
    c["sdk_id"] = get(j, Keys.sdk_id)

    c["sdk_options"] = get_sdk_options(j)
    c["attributes"] = parse_device_attributes(j)

    return c

def get_and_assign(from_json, to_obj , from_key, to_key):
    """Get value from json, and assign to object in format needed for the SDK"""
    if (temp := get(from_json, from_key)) is not None:
        to_obj[to_key] = temp


def get_sdk_options(j:json):
    sdk_options: dict[str] = {}
    sdk_options.update(parse_auth(j))
    sdk_options.update(parse_device_offline_storage(j))
    return sdk_options


def parse_device_offline_storage(j:json):
    '''Parse offline_storage parameters'''
    device_o = get(j, Keys.device)

    ret_o: dict[str] = {}
    child_o: dict[str] = {}
    if (offline_storage_o := get(device_o, Device.OfflineStorage.name)) is not None:
        child_o[SdkOptions.OfflineStorage.Children.disabled] = False
        get_and_assign(offline_storage_o,child_o, Device.OfflineStorage.Children.available_space, SdkOptions.OfflineStorage.Children.available_space)
        get_and_assign(offline_storage_o,child_o, Device.OfflineStorage.Children.file_count, SdkOptions.OfflineStorage.Children.file_count)
    else:
        child_o[SdkOptions.OfflineStorage.Children.disabled] = True
    ret_o[SdkOptions.OfflineStorage.name] = child_o

    return ret_o

def parse_device_attributes(j:json):
    '''Parse device attributes parameters'''
    device_o = get(j, Keys.device)

    all_attributes = []
    if (attributes := get(device_o, Device.Attributes.name)) is not None:
        for attribute in attributes:
            a = {}
            a[Device.Attributes.Children.name] = get(attribute, Device.Attributes.Children.name)
            a[Device.Attributes.Children.data_type] = get(attribute, Device.Attributes.Children.data_type)
            a[Device.Attributes.Children.default_value] = get(attribute, Device.Attributes.Children.default_value)
            a[Device.Attributes.Children.private_data] = get(attribute, Device.Attributes.Children.private_data)
            all_attributes.append(a)

    return all_attributes

def parse_auth(j: json):
    """Parse auth object from credential json, generate format needed for SDK"""
    temp: dict[str] = {}

    auth_o = get(j, Keys.auth)
    params_o = get(auth_o, Auth.params)

    auth_type = get(auth_o, Auth.type)
    if auth_type == Auth.Symmetric.name:
        get_and_assign(params_o,temp, Auth.Symmetric.Children.primary_key, SdkOptions.symmetric_primary_key)

    elif auth_type == Auth.X509.name:
        child: dict[str] = {}
        get_and_assign(params_o,child, Auth.X509.Children.client_key, SdkOptions.Certificate.Children.key_path)
        get_and_assign(params_o,child, Auth.X509.Children.client_cert, SdkOptions.Certificate.Children.cert_path)
        get_and_assign(params_o,child, Auth.X509.Children.root_cert, SdkOptions.Certificate.Children.root_cert_path)
        temp[SdkOptions.Certificate.name] = child


    return temp

def get_json_from_file(path):
    """Load Json from file and return json object"""
    j: json = None
    with open(path, "r", encoding="utf-8") as file:
        f_contents = file.read()
        j = json.loads(f_contents)
    return j

if __name__ == "__main__":
    PATH_TO_JSON = "credentials.json"
    print(parse_json_for_config(PATH_TO_JSON))

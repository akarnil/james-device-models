"""Load a device json file from path and translate to format required for the SDK"""
import json
from enum import Enum, auto

class ToSDK:
    '''
        Class of Enums that are related to the SDK side 
    '''
    class Credentials(Enum):
        """
            Enum for credentials object to be passed to application
            Used to build and access the dictionary object
        """
        sdk_ver = auto()
        company_id = auto()
        unique_id = auto()
        environment = auto()
        sdk_id = auto()
        sdk_options = auto()
        attributes = auto()

    class Attributes(Enum):
        name = auto()
        private_data = auto()
        data_type = auto()
        default_value = auto()

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

class FromJSON:
    '''
        Class of Enums that are related to the JSON config side
    '''
    class Keys:
        """Human readable Enum for to mapping credential's json format"""
        unique_id:str = "duid"
        company_id:str = "cpid"
        environment:str = "env"
        auth:str = "auth"
        sdk_id:str = "sdk_id"
        device:str = "device"
        sdk_ver:str = "sdk_ver"

    class Auth:
        """Human readable Enum for to mapping credential's auth object json format, including subclasses"""
        type: str = "auth_type"
        params: str = "params"

        class X509:
            name:str = "IOTC_AT_X509"
            class Children:
                client_key:str = "client_key"
                client_cert:str = "client_cert"
                root_cert:str = "root_cert"

        class Symmetric:
            name:str = "IOTC_AT_SYMMETRIC_KEY"
            class Children:
                primary_key:str = "primary_key"

        class Token:
            name:str = "IOTC_AT_TOKEN"

        class TPM:
            name:str = "IOTC_AT_TPM"

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
    c[ToSDK.Credentials.sdk_ver] = float(get(j, FromJSON.Keys.sdk_ver)) # Convert string to float
    c[ToSDK.Credentials.company_id] = get(j, FromJSON.Keys.company_id)
    c[ToSDK.Credentials.unique_id] = get(j, FromJSON.Keys.unique_id)
    c[ToSDK.Credentials.environment] = get(j, FromJSON.Keys.environment)
    c[ToSDK.Credentials.sdk_id] = get(j, FromJSON.Keys.sdk_id)

    c[ToSDK.Credentials.sdk_options] = get_sdk_options(j)
    c[ToSDK.Credentials.attributes] = parse_device_attributes(j)

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
    device_o = get(j, FromJSON.Keys.device)

    ret_o: dict[str] = {}
    child_o: dict[str] = {}
    if (offline_storage_o := get(device_o, FromJSON.Device.OfflineStorage.name)) is not None:
        child_o[ToSDK.SdkOptions.OfflineStorage.Children.disabled] = False
        get_and_assign(offline_storage_o,child_o, FromJSON.Device.OfflineStorage.Children.available_space, ToSDK.SdkOptions.OfflineStorage.Children.available_space)
        get_and_assign(offline_storage_o,child_o, FromJSON.Device.OfflineStorage.Children.file_count, ToSDK.SdkOptions.OfflineStorage.Children.file_count)
    else:
        child_o[ToSDK.SdkOptions.OfflineStorage.Children.disabled] = True
    ret_o[ToSDK.SdkOptions.OfflineStorage.name] = child_o

    return ret_o

def parse_device_attributes(j:json):
    '''Parse device attributes parameters'''
    device_o = get(j, FromJSON.Keys.device)

    all_attributes = []
    if (attributes := get(device_o, FromJSON.Device.Attributes.name)) is not None:
        for attribute in attributes:
            a = {}
            a[ToSDK.Attributes.name] = get(attribute, FromJSON.Device.Attributes.Children.name)
            a[ToSDK.Attributes.data_type] = get(attribute, FromJSON.Device.Attributes.Children.data_type)
            a[ToSDK.Attributes.default_value] = get(attribute, FromJSON.Device.Attributes.Children.default_value)
            a[ToSDK.Attributes.private_data] = get(attribute, FromJSON.Device.Attributes.Children.private_data)
            all_attributes.append(a)

    return all_attributes

def parse_auth(j: json):
    """Parse auth object from credential json, generate format needed for SDK"""
    temp: dict[str] = {}

    auth_o = get(j, FromJSON.Keys.auth)
    params_o = get(auth_o, FromJSON.Auth.params)

    auth_type = get(auth_o, FromJSON.Auth.type)

    if auth_type == FromJSON.Auth.Symmetric.name:
        get_and_assign(params_o,temp, FromJSON.Auth.Symmetric.Children.primary_key, ToSDK.SdkOptions.symmetric_primary_key)

    elif auth_type == FromJSON.Auth.X509.name:
        child: dict[str] = {}
        get_and_assign(params_o,child, FromJSON.Auth.X509.Children.client_key, ToSDK.SdkOptions.Certificate.Children.key_path)
        get_and_assign(params_o,child, FromJSON.Auth.X509.Children.client_cert, ToSDK.SdkOptions.Certificate.Children.cert_path)
        get_and_assign(params_o,child, FromJSON.Auth.X509.Children.root_cert, ToSDK.SdkOptions.Certificate.Children.root_cert_path)
        temp[ToSDK.SdkOptions.Certificate.name] = child

    elif auth_type == FromJSON.Auth.Token.name:
        raise NotImplementedError()

    elif auth_type == FromJSON.Auth.TPM.name:
        raise NotImplementedError()

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

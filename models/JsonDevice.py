#from models.device_model import *
from models.device_model import ConnectedDevice

from common.JsonParser import parse_json_for_config, ToSDK




class DynAttr:
    name = None
    path = None
    default = None
    data_type = None

    def __init__(self, name, path, default=None, data_type=None):
        self.name = name
        self.path = path
        self.data_type = data_type
        self.default = self.convert_type(default)

    def get_value(self):
        val = self.default
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                val = f.read()
                val = self.convert_type(val)
        except FileNotFoundError:
            print("File not found at " + self.path)
            raise

        return val
    
    def convert_type(self, val):
        '''
        datatypes in 2.1
        1: "INT",
        2:"LONG",
        3:"FLOAT",
        4:"STRING",
        5:"Time",
        6:"Date",
        7:"DateTime",
        8:"BIT",
        9:"Boolean",
        10:"LatLong",
        11:"OBJECT"
        '''

        if self.data_type == "int":
            return int(val)
        
        if self.data_type == "str":
            return str(val)
        
        return None

class JsonDevice(ConnectedDevice):
    attributes: DynAttr = []
    # attributes is a list of attributes brought in from json
    # the DynAttr class holds the metadata only, e.g. where the value is saved as a file - the attribute itself is set on the class
    # in the override of the super get_state()

    def __init__(self, conf_file):
        parsed_json: dict = parse_json_for_config(conf_file)

        for attr in parsed_json[ToSDK.Credentials.attributes]:
            m_att = DynAttr(attr[ToSDK.Attributes.name],attr[ToSDK.Attributes.private_data],attr[ToSDK.Attributes.default_value],attr[ToSDK.Attributes.data_type])
            setattr(self, attr[ToSDK.Attributes.name], attr[ToSDK.Attributes.default_value])
            self.attributes.append(m_att)

        super().__init__(
            parsed_json[ToSDK.Credentials.company_id],
            parsed_json[ToSDK.Credentials.unique_id],
            parsed_json[ToSDK.Credentials.environment],
            parsed_json[ToSDK.Credentials.sdk_id],
            parsed_json[ToSDK.Credentials.sdk_options]
        )

    def get_state(self):
        '''Do not override'''
        data_obj = {}
        data_obj.update(self.get_attributes_state())
        data_obj.update(self.get_local_state())
        return data_obj
    
    def get_attributes_state(self) -> dict:
        '''Gets all attributes specified from the JSON file'''
        data_obj = {}
        attr: DynAttr
        for attr in self.attributes:
            setattr(self, attr.name, attr.get_value())
            data_obj[attr.name] = getattr(self, attr.name)
        return data_obj
    
    def get_local_state(self) -> dict:
        '''Overrideable - return dictionary of local data to send to the cloud'''
        print("no class-defined object properties")
        return {}


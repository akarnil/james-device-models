#from models.device_model import *
from models.device_model import ConnectedDevice

from common.JsonParser import parse_json_for_config, ToSDK
from iotconnect.common.data_evaluation import DATATYPE

from enum import Enum

class DynAttr:

    class ReadTypes(Enum):
        ascii:str = "ascii"
        binary:str = "binary"

    class SendDataTypes(Enum):
        INT = DATATYPE["INT"]
        LONG = DATATYPE["LONG"]
        FLOAT = DATATYPE["FLOAT"]
        STRING = DATATYPE["STRING"]
        Time = DATATYPE["Time"]
        Date = DATATYPE["Date"]
        DateTime = DATATYPE["DateTime"]
        BIT = DATATYPE["BIT"]
        Boolean = DATATYPE["Boolean"]
        LatLong = DATATYPE["LatLong"]
        OBJECT = DATATYPE["OBJECT"]


    name = None
    path = None
    read_type = None

    def __init__(self, name, path,data_type):
        self.name = name
        self.path = path
        self.data_type = data_type

    def get_raw_value(self):
        val = None

        data_type = self.ReadTypes(self.data_type)
        if data_type == self.ReadTypes.ascii:
            with open(self.path, "r", encoding="utf-8") as f:
                val = f.read()

        if data_type == self.ReadTypes.binary:
            with open(self.path, "br") as f:
                val = f.read()

        return val

    
    def convert_type(self, val, to_type):
        to_type = self.SendDataTypes(to_type)

        if to_type == self.SendDataTypes.INT:
            return int(val)
        
        if to_type == self.SendDataTypes.STRING:
            return str(val)
        
        if to_type == self.SendDataTypes.Boolean:
            return bool(val)
        
        return None

class JsonDevice(ConnectedDevice):
    attributes: DynAttr = []
    # attributes is a list of attributes brought in from json
    # the DynAttr class holds the metadata only, e.g. where the value is saved as a file - the attribute itself is set on the class
    # in the override of the super get_state()

    def __init__(self, conf_file):
        parsed_json: dict = parse_json_for_config(conf_file)

        # Construct DynAttrs from json 
        for attr in parsed_json[ToSDK.Credentials.attributes]:
            m_att = DynAttr(attr[ToSDK.Attributes.name],attr[ToSDK.Attributes.private_data],attr[ToSDK.Attributes.private_data_type])
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
            for ca in self.cloud_attributes:
                if attr.name == ca['ln']:
                    raw_val = attr.get_raw_value()
                    data_obj[attr.name] = attr.convert_type(raw_val,ca['dt'])
                    break

        return data_obj
    
    def get_local_state(self) -> dict:
        '''Overrideable - return dictionary of local data to send to the cloud'''
        print("no class-defined object properties")
        return {}


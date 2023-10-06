#from models.device_model import *
from models.device_model import ConnectedDevice

from common.JsonParser import parse_json_for_config, ToSDK
from iotconnect.common.data_evaluation import DATATYPE
import struct

from enum import Enum

class DynAttr:

    class ReadTypes(Enum):
        ascii = "ascii"
        binary = "binary"

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

    def __init__(self, name, path,read_type):
        self.name = name
        self.path = path
        self.read_type = self.ReadTypes(read_type)

    def update_value(self):
        val = None
        try:
            if self.read_type == self.ReadTypes.ascii:
                with open(self.path, "r", encoding="utf-8") as f:
                    val = f.read()

            if self.read_type == self.ReadTypes.binary:
                with open(self.path, "rb") as f:
                    val = f.read()

        except FileNotFoundError:
            print("File not found at", self.path)
        return val

    def get_value(self,to_type):
        val = self.update_value()
        val = self.convert(val,to_type)
        return val
    
    def convert(self,val,to):
        to_type = self.SendDataTypes(to)

        if self.read_type == self.ReadTypes.binary:
            if to_type in [self.SendDataTypes.INT, self.SendDataTypes.LONG]:
                return int.from_bytes(val, 'big')
            
            elif to_type in [self.SendDataTypes.FLOAT]:
                return (struct.unpack('f', val)[0])
            
            elif to_type in [self.SendDataTypes.STRING]:
                return val.decode("utf-8")
            
            elif to_type in [self.SendDataTypes.Boolean]:
                return struct.unpack('?', val)[0]
            
            elif to_type in [self.SendDataTypes.BIT]:
                if struct.unpack('?', val)[0]:
                    return 1
                return 0

        if self.read_type == self.ReadTypes.ascii:
            try:
                if to_type in [self.SendDataTypes.INT, self.SendDataTypes.LONG]:
                    return int(float(val))
                elif to_type in [self.SendDataTypes.FLOAT]:
                    return float(val)
                elif to_type in [self.SendDataTypes.STRING]:
                    return str(val)
                elif to_type in [self.SendDataTypes.BIT]:
                    if self.convert(val, self.SendDataTypes.INT) != 0:
                        return 1
                    return 0
                elif to_type in [self.SendDataTypes.Boolean]:
                    if type(val) == bool:
                        return val
                    elif type(val) == int:
                        return val != 0
                    elif type(val) == str:
                        if val in ["False", "false", "0", ""]:
                            return False
                        return True
            except Exception as e:
                print(e)


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
        attribute: DynAttr
        for attribute in self.attributes:
            for metadata in self.attribute_metadata:
                if attribute.name == metadata[self.MetadataKeys.name]:
                    data_obj[attribute.name] = attribute.get_value(metadata[self.MetadataKeys.data_type])
                    break

        return data_obj
    
    def get_local_state(self) -> dict:
        '''Overrideable - return dictionary of local data to send to the cloud'''
        #print("no class-defined object properties")
        return {}


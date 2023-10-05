'''
    Converting from iotconnect SDK's dictionary types to a more useful enum
    Benefit of it is that we can rename the enums to a more verbose and user friendly standard
'''
from enum import Enum
from typing import Union # to use Union[Enum, None] type hint

from iotconnect.IoTConnectSDK import MSGTYPE,ErorCode,CMDTYPE,OPTION,DATATYPE


class Enums:

    class Keys(Enum):
        ack:str = 'ack'
        command_type:str = 'ct'
        id:str = 'id'
        device_command:str = 'cmd'

    class Values:
        # 2.1 enums
        class AckStat(Enum):
            FAIL = 4
            EXECUTED = 5
            SUCCESS = 7
            EXECUTED_ACK = 6 # what is the difference between this and EXECUTED??
            
        class OtaStat(Enum):
            SUCCESS = 0
            FAILED = 1
            DL_IN_PROGRESS = 2
            DL_DONE = 3
            DL_FAILED = 4

        class MessageType(Enum):
            RPT = MSGTYPE["RPT"]
            FLT = MSGTYPE["FLT"]
            RPTEDGE = MSGTYPE["RPTEDGE"]
            RMEdge = MSGTYPE["RMEdge"]
            LOG = MSGTYPE["LOG"]
            ACK = MSGTYPE["ACK"]
            OTA = MSGTYPE["OTA"]
            FIRMWARE = MSGTYPE["FIRMWARE"]

        class ErrorCode(Enum):
            OK = ErorCode["OK"]
            DEV_NOT_REG = ErorCode["DEV_NOT_REG"]
            AUTO_REG = ErorCode["AUTO_REG"]
            DEV_NOT_FOUND = ErorCode["DEV_NOT_FOUND"]
            DEV_INACTIVE = ErorCode["DEV_INACTIVE"]
            OBJ_MOVED = ErorCode["OBJ_MOVED"]
            CPID_NOT_FOUND = ErorCode["CPID_NOT_FOUND"]

        class Commands(Enum):
            DEVICE_COMMAND = CMDTYPE["DCOMM"]
            FIRMWARE = CMDTYPE["FIRMWARE"]
            MODULE = CMDTYPE["MODULE"]
            U_ATTRIBUTE = CMDTYPE["U_ATTRIBUTE"]
            U_SETTING = CMDTYPE["U_SETTING"]
            U_RULE = CMDTYPE["U_RULE"]
            U_DEVICE = CMDTYPE["U_DEVICE"]
            DATA_FRQ = CMDTYPE["DATA_FRQ"]
            U_barred = CMDTYPE["U_barred"]
            D_Disabled = CMDTYPE["D_Disabled"]
            D_Released = CMDTYPE["D_Released"]
            STOP = CMDTYPE["STOP"]
            Start_Hr_beat = CMDTYPE["Start_Hr_beat"]
            Stop_Hr_beat = CMDTYPE["Stop_Hr_beat"]
            INIT_CONNECT = CMDTYPE["is_connect"]
            SYNC = CMDTYPE["SYNC"]
            RESETPWD = CMDTYPE["RESETPWD"]
            UCART = CMDTYPE["UCART"]

        class Option(Enum):
            attribute = OPTION["attribute"]
            setting = OPTION["setting"]
            protocol = OPTION["protocol"]
            device = OPTION["device"]
            sdkConfig = OPTION["sdkConfig"]
            rule = OPTION["rule"]

        class DataType(Enum):
            INT = list(DATATYPE.values()).index("INT")
            LONG = list(DATATYPE.values()).index("LONG")
            FLOAT = list(DATATYPE.values()).index("FLOAT")
            STRING = list(DATATYPE.values()).index("STRING")
            Time = list(DATATYPE.values()).index("Time")
            Date = list(DATATYPE.values()).index("Date")
            DateTime = list(DATATYPE.values()).index("DateTime")
            BIT = list(DATATYPE.values()).index("BIT")
            Boolean = list(DATATYPE.values()).index("Boolean")
            LatLong = list(DATATYPE.values()).index("LatLong")
            OBJECT = list(DATATYPE.values()).index("OBJECT")

    @classmethod
    def enums_from_keys(cls, key : Keys) -> Union[Enum, None]:
        if key == cls.Keys.command_type:
            return cls.Values.Commands
        
        return None

    @classmethod
    def get_value_using_key(cls,msg, key: Enum) -> Union[str, None]:
        key = key.value
        if (key in msg):
            return msg[key]
        return None


    @classmethod
    def get_enum_using_key(cls, msg, key: Keys) -> Union[Enum, None]:
        '''
            Checks if the value got from the message using the key is valid
            if so then returns the associated Enum object with the value.
            Returns None if not.
        '''
        if (value := cls.get_value_using_key(msg,key)) is not None:
            if (all_enums := cls.enums_from_keys(key)) is not None:
                a_e: Enum
                for a_e in all_enums:
                    if value == a_e.value:
                        return a_e
            print("not valid " + key.name + " does not have associated enum of value " + str(value))
        return None

    @classmethod
    def key_in_msg(cls, msg, key: Keys) -> bool:
        return (key.value in msg)
    
    @classmethod
    def get_command_type(cls, msg) -> Union[Enum, None]:
        return cls.get_enum_using_key(msg, cls.Keys.command_type) 
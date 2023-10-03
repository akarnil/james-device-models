from enum import Enum
from typing import Union # to use Union[Enum, None] type hint



class Enums:

    class Keys(str, Enum):
        ack = 'ack'
        command_type = 'ct'
        id = 'id'
        device_command = 'cmd'

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
            DL_FAILED= 4

        class MessageType(Enum):
            RPT = 0
            FLT = 1
            RPTEDGE = 2
            RMEdge = 3
            LOG = 4
            ACK = 5
            OTA = 6
            FIRMWARE = 11

        class ErrorCode(Enum):
            OK = 0
            DEV_NOT_REG = 1
            AUTO_REG = 2
            DEV_NOT_FOUND = 3
            DEV_INACTIVE = 4
            OBJ_MOVED = 5
            CPID_NOT_FOUND = 6

        class Commands(Enum):
            DCOMM = 0
            FIRMWARE = 1
            MODULE = 2
            U_ATTRIBUTE = 101
            U_SETTING = 102
            U_RULE = 103
            U_DEVICE = 104
            DATA_FRQ = 105
            U_barred = 106
            D_Disabled = 107
            D_Released = 108
            STOP = 109
            Start_Hr_beat = 110
            Stop_Hr_beat = 111
            is_connect = 116
            SYNC = "sync"
            RESETPWD = "resetpwd"
            UCART = "updatecrt"

        class Option(Enum):
            attribute = "att"
            setting = "set"
            protocol = "p"
            device = "d"
            sdkConfig = "sc"
            rule = "r"

        class DataType(Enum):
            INT = 1
            LONG = 2
            FLOAT = 3
            STRING = 4
            Time = 5
            Date = 6
            DateTime = 7
            BIT = 8
            Boolean = 9
            LatLong = 10
            OBJECT = 11

    @classmethod
    def enums_from_keys(cls, key : Keys) -> Union[Enum, None]:
        if key == cls.Keys.command_type:
            return cls.Values.Commands
        
        return None

    @classmethod
    def get_value_using_key(cls,msg, key) -> Union[str, None]:
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
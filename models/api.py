class api21:
    from enum import Enum

    # 2.1 enums
    class AckStat(Enum):
        FAIL = 4,
        EXECUTED = 5,
        SUCCESS = 7,
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

    class Keys(str, Enum):
        ack = 'ack'
        command_type = 'ct'
        id = 'id'

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
    def get_value_from_key(self, msg, key):
        ret = None
        if key in msg:
            if msg[key] in self.Commands._value2member_map_:
                ret = self.Commands(msg[key])
        return ret
    
    @classmethod
    def get_command_type(self, msg):
        return self.get_value_from_key(msg, self.Keys.command_type) 
from enum import Enum

# 2.1 enums
class ackCmdStatus(Enum):
    FAIL = 4,
    EXECUTED = 5,
    SUCCESS = 7,
    EXECUTED_ACK = 6 # what is the difference between this and EXECUTED??




if 10 in ackCmdStatus._value2member_map_:
    pass
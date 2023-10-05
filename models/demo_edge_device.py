from enum import Enum
import sys
from common.enums import Enums as e
from models.JsonDevice import JsonDevice
sys.path.append("iotconnect")
from typing import Union # to use Union[Enum, None] type hint


def whoami():
    import sys
    return sys._getframe(1).f_code.co_name


class DemoEdgeDevice(JsonDevice):
    class DeviceCommands(Enum):
        ECHO:str = "echo "
        LED:str = "led "
        TEST:str = "test_command"

    def device_cb(self,msg):
        print("device callback received")

        # check command type got from message
        if (command_type := e.get_command_type(msg)) is not None:
            if command_type == e.Values.Commands.DEVICE_COMMAND:
                # do something cool here
                self.device_command(msg)

            if command_type == e.Values.Commands.INIT_CONNECT:
                print("connection status is " + msg["command"])

            else:
                print(whoami() + " got sent command_type     " + command_type.name)
            return

        print("callback received not valid")
        print("rule command",msg)

    def get_device_command(self, full_command:str) -> Union[Enum, None]:
        command_enum = None
        if full_command is not None:
            for dc in [dc.value for dc in self.DeviceCommands]:
                if (sliced := full_command[:len(dc)]) == dc:
                    command_enum = self.DeviceCommands(sliced)
                    break
        return command_enum

    def device_command(self, msg):
        full_command = e.get_value_using_key(msg, e.Keys.device_command)
        command_enum = self.get_device_command(full_command)

        if command_enum == self.DeviceCommands.ECHO:
            to_print = full_command[len(self.DeviceCommands.ECHO.value):]
            print(to_print)
            self.send_ack(msg,e.Values.AckStat.SUCCESS, "Command Executed Successfully")

        if command_enum == self.DeviceCommands.TEST:
            self.send_ack(msg,e.Values.AckStat.SUCCESS, "Command Executed Successfully")


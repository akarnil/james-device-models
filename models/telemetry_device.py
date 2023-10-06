from enum import Enum
import sys
from common.Enums import Enums as E
from models.JsonDevice import JsonDevice
sys.path.append("iotconnect")
from typing import Union # to use Union[Enum, None] type hint


def whoami():
    import sys
    return sys._getframe(1).f_code.co_name


class TelemetryDevice(JsonDevice):
    class DeviceCommands(Enum):
        ECHO = "echo "
        LED = "led "
        TEST = "test_command"

    def device_cb(self,msg):
        print("device callback received")

        # check command type got from message
        if (command_type := E.get_value(msg, E.Keys.command_type)) is not None:
            if command_type == E.Values.Commands.DEVICE_COMMAND:
                # do something cool here
                self.device_command(msg)

            if command_type == E.Values.Commands.INIT_CONNECT:
                print("connection status is " + msg["command"])

            else:
                print(whoami() + " got sent command_type     " + int(command_type))
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
        full_command = E.get_value(msg, E.Keys.device_command)
        command_enum = self.get_device_command(full_command)

        if command_enum == self.DeviceCommands.ECHO:
            to_print = full_command[len(self.DeviceCommands.ECHO.value):]
            print(to_print)
            self.send_ack(msg,E.Values.AckStat.SUCCESS, "Command Executed Successfully")

        if command_enum == self.DeviceCommands.TEST:
            self.send_ack(msg,E.Values.AckStat.SUCCESS, "Command Executed Successfully")


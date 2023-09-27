from models.device_model import *

cpid = '<<your Settings > Key Vault > CPID here>>'
env = '<<your Settings > Key Vault > Environment here>>'
uniqueid = "<<your Device ID>>"
SId = "<<your Settings > Key Vault > Language=\"Python **\" > Version = "1.0" > Identity here>>"

sdk_options = {
    "devicePrimaryKey": "<<your Device > Connection Info > Device Connection > PrimaryKey here>>"
}

m_device = ConnectedDevice(cpid, uniqueid, env, SId, sdk_options=sdk_options)

m_device.connect()

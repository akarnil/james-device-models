Example `.json` that uses offline storage and symmetric key authentication 
```json
{
    "message_version": 2.1,
    "duid": "afkPythonDemo",
    "cpid": "avtds",
    "env": "avnetpoc",
    "sdk_id": "XXX",
    "auth": {
        "type": "symmetric",
        "params": {
            "primary_key": "XXX"
        }
    },
    "device": {
        "offline_storage": {
            "available_space_MB" : 1,
            "file_count" : 1 
        },
        "name": "maaxboardt",
        "commands":[
            {
                "name":"led",
                "private_data": "/sys/class/leds/usr_led/brightness"
            }
        ]           
    }
}
```
* `"message_version": "<>"` The message version of the SDK used currently only `2.1` supported

* `"duid": "<>"` The device's unique id

* `"cpid": "<>"` The company id

* `"env": "<>"` The environment it uses

* `"sdk_id": "<>",` identity key of the SDK

* Authentication object, inside this object, place all of the parameters required based on your authentication type,

    Symmetric Key Authentication
    ```json
        "auth": {
            "auth_type": "symmetric",
            "params": {
                "primary_key": "XXX"
            }
        },
    ```

    X509 Certificate Authentication
    ```json
        "auth": {
            "auth_type": "x509",
            "params": {
                "client_key": "Path to key",
                "client_cert": "Path to cert",
                "root_cert": "Path to Root CA"
            }
        },
    ```


* Device configurables live inside the `"device"` object, inside the object different children objects are used to configure device specific parameters

    Offline Storage, omitting this object in your configuration disables offline storage support
    ```json
        "offline_storage": {
            "available_space_MB" : 1,
            "file_count" : 1 
        },
    ```

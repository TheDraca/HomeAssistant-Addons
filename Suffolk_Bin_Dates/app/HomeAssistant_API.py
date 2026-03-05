import os
import requests
import json
from datetime import datetime, timezone

HA_Server="http://supervisor/core/api"
HA_Supervisor_Token=os.getenv('SUPERVISOR_TOKEN')

def UpdateSensor(HA_Domain,HA_SensorName,HA_SensorFriendlyName,Data,unit=None,
    device_class=None):
    FullSensorName=HA_Domain + "_" + HA_SensorName
    response=requests.post(
        "{0}/states/sensor.{1}".format(HA_Server,FullSensorName),
        headers={
            "Authorization": "Bearer {0}".format(HA_Supervisor_Token),
            "content-type": "application/json",
        },
        data=json.dumps({
            "state": str(Data),
            "attributes": {
                "friendly_name": HA_SensorFriendlyName,
                "last_update": datetime.now(timezone.utc).isoformat()
            }
        }),
    )

    if unit:
        attributes["unit_of_measurement"] = unit
    if device_class:
        attributes["device_class"] = device_class

    return response

def ReadSensor(HA_Domain,HA_SensorName):
    FullSensorName=HA_Domain + "_" + HA_SensorName
    response=requests.get(
        "{0}/states/sensor.{1}".format(HA_Server,FullSensorName),
        headers={
            "Authorization": "Bearer {0}".format(HA_Supervisor_Token),
            "content-type": "application/json",
        }
    )

    return response

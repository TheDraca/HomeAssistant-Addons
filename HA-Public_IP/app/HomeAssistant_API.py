import os
import requests
import json

HA_Server="http://supervisor/core/api"
HA_Supervisor_Token=os.getenv('SUPERVISOR_TOKEN')

def UpdateSensor(HA_Domain,HA_SensorName,HA_SensorFriendlyName,Data):
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
                "friendly_name": HA_SensorFriendlyName
            }
        }),
    )

    return response
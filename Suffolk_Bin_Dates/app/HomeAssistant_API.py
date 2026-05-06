import os
import requests
import json
from datetime import datetime, timezone

HA_Server="http://supervisor/core/api"
HA_Supervisor_Token=os.getenv('SUPERVISOR_TOKEN')

def UpdateState(HA_Domain, HA_SensorName, HA_SensorFriendlyName, Data, extra_attributes=None, HA_StateDomain="sensor"):
    FullSensorName=HA_Domain + "_" + HA_SensorName
    attributes = {
                "friendly_name": HA_SensorFriendlyName,
                "last_update": datetime.now(timezone.utc).isoformat()
                }

    if extra_attributes:
        attributes.update(extra_attributes)

    response=requests.post(
        "{0}/states/{1}.{2}".format(HA_Server,HA_StateDomain,FullSensorName),
        headers={
            "Authorization": "Bearer {0}".format(HA_Supervisor_Token),
            "content-type": "application/json",
        },
        data=json.dumps(
            {
                "state": str(Data),
                "attributes": attributes
            }
        )
    )
    return response

def ReadState(HA_Domain,HA_SensorName,HA_StateDomain="sensor"):
    FullSensorName=HA_Domain + "_" + HA_SensorName
    response=requests.get(
        "{0}/states/{1}.{2}".format(HA_Server,HA_StateDomain,FullSensorName),
        headers={
            "Authorization": "Bearer {0}".format(HA_Supervisor_Token),
            "content-type": "application/json",
        }
    )

    return response

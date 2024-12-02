
import json
import time
import requests
import logging
import HomeAssistant_API

#Load HA options from config.yaml / user edited from the web UI
with open("/data/options.json","r") as options:
    HA_Options=json.load(options)


#Set debug level to debug if the UI says so, else we're on INFO
if HA_Options["Debug"]:
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
else:
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')



#Announce we've loaded the PY script
logging.info("Starting HA_Public-IP")

#Log what options have been loaded if debug is enabled
logging.debug("Loaded options from Docker's config.ymal, contents looks like:")
logging.debug(HA_Options)

#Read the Refresh Time provided to us by HA config, X60 to make it minutes
TimeToSleep=int(HA_Options["Refresh time"])*60


#Main Loop
while True:
    APIResponse=requests.get("https://api.ipify.org?format=json")

    if int(APIResponse.status_code) == 200:
        PublicIP = json.loads(APIResponse.text) #Json of public api in format {"ip":"1.2.3.4"}
        PublicIP = PublicIP["ip"] # Just the IP part of the IP
        
        logging.info("New IP detected, updating sensor")
        HA_API_Response=HomeAssistant_API.UpdateSensor("ha_public_ip","ip","Public IP Address",PublicIP)

        logging.debug(HA_API_Response.status_code)
        logging.debug(HA_API_Response.text)
    else:
        logging.warning("Non-200 status code from ipify")
        logging.warning(APIResponse.status_code)
        logging.warning(APIResponse.text)

    logging.debug("Check finished waiting %s seconds before looping",str(TimeToSleep))
    time.sleep(TimeToSleep)



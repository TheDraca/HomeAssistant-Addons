
import json
import time
import requests
import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from random import randint
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
logging.info("Starting Suffolk_Bin_Dates")

#Log what options have been loaded if debug is enabled
logging.debug("Loaded options from Docker's config.ymal, contents looks like:")
logging.debug(HA_Options)

def GetTimeToSleep():
    #Read the Refresh Time provided to us by HA config
    TimeToSleep=int(HA_Options["Refresh time"])

    #Read Time variation provided to us in HA config
    TimeToSleepVariation=int(HA_Options["Time variation"])

    #Override the variation with a random number
    TimeToSleepVariation=int(randint(0,TimeToSleepVariation))

    #X60 these added together as sleep is in seconds
    return (TimeToSleep + TimeToSleepVariation)*60


#Function to do the scraping
def GetBins(LocationCookie):
    logging.info("Scraping website...")

    # Define the cookies
    cookies = {
        "atLocation": LocationCookie
    }

    #Custom headers - no officer this is not a scraper
    headers = {
        "User-Agent": HA_Options["User Agent"]
    }


    url = "https://maps.westsuffolk.gov.uk"

    response=requests.get(url, cookies=cookies, headers=headers)

    logging.debug("HTTP response code: %s",response.status_code)
    response_content = response.text.split("\n")

    #logging.debug("\nHTTP response content: %s \n\n",response_content)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with class 'atPanelData'
    panel_data_elements = soup.find_all('div', class_='atPanelData')


    if panel_data_elements:
        for panel_data in panel_data_elements:
            # Extract the text content of the div - while also stripping out crap
            panel_text = panel_data.get_text(separator=' ').replace('\n', '').replace('\r', '')

            # Strip this of extra white space and all extra spaces, tabs newlines, returns, etc.
            panel_text = " ".join(panel_text.split())
            
            # Replace all the double spaces with single spaces
            panel_text = re.sub(r'\s+', ' ', panel_text)

            #Find the pannel with bin info in it
            if "bin" in panel_text.lower():
                if str(HA_Options["Brown Bin"]) == "True":
                    # Use regular expression to find matches for each bin, store that and the date
                    bin_matches = re.findall(
                        r'(Black|Blue|Brown) Bins: (.*?)(?=\bBlack|Blue|Brown|\Z)',
                        panel_text,
                        re.IGNORECASE
                    )
                else:
                    # Same as above but no brown bin :(
                    bin_matches = re.findall(
                        r'(Black|Blue) Bins: (.*?)(?=\bBlack|Blue|\Z)', 
                        panel_text,
                        re.IGNORECASE
                    )

    logging.debug("Scrapped bin_matches are: %s",str(bin_matches))

    return bin_matches


#Function to turn date retrived from website into a usable python datetime
def ParseBinDate(bin_date):
    #Set the date format to use when handling datetime objects
    format_str = "%A %d %B %Y"

    # Store todays date
    today = datetime.now()

    # Get tomorrow's date and create a datetime object for it 
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime(format_str)
    
    # The council website does not have years and python will just assume its the 1900's
    # To avoid this we'll add this year to the end of the dates unless we're currently in december and the bin dates contain January then we should add next year on the end
    if today.month == 12 and "January" in bin_date:
        year_to_add = today.year + 1
    else:
        year_to_add = today.year

    # Add the current year (or next year if we've added one) to the bin_date
    bin_date= f"{bin_date} {year_to_add}"

    # Clean the date string by removing all the suffixes
    bin_date = bin_date.replace("1st", "1").replace("2nd", "2").replace("3rd", "3").replace("th", "")

    # Convert the cleaned date string to a datetime object
    bin_date = datetime.strptime(bin_date, format_str)

    logging.debug("Converted datetime is: %s",bin_date)

    return bin_date

#Main Loop
while True:
    ##Scrape the dates, skip straight to sleeping if this fails.
    try:
        Bin_Dates=GetBins(HA_Options["Location Cookie"])
    except:
        logging.critical("ERROR Scraping website, waiting to try again later - this error will NOT resolve itself if the location cookie isn't set correctly")
        
        TimeToSleep=GetTimeToSleep()
        logging.info("Error - waiting %s minutes before looping",str(int(TimeToSleep/60)))
        time.sleep(TimeToSleep)
        break

    logging.info("Updating home assistant sensors with data")

    # Loop through the matches and update each
    for bin_name, bin_date in Bin_Dates:
        sensor_name="due_date_" + bin_name
        sensor_friendly_name="{0} Bin Due Date".format(bin_name)
        
        parsed_date = ParseBinDate(bin_date.strip())

        #Set the value to go back to HA as a time stamp for 6AM on the day of collection (6AM is when the council say bins should be out by)
        sensor_due_date = parsed_date.replace(hour=6, tzinfo=ZoneInfo("Europe/London")).isoformat()
    

        logging.debug("Determining if date for %s bin is tomorrow",bin_name)

        #Check if the date stamp we made is tomorrow's date:
        if parsed_date.date() == (datetime.now() + timedelta(days=1)).date():
            bin_due_tomorrow = "Yes"
        else:
            bin_due_tomorrow = "No"

        logging.debug("Updating sensor for %s bin with timestamp for %s",bin_name,bin_date)

        HA_API_Response=HomeAssistant_API.UpdateState("suffolk_bin_dates", sensor_name, sensor_friendly_name, sensor_due_date, extra_attributes={
        "being collected tomorrow": bin_due_tomorrow,
        "device_class": "timestamp"
        })

        logging.debug(HA_API_Response.status_code)
        logging.debug(HA_API_Response.text)
    
    TimeToSleep=GetTimeToSleep()

    logging.info("Check finished waiting %s minutes before looping",str(int(TimeToSleep/60)))
    time.sleep(TimeToSleep)


import json
import time
import requests
import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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

#Read the Refresh Time provided to us by HA config, X60 to make it minutes
TimeToSleep=int(HA_Options["Refresh time"])*60



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


    url = "https://maps.westsuffolk.gov.uk/MyWestSuffolk.aspx"

    response=requests.get(url, cookies=cookies, headers=headers)

    #print(response.status_code)
    response_content = response.text.split("\n")

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
            if "bin" in panel_text:
                if str(HA_Options["Brown Bin"]) == "True":
                    # Use regular expression to find matches for each bin, store that and the date
                    bin_matches = re.findall(r'(Black|Blue|Brown) bin: (.*?)(?=\bBlack|Blue|Brown|\Z)', panel_text)
                else:
                    # Same as above but no brown bin :(
                    bin_matches = re.findall(r'(Black|Blue) bin: (.*?)(?=\bBlack|Blue|\Z)', panel_text)

    logging.debug("Scrapped bin_matches are: %s",str(bin_matches))

    return bin_matches


#Function to decide if a bin is due tomorrow or not
def BinIsTomorrow(bin_date):
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

    if bin_date.strftime(format_str) == tomorrow_date:
        logging.debug("BinIsTomorrow returning True")
        return True
    else:
        logging.debug("BinIsTomorrow returning False")
        return False


#Main Loop
while True:
    ##Scrape the dates, skip straight to sleeping if this fails.
    try:
        Bin_Dates=GetBins(HA_Options["Location Cookie"])
    except:
        logging.CRITICAL("ERROR Scraping website, waiting to try again later - this error will NOT resolve itself if the location cookie isn't set correctly")
        
        time.sleep(TimeToSleep)
        break

    logging.info("Updating home assistant sensors with data")

    # Loop through the matches and update each
    for bin_name, bin_date in Bin_Dates:
        sensor_name="due_date_" + bin_name
        sensor_friendly_name="{0} Bin Due Date".format(bin_name)
        sensor_due_date=bin_date.strip()

        logging.debug("Updating sensor for %s bin",bin_name)

        HA_API_Response=HomeAssistant_API.UpdateSensor("suffolk_bin_dates",sensor_name,sensor_friendly_name,bin_date)

        logging.debug(HA_API_Response.status_code)
        logging.debug(HA_API_Response.text)



        logging.debug("Determining if date for %s bin is tomorrow",bin_name)
        
        if BinIsTomorrow(bin_date):
            bin_due_tomorrow="true"
        else:
            bin_due_tomorrow="false"

        logging.debug("Updating sensor for %s bin due tomorrow",bin_name)

        sensor_name="due_tomorrow_" + bin_name
        sensor_friendly_name="{0} Bin Due Tomorrow".format(bin_name)

        HA_API_Response=HomeAssistant_API.UpdateSensor("suffolk_bin_dates",sensor_name,sensor_friendly_name,bin_due_tomorrow)

        logging.debug(HA_API_Response.status_code)
        logging.debug(HA_API_Response.text)

    logging.info("Check finished waiting %s seconds before looping",str(TimeToSleep))
    time.sleep(TimeToSleep)

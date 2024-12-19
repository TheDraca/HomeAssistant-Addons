<b> Scrape your bin dates from the Suffolk (UK) council website </b>

This is a **scraper** and doesn't use an API, be careful with the refresh time.
Also be aware it could break at anytime and as stated on this repo's readme **updates will come as an when... if at all**

<small>Also if the Suffolk County Council some how comes across this... Please bring find my nearest out of 2002 and give it an API too <3 (I promise if I find out there's an API I'll update this with it <3)</small>

[GitHub Page](https://github.com/TheDraca/HomeAssistant-Addons/tree/main/Suffolk_Bin_Dates)

## Required step: Getting your location cookie ##
Before running the add-on for the first time set the "Location Cookie" in the configuration tab, to do this go to [Find my nearest](https://maps.westsuffolk.gov.uk/) and enter your address in the box.

You'll then need to get the "atLocation" cookie that is now stored in your browser, for FireFox simply right click anywhere on the page and click "Inspect"

In the menu that appears on the left had side select "Cookies" then the adjacent table should show atLocation, copy that value and paste it into home assistant.

<b>BE AWARE: This contains your address and it will be available in home assistant, vet my C-tier code before running it and don't blindly paste this</b>

## Entities provided by this addon ##

Three entities will be created
- "Blue Bin Due Date" (sensor.suffolk_bin_dates_due_blue)
- "Black Bin Due Date" (sensor.suffolk_bin_dates_due_black)
- "Blue Bin Due Tomorrow" (sensor.suffolk_bin_dates_due_tomorrow_blue)
- "Black Bin Due Tomorrow" (sensor.suffolk_bin_dates_due_tomorrow_black)

These entities will also bee created if you enable Brown Bin
- "Brown Bin Due Date" (sensor.suffolk_bin_dates_due_brown)
- "Brown Bin Due Tomorrow" (sensor.suffolk_bin_dates_due_tomorrow_brown)

Due tomorrow entities are always either "true" or "false", if you wish to setup a reminder to notify you to put the bin out you'd do so as follows:
- Trigger: Fixed time of your choosing
- And if: Entity --> State: sensor.suffolk_bin_dates_due_tomorrow_blue == true
- Then do: send notification





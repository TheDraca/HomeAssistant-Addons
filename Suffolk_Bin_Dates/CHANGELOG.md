## 1.1.03
### **Breaking change**: Sensor names and attributes have been renamed to use "collection" rather than due date - check readme for new domains

## 1.1.02
- Add icons for bin sensor, with a diffrent icon for when the bin is due tomorrow

## 1.1.01
- Remove unused extra variables from UpdateState that are now expected in extra_attributes 

## 1.1.00
 ### **Breaking change**: Due tomorrow sensors have been removed in favour of "Being collected tomorrow" attribute within each bin due date update your automations
- Fix attributes not being included in post request
- Moved all attributes to a single extra_attributes variable to send to HomeAssistant_API
- Send due dates back as date timestamp class to HA
- Update HomeAssistant_API to send back more than just sensors
- Remove due_tomorrow sensors - return "being collected tomorrow" attribute instead
- Update README with correct sensor due date names + updated instructions for bin notifications with new attribute

## 1.0.07
- Update url to scrape + fix regex for new wording on site + lowercase a debugging call

## 1.0.06
- Update build_from to new FROM ghcr.io/home-assistant/base:latest

## 1.0.05
- Add some extra debug logging

## 1.0.04
- Provide last_update in UpdateSensor and unit/device_class if provided

## 1.0.03

- Fix time sleeping in logs being provided in seconds not minutes

## 1.0.02

- Add random time variation for scraping

## 1.0.01

- Sleep for configured time instead of crashing on failed scrape

## 1.0.00

- Initial release

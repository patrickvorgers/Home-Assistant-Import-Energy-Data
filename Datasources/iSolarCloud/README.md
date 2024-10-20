# Energy provider: iSolarCloud

iSolarCloud offers the option to export data from the [iSolarCloud](https://www.isolarcloud.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Solar production - High resolution (day interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```


**How-to**
- Export data from the [iSolarCloud](https://www.isolarcloud.com/) site
  - Go to the [iSolarCloud](https://www.isolarcloud.com/) site
  - Login with your account
  - Select plant
  - Scroll down to statistics section (default is day) and select month
  - Click export and select csv
  - Repear this for each month you want to export
  - The data for each selected month is downloaded to your PC as a separate file
- Download the ```iSolarCloudaPrepare.py``` file and put it in the same directory as the iSolarCloud data
- Execute the python script with as parameter the name of the directory which contains the files with the exported data ```python iSolarCloudDataPrepare.py *.csv```. The python script creates the needed file for the generic import script.
- Follow the steps in the overall how-to
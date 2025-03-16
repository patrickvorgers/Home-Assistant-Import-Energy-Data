# Energy provider: Solarman

Solarman offers the option to export data from the [Solarman](https://www.solarmanpv.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Solar production - High resolution (day interval) - kWh
- Battery charge - High resolution (day interval) - kWh
- Battery discharge - High resolution (day interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```
- OpenPyXL python library ```pip install openpyxl```


**How-to**
- Export data from the [Solarman](https://www.solarmanpv.com/) site
  - Go to the [Solarman](https://www.solarmanpv.com/) site
  - Login with your account (Press `SOLARMAN Login` and select `SOLARMAN Smart`)
  - Export the data
- Download the ```SolarmanPrepare.py``` file and put it in the same directory as the Solarman data
- Execute the python script with as parameter the name of the directory which contains the files with the exported data ```python SolarmanDataPrepare.py *.xlsx```. The python script creates the needed file for the generic import script.
- Follow the steps in the overall how-to
# Energy provider: NEM12

NEM12 is a standard for Australian smart meter data, it allows users to export their electricity consumption data, which can be processed and imported into Home Assistant.
This implementation is based on the NEM12 standard, which is used by many Australian energy providers.
It does not fully implement the NEM12 standard, but it tries to extract the data from the NEM12 records.
This implementation is under development and may not work for all NEM12 files.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```

**How-to**
- Export your electricity consumption data in the NEM12 format.
- Download the ```NEM12DataPrepare.py``` script and place it in the same directory as the exported NEM12 data.
- Execute the Python script by providing the name of the exported file as a parameter. Example:  
  ```python NEM12DataPrepare.py power-redacted.csv```.  
  The script will generate the necessary files for importing the data into Home Assistant.
- Follow the steps in the overall Home Assistant import guide for integrating the data into your setup.
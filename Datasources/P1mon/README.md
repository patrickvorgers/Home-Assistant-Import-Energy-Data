# Energy provider: P1Mon (ZTATZ)

P1Mon offers the option to export data from the local database. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 2 - High resolution (hour interval) - kWh
- Gas consumption - High resolution (hour interval) - m³
- Water consumption - High resolution (hour interval) - m³

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```
- OpenPyXL python library ```pip install openpyxl```

**How-to**
- Export data from P1Mon.
    - Go to P1Mon's local IP address or URL. 
    - Go to ```configuation and Settings``` and login with the password
    - Select the 'in-export' tab
    - Select 'Excel Export' and choose 'e_historie.db'
    - The data will now be downloaded to your PC
    - Optionally: Consolidate the minute interval data into hourly data. (Having minute data significantly reduces performance)
- Download the ```P1MonDataPrepare.py``` and/or ```P1MonWaterDataPrepare.py``` file and put it in the same directory as the P1Mon data
- Execute the python script with as parameter the name of the file that contains the exported data ```python P1MonDataPrepare.py e_historie.db.xlsx```. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to

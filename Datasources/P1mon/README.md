# Energy provider: P1Mon (ZTATZ)

P1Mon offers the option to export data from the `settings > in-export` menu. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (day interval) - kWh
- Gas consumption - High resolution (day interval) - m³ (not tested)
- Water consumption - high resulution (day interval) - m³

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```
- OpenPyXL python library ```pip install openpyxl```

**How-to**
- Export data from P1Mon.
    - Go to P1Mon's local IP address or URL. 
    - Go to `configuation and Settings` and login with the password
    - Select the 'in-export' tab
    - On to bottom right select 'Verbruiksgegevens'
    - Fill in the start and end date and press 'Download'
    - The data is now downloaded to your PC
- Download the ```EnecoDataPrepare.py``` file and put it in the same directory as the Eneco data
- Execute the python script with as parameter the name of the file that contains the exported data ```python EnecoPrepare.py Verbruik_01-01-2020-31-12-2020.xlsx```. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to

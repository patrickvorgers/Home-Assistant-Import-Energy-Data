# Energy provider: Zonneplan

Zonneplan does not directly provide the possibility to export data. Data can be requested by sending an email to Zonneplan. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh
- Gas consumption - High resolution (hour interval) - m³

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```
- OpenPyXL python library ```pip install openpyxl```

**How-to**
- Request the data from [Zonneplan](https://www.zonneplan.nl/)
  - Go to the [Zonneplan](https://www.zonneplan.nl/) site
  - Click on `Service`
  - Request via the chatbot to be connected with an employee
  - Request from the employee the data
- Download the ```ZonneplanDataPrepare.py``` file and put it in the same directory as the Zonneplan data
- Execute the python script with as parameter the name of the file that contains the exported data ```python ZonneplanDataPrepare.py export-2025-01-21.11_17_12.xlsx```.
  The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to

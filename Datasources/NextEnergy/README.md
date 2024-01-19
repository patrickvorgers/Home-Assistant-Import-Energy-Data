# Energy provider: NextEnergy

NextEnergy doesn't offer the option to export data from their website or mobile app, but it is possible to request data via customer service. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh
- Gas consumption - High resolution (hour interval) - m³

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```
- OpenPyXL python library ```pip install openpyxl```

**How-to**
- Request data from NextEnergy customer service
- Download the ```NextEnergyDataPrepare.py``` file and put it in the same directory as the NextEnergy data
- Execute the python script with as parameter the name of the file that contains the exported data ```python NextEnergyDataPrepare.py "Measurements 19-01-2024 accesspointId 99999.xlsx"```. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
# Energy provider: Ameren Electric

Ameren Electric offers the option to export data from the [Ameren Electric](https://www.ameren.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**
- Export data from the [Ameren Electric](https://www.ameren.com/) site
- Download the `AmerenElectricDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded Ameren Electric data
- Execute the python script with as parameter the name of the file that contains the exported data `python AmerenElectricDataPrepare.py ACE_Electric_72621898_03_30_2024_03_30_2025.csv`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
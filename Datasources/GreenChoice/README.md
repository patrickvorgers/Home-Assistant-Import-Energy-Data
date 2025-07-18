# Energy provider: GreenChoice

Greenchoice offers the option to export data from the [GreenChoice](https://www.greenchoice.nl/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (day interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**
- Export data from the [GreenChoice](https://www.greenchoice.nl/) site
- Download the `GreenChoiceDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded GreenChoice data
- Execute the python script with as parameter the name of the file that contains the exported data `python GreenChoiceDataPrepare.py meterstanden_stroom_2023.csv`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
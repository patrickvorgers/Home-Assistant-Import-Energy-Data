# Energy provider: HomeWizard

HomeWizard offers the option to export data from Energy+. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (15 min interval) - kWh
- Electricity consumption - Tariff 1 - Low resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (15 min interval) - kWh
- Electricity consumption - Tariff 2 - Low resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (15 min interval) - kWh
- Electricity production - Tariff 1 - Low resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (15 min interval) - kWh
- Electricity production - Tariff 2 - Low resolution (day interval) - kWh
- Gas consumption - High resolution (15 min interval) - m³
- Gas consumption - Low resolution (day interval) - m³
- Water consumption - High resolution (15 min interval) - m³
- Water consumption - Low resolution (day interval) - m³

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Go to the [HomeWizard](https://helpdesk.homewizard.com/en/articles/6664029-how-to-export-and-use-csv-files) site and follow the help to export the data
- Download the `HomeWizardDataPrepare.py` and/or `HomeWizardGasDataPrepare.py` and/or `HomeWizardWaterDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the HomeWizard data
- Execute the python script with as parameter the name of the file that contains the exported data `python HomeWizardDataPrepare.py homewizard_2022-09_15min_elec.csv`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
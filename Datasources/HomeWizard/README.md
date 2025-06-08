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

The site mentions that also gas and water consumption data can be exported,
but this is not added to the script yet, because sample data is not available.
Anyone who has this data and is willing to share it, please contact me.

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Go to the [HomeWizard](https://helpdesk.homewizard.com/en/articles/6664029-how-to-export-and-use-csv-files) site and follow the help to export the data
- Download the `HomeWizardDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded HomeWizard data
- Execute the python script with as parameter the name of the file that contains the exported data `python HomeWizardDataPrepare.py homewizard_2022-09_15min_elec.csv`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
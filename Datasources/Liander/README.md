# Energy provider: Liander

Liander doesn't offer the option to export data from their site or mobile app, but it is possible to request data via customer service. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (day interval) - kWh
- Gas consumption - High resolution (day interval) - m³

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Request data from Liander customer service
- Download the `LianderDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Liander data
- Execute the python script with as parameter the name of the file that contains the exported data `python LianderDataPrepare.py csv_bijlage.csv`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
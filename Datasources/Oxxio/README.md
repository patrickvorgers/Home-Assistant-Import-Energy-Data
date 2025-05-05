# Energy provider: Oxxio

Oxxio offers the option to export data from the [Mijn Oxxio](https://inloggen.oxxio.nl/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (day interval) - kWh
- Gas consumption - High resolution (day interval) - m³

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- OpenPyXL python library `pip install openpyxl`

**How-to**
- Export data from the [Mijn Oxxio](https://inloggen.oxxio.nl/) site
- Download the `OxxioDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Oxxio data
- Execute the python script with as parameter the name of the file that contains the exported data `python OxxioPrepare.py Oxxio.Verbruik_05-06-2023-22-01-2024.xlsx`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
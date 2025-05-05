# Energy provider: Eneco

Eneco offers the option to export data from the [Mijn Eneco](https://inloggen.eneco.nl/) site. This data can be transformed and used to import into Home Assistant.

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
- Export data from the [Mijn Eneco](https://inloggen.eneco.nl/) site
  - Go to the [Mijn Eneco](https://inloggen.eneco.nl/) site
  - Login with your account
  - Select the 'Verbruik' tab
  - On to bottom right select 'Verbruiksgegevens'
  - Fill in the start and end date and press 'Download'
  - The data is now downloaded to your PC
- Download the `EnecoDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Eneco data
- Execute the python script with as parameter the name of the file that contains the exported data `python EnecoPrepare.py Verbruik_01-01-2020-31-12-2020.xlsx`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
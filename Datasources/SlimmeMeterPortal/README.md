# Energy provider: Slimme Meter Portal

The SlimmeMeterPortal offers the option to export data from the SlimmeMeterPortal site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (15 min interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (15 min interval) - kWh
- Electricity production - Tariff 1 - High resolution (15 min interval) - kWh
- Electricity production - Tariff 2 - High resolution (15 min interval) - kWh
- Gas consumption - High resolution (hour interval) - m³

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```
- OpenPyXL python library ```pip install openpyxl```

**How-to**
- Export data from the [Slimme Meter Portal](https://www.slimmemeterportal.nl/) site
  - Go to the [Slimme Meter Portal](https://www.slimmemeterportal.nl/) site
  - Click on `Inloggen`
  - Provide `E-mailadres` and `Wachtwoord` and click on `INLOGGEN`
  - Hover over `PlusAccount` and select `Detaildata Downloaden`
  - Repeat the below steps for all the needed meters and years
      - Select the meter and year and click on `BESTAND OPVRAGEN`
      - Download the generated file
- Download the ```SlimmeMeterPortalDataPrepare.py``` and/or ```SlimmeMeterPortalGasDataPrepare.py``` file and put it in the same directory as the P1Mon data
- Execute the python script with as parameter the name of the file that contains the exported data ```python SlimmeMeterPortalDataPrepare.py data_20??_871687120058657526.xlsx```.
  The python script creates the needed files for the generic import script.
  To import data for multiple years, use `?` or `*` in the filename to match multiple files.
- Follow the steps in the overall how-to

# Energy provider: VanOns

VanOns offers the option to export data from the [VanOns](https://mijn.vanons.org/overview) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (day interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```

**How-to**
- Export data from the [VanOns](https://mijn.vanons.org/overview) site
- Download the ```VanOnsDataPrepare.py``` file and put it in the same directory as the downloaded VanOns data
- Execute the python script with as parameter the name of the file that contains the exported data ```python VanOnsDataPrepare.py meterstanden_stroom_2023.csv```. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to

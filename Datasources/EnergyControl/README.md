# Energy provider: EnergyControl

[EnergyControl](https://www.steige-solutions.de/energy-control/) offers the option to import various types of data, such as water, solar, energy and more. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 2 - High resolution (day interval) - kWh
- Gas consumption - High resolution (day interval) - m³
- Water consumption - High resolution (day interval) - m³

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Export data from the [EnergyControl](https://www.steige-solutions.de/energy-control/) app.
- Download the `EnergyControlDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and place it in the same directory as the exported EnergyControl data.
- Execute the Python script with the exported data file as a parameter:  `python EnergyControlDataPrepare.py data_file.csv`. The python script creates the needed file for the generic import script.
- Follow the steps in the overall how-to

# Energy provider: Shelly EM3

The Shelly EM3 device offers the option to export history data by accessing the Web UI of the device. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - Wh
- Electricity production - Tariff 1 - High resolution (hour interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Open the Shelly EM3 Web UI by entering the device's IP address in your browser.
- Navigate to `Consumption Chart` and find the `Consumption` or `Energy Consumption` section.
- If necessary, expand the chart to full screen to view the entire data range. 
- Look for an `Export` or `Download` option and select it to save the data as a CSV file. 
- Download the `ShellyEM3DataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded Shelly EM3 data.
- Execute the python script with as parameter the name of the file that contains the exported data `python ShellyEM3DataPrepare.py -p phaseA em_data_phaseA.csv`. The python script creates the needed files for the generic import script. Repeat this step for the other phases.
- Follow the steps in the overall how-to.
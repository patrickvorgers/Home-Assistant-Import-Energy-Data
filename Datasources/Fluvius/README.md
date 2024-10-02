# Energy provider: Fluvis

Fluvius offers the option to export data from the [Mijn Fluvius](https://mijn.fluvius.be/) site. This data can be transformed and used to import into Home Assistant.

It is recommended to create a quarter hourly (15 minute) export request so you can export the quarter hourly totals.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (15 minute interval) - kWh (Metered version)
- Electricity consumption - Tariff 2 - High resolution (15 minute interval) - kWh (Metered version)
- Electricity production - Tariff 1 - High resolution (15 minute interval) - kWh (Metered version)
- Electricity production - Tariff 2 - High resolution (15 minute interval) - kWh (Metered version)
- Gas consumption - High resolution (hour interval) - m³ or kWh (Metered version)

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```

**How-to**

To be able to download quarter hourly CSVs, you need to make a request to be able to download them.

You might also need to enable the P1 port to activate quarter hourly reports on https://mijn.fluvius.be/poortbeheer/

You need to do this only once for each meter.

- Setup the quarter hourly reports (only once per meter)
  - Go to https://mijn.fluvius.be/verbruik/aanvragen 
  - Select the meter and continue to the next page
  - Select "Kwartier" or "Alle" - this allows you to be able to download quarter hourly data and continue to the next page
  - Select "Alle verbruiken vanaf ..." and continue to the next page
  - Confirm the request (you will receive an email to approve the request)

- Export data from the [Mijn Fluvius](https://mijn.fluvius.be/) site
  - Go to https://mijn.fluvius.be/verbruik/
  - For the meter, click *Details* and *Verbruik*, then *Rapport downloaden* and select *kwartiertotalen*.
  - Select the time frame and press *Download*
  - Do the same thing for your Gas Meter if you have one and download it in the same directory
  - Download the ```FluviusDataPrepare.py``` file and put it in the same directory as the Enphase data
  - Execute the python script with as parameter the name of the file that contains the exported data ```python FluviusDataPrepare.py "Verbruiks*.csv"```. The python script creates the needed files for the generic import script.
  - Follow the steps in the overall how-to